import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="Aggressive Options Scaler", page_icon="⚡", layout="wide")

st.title("⚡ Aggressive Options Compounding Engine")
st.write("This model accommodates high-yield premium strategies, tracking the exponential curve up to a 20% monthly target.")

st.divider()

# --- FILE PATHS FOR PERSISTENT TRACKING ---
MONTH_DATA_FILE = "pnl_data.csv"
WEEK_DATA_FILE = "weekly_pnl_data.csv"
TRACKER_MONTHS = 36  # Fixed 3-year horizon

# --- GENERATE CALENDAR MONTH NAMES DYNAMICALLY ---
# Start from the current month/year and look forward 36 months
start_date = datetime.now()
CALENDAR_MONTHS = [(start_date + relativedelta(months=i)).strftime("%B %Y") for i in range(TRACKER_MONTHS)]

# --- GLOBAL SIDEBAR INPUTS ---
st.sidebar.header("🕹️ Growth Levers")
starting_capital = st.sidebar.number_input("Starting Capital ($)", min_value=0.0, value=30000.0, step=1000.0)
target_goal = st.sidebar.number_input("Ultimate Goal Target ($)", min_value=0.0, value=1000000.0, step=50000.0)

st.sidebar.subheader("📈 Trading Strategy")
monthly_yield = st.sidebar.slider("Target Monthly Return (%)", min_value=1.0, max_value=20.0, value=20.0, step=0.5,
                                  help="Warning: Higher monthly percentages dramatically increase assignment and tail risk.")

st.sidebar.subheader("💵 Capital Infusion")
monthly_deposit = st.sidebar.number_input("Monthly Contribution from Income ($)", min_value=0.0, value=0.0, step=100.0,
                                         help="Fresh cash added to the portfolio each month.")

st.sidebar.subheader("🚨 Risk Management Rule")
risk_per_trade = st.sidebar.slider("Max Account Risk Per Trade (%)", min_value=0.5, max_value=20.0, value=5.0, step=0.5,
                                   help="The % of your total account value risked on any single option setup.")


# --- PERSISTENT TRACKER DATA LOADERS ---
def load_month_data():
    if os.path.exists(MONTH_DATA_FILE):
        df = pd.read_csv(MONTH_DATA_FILE)
        # Verify alignment with current calendar frame
        if len(df) == TRACKER_MONTHS and df["Month"].iloc[0] == CALENDAR_MONTHS[0]:
            return df
    return pd.DataFrame({
        "Month": CALENDAR_MONTHS,
        "Actual PnL ($)": [0.0] * TRACKER_MONTHS
    })

def load_week_data():
    if os.path.exists(WEEK_DATA_FILE):
        df = pd.read_csv(WEEK_DATA_FILE)
        if df["Month"].iloc[0] == CALENDAR_MONTHS[0]:
            return df
    
    # Initialize empty weekly matrix using calendar months
    months_col = []
    weeks_col = []
    for m_name in CALENDAR_MONTHS:
        for w in range(1, 5):
            months_col.append(m_name)
            weeks_col.append(f"Week {w}")
            
    return pd.DataFrame({
        "Month": months_col,
        "Week": weeks_col,
        "Actual PnL ($)": [0.0] * (TRACKER_MONTHS * 4)
    })

df_actual_months = load_month_data()
df_actual_weeks = load_week_data()


# --- ENGINE 1: MAIN TRAJECTORY SIMULATION (Theoretical Timeline) ---
current_balance = starting_capital
months_counter = 0
simulation_data = []

if monthly_yield == 0 and monthly_deposit == 0:
    st.error("You must have either a monthly return or a monthly deposit to grow the account!")
