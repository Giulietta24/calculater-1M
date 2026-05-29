import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

st.set_page_config(page_title="Aggressive Options Scaler", page_icon="⚡", layout="wide")

st.title("⚡ Aggressive Options Compounding Engine")
st.write("This model accommodates high-yield premium strategies, tracking the exponential curve up to a 20% monthly target.")

st.divider()

# --- FILE PATH FOR PERSISTENT TRACKING ---
DATA_FILE = "pnl_data.csv"
TRACKER_MONTHS = 36  # Fixed 3-year horizon for the tracking journal

# --- GLOBAL SIDEBAR INPUTS (Retained from original script) ---
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


# --- PERSISTENT TRACKER DATA LOADER ---
def load_tracker_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        if len(df) == TRACKER_MONTHS:
            return df
    return pd.DataFrame({
        "Month": [f"Month {i}" for i in range(1, TRACKER_MONTHS + 1)],
        "Actual PnL ($)": [0.0] * TRACKER_MONTHS
    })

df_actuals = load_tracker_data()


# --- ENGINE 1: MAIN TRAJECTORY SIMULATION (Original Logic) ---
current_balance = starting_capital
months = 0
simulation_data = []

if monthly_yield == 0 and monthly_deposit == 0:
    st.error("You must have either a monthly return or a monthly deposit to grow the account!")
else:
    while current_balance < target_goal and months < 240:
        trading_profit = current_balance * (monthly_yield / 100)
        max_dollar_risk_per_trade = current_balance * (risk_per_trade / 100)
        
        simulation_data.append({
            "Month": months,
            "Portfolio Value ($)": current_balance,
            "Monthly Profit ($)": trading_profit,
            "Weekly Profit Target ($)": trading_profit / 4.33,
            "Max Risk Per Trade ($)": max_dollar_risk_per_trade
        })
        current_balance += trading_profit + monthly_deposit
        months += 1

    simulation_data.append({
        "Month": months,
        "Portfolio Value ($)": current_balance,
        "Monthly Profit ($)": current_balance * (monthly_yield / 100),
        "Weekly Profit Target ($)": (current_balance * (monthly_yield / 100)) / 4.33,
        "Max Risk Per Trade ($)": current_balance * (risk_per_trade / 100)
    })

df_sim = pd.DataFrame(simulation_data)


# --- ENGINE 2: 3-YEAR TRACKER MATRIX CALCULATIONS ---
# Calculate targets strictly mapped to the sidebar settings for the 3-year grid
tracker_balances = []
tracker_pnls = []
tracker_balance_runner = starting_capital

for m in range(TRACKER_MONTHS):
    pnl_target = tracker_balance_runner * (monthly_yield / 100)
    tracker_pnls.append(round(pnl_target, 2))
    tracker_balance_runner += pnl_target + monthly_deposit
    tracker_balances.append(round(tracker_balance_runner, 2))

df_tracker = pd.DataFrame({
    "Month": df_actuals["Month"],
    "Target PnL ($)": tracker_pnls,
    "Actual PnL ($)": df_actuals["Actual PnL ($)"].astype(float),
    "Target Balance ($)": tracker_balances
})
df_tracker["Variance ($)"] = df_tracker["Actual PnL ($)"] - df_tracker["Target PnL ($)"]


# --- CREATE TABS INTERFACE ---
tab1, tab2 = st.tabs(["📊 Main Projection Dashboard", "📅 3-Year Milestone Tracker & Live Entry"])


# ==========================================
# TAB 1: ORIGINAL COMPREHENSIVE PROJECTION
# ==========================================
with tab1:
    st.subheader("🏁 Performance Timeline")
    
    # Calculate performance using actual manual entries to override starting settings
    total_actual_pnl = df_tracker["Actual PnL ($)"].sum()
    current_portfolio_value = starting_capital + total_actual_pnl
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Theoretical Time to Goal", f"{months} Months", f"{(months/12):.1f} Years")
    col2.metric("Live Portfolio Balance", f"${current_portfolio_value:,.2f}", 
                delta=f"${total_actual_pnl:,.2f} Total Net PnL" if total_actual_pnl != 0 else None)
    col3.metric("Target Monthly Yield", f"{monthly_yield}%")
    col4.metric("Starting Base Risk Size", f"${starting_capital * (risk_per_trade / 100):,.2f}")
    
    st.divider()
    
    # Growth chart
    st.subheader("📉 Capital Scaling Trajectory")
    fig = px.area(
        df_sim, x="Month", y="Portfolio Value ($)", 
        title=f"Compounding Theoretical Profile at {monthly_yield}% Per Month",
        labels={"Portfolio Value ($)": "Account Balance ($)"}
    )
    fig.add_hline(y=target_goal, line_dash="dash", line_color="green", annotation_text="Target Goal Mark")
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Position Scaling Matrix 
    st.subheader("📋 Theoretical Position Scaling Guide")
    df_display = df_sim.copy()
    df_display["Portfolio Value ($)"] = df_display["Portfolio Value ($)"].map("${:,.2f}".format)
    df_display["Monthly Profit ($)"] = df_display["Monthly Profit ($)"].map("${:,.2f}".format)
    df_display["Weekly Profit Target ($)"] = df_display["Weekly Profit Target ($)"].map("${:,.2f}".format)
    df_display["Max Risk Per Trade ($)"] = df_display["Max Risk Per Trade ($)"].map("${:,.2f}".format)
    st.dataframe(df_display.set_index("Month"), use_container_width=True)


# ==========================================
# TAB 2: GRANULAR 3-YEAR TRACKER
# ==========================================
with tab2:
    st.header("📅 36-Month Goal Execution Journal")
    st.write("✏️ **Action:** Double-click cells in the **'Actual PnL ($)'** column to input your realistic trading results.")
    
    # Setup interactive dataframe input layout
    edited_df = st.data_editor(
        df_tracker[["Month", "Target PnL ($)", "Actual PnL ($)", "Variance ($)", "Target Balance ($)"]],
        disabled=["Month", "Target PnL ($)", "Variance ($)", "Target Balance ($)"],
        hide_index=True,
        use_container_width=True
    )
    
    # Interactive Save Actions
    if st.button("💾 Save Tracker Progress"):
        edited_df[["Month", "Actual PnL ($)"]].to_csv(DATA_FILE, index=False)