else:
    while current_balance < target_goal and months_counter < 240:
        trading_profit = current_balance * (monthly_yield / 100)
        max_dollar_risk_per_trade = current_balance * (risk_per_trade / 100)
        
        simulation_data.append({
            "Month Index": months_counter,
            "Portfolio Value ($)": current_balance,
            "Monthly Profit ($)": trading_profit,
            "Weekly Profit Target ($)": trading_profit / 4.33,
            "Max Risk Per Trade ($)": max_dollar_risk_per_trade
        })
        current_balance += trading_profit + monthly_deposit
        months_counter += 1

    simulation_data.append({
        "Month Index": months_counter,
        "Portfolio Value ($)": current_balance,
        "Monthly Profit ($)": current_balance * (monthly_yield / 100),
        "Weekly Profit Target ($)": (current_balance * (monthly_yield / 100)) / 4.33,
        "Max Risk Per Trade ($)": current_balance * (risk_per_trade / 100)
    })

df_sim = pd.DataFrame(simulation_data)


# --- ENGINE 2: TRACKER MATRIX CALCULATIONS ---
tracker_balances = []
tracker_pnls = []
tracker_balance_runner = starting_capital

for m in range(TRACKER_MONTHS):
    pnl_target = tracker_balance_runner * (monthly_yield / 100)
    tracker_pnls.append(round(pnl_target, 2))
    tracker_balance_runner += pnl_target + monthly_deposit
    tracker_balances.append(round(tracker_balance_runner, 2))

df_tracker = pd.DataFrame({
    "Month": CALENDAR_MONTHS,
    "Target PnL ($)": tracker_pnls,
    "Actual PnL ($)": df_actual_months["Actual PnL ($)"].astype(float),
    "Target Balance ($)": tracker_balances
})
df_tracker["Variance ($)"] = df_tracker["Actual PnL ($)"] - df_tracker["Target PnL ($)"]


# --- CREATE TABS INTERFACE ---
tab1, tab2, tab3 = st.tabs(["📊 Main Projection Dashboard", "📅 3-Year Monthly Milestones", "⏱️ Weekly Journal"])


# ==========================================
# TAB 1: PROJECTION DASHBOARD
# ==========================================
with tab1:
    st.subheader("🏁 Performance Timeline")
    
    total_actual_pnl = df_tracker["Actual PnL ($)"].sum()
    current_portfolio_value = starting_capital + total_actual_pnl
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Theoretical Time to Goal", f"{months_counter} Months", f"{(months_counter/12):.1f} Years")
    col2.metric("Live Portfolio Balance", f"${current_portfolio_value:,.2f}", 
                delta=f"${total_actual_pnl:,.2f} Total Net PnL" if total_actual_pnl != 0 else None)
    col3.metric("Target Monthly Yield", f"{monthly_yield}%")
    col4.metric("Starting Base Risk Size", f"${starting_capital * (risk_per_trade / 100):,.2f}")
    
    st.divider()
    
    st.subheader("📉 Capital Scaling Trajectory")
    fig = px.area(
        df_sim, x="Month Index", y="Portfolio Value ($)", 
        title=f"Compounding Theoretical Profile at {monthly_yield}% Per Month",
        labels={"Portfolio Value ($)": "Account Balance ($)", "Month Index": "Months Passed"}
    )
    fig.add_hline(y=target_goal, line_dash="dash", line_color="green", annotation_text="Target Goal Mark")
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    st.subheader("📋 Theoretical Position Scaling Guide")
    df_display = df_sim.copy()
    df_display["Portfolio Value ($)"] = df_display["Portfolio Value ($)"].map("${:,.2f}".format)
    df_display["Monthly Profit ($)"] = df_display["Monthly Profit ($)"].map("${:,.2f}".format)
    df_display["Weekly Profit Target ($)"] = df_display["Weekly Profit Target ($)"].map("${:,.2f}".format)
    df_display["Max Risk Per Trade ($)"] = df_display["Max Risk Per Trade ($)"].map("${:,.2f}".format)
    st.dataframe(df_display.set_index("Month Index"), use_container_width=True)


# ==========================================
# TAB 2: MONTHLY MILIESTONES
# ==========================================
with tab2:
    st.header("📅 36-Month Goal Execution Journal")
    st.write("💡 *Note: Your Actual PnL values are automatically updated when you log your weekly earnings in the next tab!*")
    
    # Format dataframe for presentation
    df_tracker_display = df_tracker.copy()
    df_tracker_display["Target PnL ($)"] = df_tracker_display["Target PnL ($)"].map("${:,.2f}".format)
    df_tracker_display["Actual PnL ($)"] = df_tracker_display["Actual PnL ($)"].map("${:,.2f}".format)
    df_tracker_display["Variance ($)"] = df_tracker_display["Variance ($)"].map("${:,.2f}".format)
    df_tracker_display["Target Balance ($)"] = df_tracker_display["Target Balance ($)"].map("${:,.2f}".format)

    st.dataframe(
        df_tracker_display,
        hide_index=True,
        use_container_width=True
    )
        
    st.divider()
    
    st.subheader("📊 Tracker Execution Path (Actuals vs Target)")
    df_tracker_chart = df_tracker.copy()
    df_tracker_chart["Actual Balance ($)"] = starting_capital + df_tracker_chart["Actual PnL ($)"].cumsum()
    
    active_entries = df_tracker_chart[df_tracker_chart["Actual PnL ($)"] != 0].index
    if len(active_entries) > 0:
        last_idx = active_entries[-1]
        df_tracker_chart.loc[last_idx + 1:, "Actual Balance ($)"] = np.nan
    else:
        df_tracker_chart["Actual Balance ($)"] = np.nan
        
    st.line_chart(df_tracker_chart.set_index("Month")[["Target Balance ($)", "Actual Balance ($)"]])


# ==========================================
# TAB 3: WEEKLY JOURNAL
# ==========================================
with tab3:
    st.header("⏱️ Weekly Tracking Engine")
    st.write("Focus completely on the current micro-cycle. Select the calendar month you are working on, enter your weekly results, and save.")
    
    # Dropdown selector displaying actual calendar months
    selected_month = st.selectbox("Select Target Month to Edit:", CALENDAR_MONTHS)
    
    # Calculate this month's proportional target per week
    target_row = df_tracker[df_tracker["Month"] == selected_month].iloc[0]
    weekly_target = round(target_row["Target PnL ($)"] / 4, 2)
    
    st.info(f"🎯 **Target Strategy for {selected_month}:** You need to average **${weekly_target:,.2f} / week** to smash this milestone.")
    
    # Filter weekly data frame
    df_filtered_weeks = df_actual_weeks[df_actual_weeks["Month"] == selected_month].copy()
    df_filtered_weeks["Target PnL ($)"] = weekly_target
    df_filtered_weeks["Variance ($)"] = df_filtered_weeks["Actual PnL ($)"] - weekly_target
    
    # Show interactive weekly data editor
    edited_weeks_df = st.data_editor(
        df_filtered_weeks[["Week", "Target PnL ($)", "Actual PnL ($)", "Variance ($)"]],
        disabled=["Week", "Target PnL ($)", "Variance ($)"],
        hide_index=True,
        use_container_width=True
    )
    
    if st.button("💾 Save Weekly Progress"):
        for index, row in edited_weeks_df.iterrows():
            week_label = row["Week"]
            actual_val = float(row["Actual PnL ($)"])
            
            match_idx = df_actual_weeks[(df_actual_weeks["Month"] == selected_month) & (df_actual_weeks["Week"] == week_label)].index
            df_actual_weeks.loc[match_idx, "Actual PnL ($)"] = actual_val
            
        # Save weekly master file
        df_actual_weeks[["Month", "Week", "Actual PnL ($)"]].to_csv(WEEK_DATA_FILE, index=False)
        
        # Aggregate to monthly master file
        rollup_df = df_actual_weeks.groupby("Month")["Actual PnL ($)"].sum().reset_index()
        
        # Build clean mapping back to order framework
        df_final_months = pd.DataFrame({"Month": CALENDAR_MONTHS})
        df_final_months = df_final_months.merge(rollup_df, on="Month", how="left").fillna(0.0)
        
        df_final_months[["Month", "Actual PnL ($)"]].to_csv(MONTH_DATA_FILE, index=False)
        
        st.success(f"Weekly journal saved! rolled up total into {selected_month} dashboard profile.")
        st.rerun()
