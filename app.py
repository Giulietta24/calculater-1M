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

# --- FILE PATHS FOR PERSISTENT STORAGE ---
MONTH_DATA_FILE = "pnl_data.csv"
WEEK_DATA_FILE = "weekly_pnl_data.csv"
JOURNAL_DATA_FILE = "trade_journal.csv"
TRACKER_MONTHS = 36 

# --- GENERATE CALENDAR MONTH NAMES DYNAMICALLY ---
start_date = datetime.now()
CALENDAR_MONTHS = [(start_date + relativedelta(months=i)).strftime("%B %Y") for i in range(TRACKER_MONTHS)]

# --- GLOBAL SIDEBAR INPUTS ---
st.sidebar.header("🕹️ Growth Levers")
starting_capital = st.sidebar.number_input("Starting Capital ($)", min_value=0.0, value=30000.0, step=1000.0)
target_goal = st.sidebar.number_input("Ultimate Goal Target ($)", min_value=0.0, value=1000000.0, step=50000.0)

st.sidebar.subheader("📈 Trading Strategy")
monthly_yield = st.sidebar.slider("Target Monthly Return (%)", min_value=1.0, max_value=20.0, value=20.0, step=0.5)

st.sidebar.subheader("💵 Capital Infusion")
monthly_deposit = st.sidebar.number_input("Monthly Contribution from Income ($)", min_value=0.0, value=0.0, step=100.0)

st.sidebar.subheader("🚨 Risk Management Rule")
risk_per_trade = st.sidebar.slider("Max Account Risk Per Trade (%)", min_value=0.5, max_value=20.0, value=5.0, step=0.5)
# Add this control directly to your sidebar workspace
lookback_choice = st.sidebar.selectbox(
    "Alpha/Beta Baseline Window", 
    options=["3mo", "6mo", "1y"], 
    index=1  # Default choice points to 6 months
)

# Then pass that dynamic variable straight into your data fetching functions:
daily_hist = yf.Ticker(ticker).history(period=lookback_choice)

# --- PERSISTENT DATA LOADERS ---
def load_month_data():
    if os.path.exists(MONTH_DATA_FILE):
        df = pd.read_csv(MONTH_DATA_FILE)
        if len(df) == TRACKER_MONTHS and df["Month"].iloc[0] == CALENDAR_MONTHS[0]:
            return df
    return pd.DataFrame({"Month": CALENDAR_MONTHS, "Actual PnL ($)": [0.0] * TRACKER_MONTHS})

def load_week_data():
    if os.path.exists(WEEK_DATA_FILE):
        df = pd.read_csv(WEEK_DATA_FILE)
        if df["Month"].iloc[0] == CALENDAR_MONTHS[0]:
            return df
    months_col, weeks_col = [], []
    for m_name in CALENDAR_MONTHS:
        for w in range(1, 5):
            months_col.append(m_name)
            weeks_col.append(f"Week {w}")
    return pd.DataFrame({"Month": months_col, "Week": weeks_col, "Actual PnL ($)": [0.0] * (TRACKER_MONTHS * 4)})

def load_journal_data():
    if os.path.exists(JOURNAL_DATA_FILE):
        df = pd.read_csv(JOURNAL_DATA_FILE)
        df["Date"] = pd.to_datetime(df["Date"]).dt.date
        return df
    # Added "Status" column to handle active inventory
    return pd.DataFrame(columns=["Date", "Month Ref", "Week Ref", "Ticker", "Strategy Type", "Status", "Trade PnL ($)", "Notes"])

df_actual_months = load_month_data()
df_actual_weeks = load_week_data()
df_journal = load_journal_data()


# --- MATH ENGINE 1: SIMULATION CORE ---
current_balance = starting_capital
months_counter = 0
simulation_data = []

while current_balance < target_goal and months_counter < 240:
    trading_profit = current_balance * (monthly_yield / 100)
    simulation_data.append({
        "Month Index": months_counter,
        "Portfolio Value ($)": current_balance,
        "Monthly Profit ($)": trading_profit,
        "Weekly Profit Target ($)": trading_profit / 4.33,
        "Max Risk Per Trade ($)": current_balance * (risk_per_trade / 100)
    })
    current_balance += trading_profit + monthly_deposit
    months_counter += 1

df_sim = pd.DataFrame(simulation_data)


# --- MATH ENGINE 2: TRACKER CONNECTIONS ---
tracker_balances, tracker_pnls = [], []
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


# --- TABS LAYOUT ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Main Projection Dashboard", 
    "📅 3-Year Monthly Milestones", 
    "⏱️ Weekly Aggregates", 
    "📓 Comprehensive Trade Journal"
])


# ==========================================
# TAB 1: DASHBOARD
# ==========================================
with tab1:
    st.subheader("🏁 Live Performance vs Projection")
    total_actual_pnl = df_tracker["Actual PnL ($)"].sum()
    current_portfolio_value = starting_capital + total_actual_pnl
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Theoretical Time to Goal", f"{months_counter} Months")
    col2.metric("Live Portfolio Balance", f"${current_portfolio_value:,.2f}", delta=f"${total_actual_pnl:,.2f} Net PnL")
    col3.metric("Target Monthly Yield", f"{monthly_yield}%")
    col4.metric("Starting Base Risk Size", f"${starting_capital * (risk_per_trade / 100):,.2f}")
    
    st.divider()
    fig = px.area(df_sim, x="Month Index", y="Portfolio Value ($)", title="Compounding Target Matrix")
    fig.add_hline(y=target_goal, line_dash="dash", line_color="green")
    st.plotly_chart(fig, use_container_width=True)


# ==========================================
# TAB 2: MONTHLY MILESTONES
# ==========================================
with tab2:
    st.header("📅 36-Month Milestone Ledger")
    df_tracker_display = df_tracker.copy()
    for col in ["Target PnL ($)", "Actual PnL ($)", "Variance ($)", "Target Balance ($)"]:
        df_tracker_display[col] = df_tracker_display[col].map("${:,.2f}".format)
    st.dataframe(df_tracker_display, hide_index=True, use_container_width=True)


# ==========================================
# TAB 3: WEEKLY AGGREGATES
# ==========================================
with tab3:
    st.header("⏱️ Weekly Milestone Performance")
    selected_month = st.selectbox("View Weeklies For:", CALENDAR_MONTHS)
    
    df_filtered_weeks = df_actual_weeks[df_actual_weeks["Month"] == selected_month].copy()
    m_target = df_tracker[df_tracker["Month"] == selected_month].iloc[0]["Target PnL ($)"]
    df_filtered_weeks["Target PnL ($)"] = round(m_target / 4, 2)
    df_filtered_weeks["Variance ($)"] = df_filtered_weeks["Actual PnL ($)"] - df_filtered_weeks["Target PnL ($)"]
    
    st.dataframe(df_filtered_weeks, hide_index=True, use_container_width=True)


# ==========================================
# TAB 4: UPGRADED TRADE JOURNAL (ALL STRATEGIES)
# ==========================================
with tab4:
    st.header("📓 Multi-Asset Trading Ledger")
    
    # Form layout for inputting raw values
    with st.form("trade_entry_form", clear_on_submit=True):
        st.subheader("🖋️ Log New Trade Setup / Asset Allocation")
        c1, c2, c3 = st.columns(3)
        t_date = c1.date_input("Trade Execution Date", value=datetime.now().date())
        t_month = c2.selectbox("Assign to Calculation Month:", CALENDAR_MONTHS)
        t_week = c3.selectbox("Assign to Week:", ["Week 1", "Week 2", "Week 3", "Week 4"])
        
        c4, c5, c6, c7 = st.columns(4)
        t_ticker = c4.text_input("Ticker Symbol (e.g. SPY, NVDA, TSLA)", value="SPY").upper()
        
        # Expanded strategy types to track everything requested
        t_strategy = c5.selectbox("Asset / Strategy Class:", [
            "Cash Secured Put (CSP)", 
            "Covered Call / Wheel",
            "Credit Spread (Put/Call)", 
            "Long Call Buy",
            "Long Put Buy",
            "Naked Premium / Condor",
            "Shares / Stocks Held",
            "LEAPS / Long-Term Options",
            "Futures / Crypto Scalp"
        ])
        
        # Status dropdown to isolate closed performance from currently held inventory
        t_status = c6.selectbox("Trade Status:", ["Closed (Realized PnL)", "Open (Current Holding)"])
        t_pnl = c7.number_input("Realized PnL ($ Amount - Leave 0 if Open)", value=0.00, step=10.0)
        
        t_notes = st.text_input("Position Notes (Entry delta, cost basis, expiration, adjustments)", placeholder="Sold 30 delta CSP, covered calls running at...")
        submit_btn = st.form_submit_button("⚡ Commit Entry to Database")
        
        if submit_btn:
            new_trade = pd.DataFrame([{
                "Date": t_date, "Month Ref": t_month, "Week Ref": t_week,
                "Ticker": t_ticker, "Strategy Type": t_strategy, "Status": t_status, "Trade PnL ($)": t_pnl, "Notes": t_notes
            }])
            df_journal = pd.concat([df_journal, new_trade], ignore_index=True)
            df_journal.to_csv(JOURNAL_DATA_FILE, index=False)
            
            # --- AUTO RUN ROLLUP CASCADE ENGINE ---
            # Calculates weekly / monthly targets using CLOSED trades only so unrealized holdings don't throw off milestones
            df_closed_only = df_journal[df_journal["Status"] == "Closed (Realized PnL)"]
            
            # 1. Clear out old weekly state & reload from fresh closed data
            df_actual_weeks["Actual PnL ($)"] = 0.0
            if not df_closed_only.empty:
                week_rollups = df_closed_only.groupby(["Month Ref", "Week Ref"])["Trade PnL ($)"].sum().reset_index()
                for _, row in week_rollups.iterrows():
                    m_ref, w_ref, pnl_sum = row["Month Ref"], row["Week Ref"], row["Trade PnL ($)"]
                    w_idx = df_actual_weeks[(df_actual_weeks["Month"] == m_ref) & (df_actual_weeks["Week"] == w_ref)].index
                    df_actual_weeks.loc[w_idx, "Actual PnL ($)"] = pnl_sum
            df_actual_weeks.to_csv(WEEK_DATA_FILE, index=False)
            
            # 2. Recalculate monthly totals from the updated weekly totals
            month_rollups = df_actual_weeks.groupby("Month")["Actual PnL ($)"].sum().reset_index()
            df_final_months = pd.DataFrame({"Month": CALENDAR_MONTHS}).merge(month_rollups, on="Month", how="left").fillna(0.0)
            df_final_months.to_csv(MONTH_DATA_FILE, index=False)
            
            st.success("Entry processed! Multi-tab cascading metrics updated completely.")
            st.rerun()

    st.divider()
    
    # --- STRATEGY METRICS & HISTORICAL FILTERS ---
    st.subheader("🔍 Filter & Analyze Portfolio Ledger")
    
    if not df_journal.empty:
        col_f1, col_f2 = st.columns([1, 3])
        
        with col_f1:
            # Dynamic filter widgets containing all requested asset classes
            filter_status = st.multiselect("Filter by Status:", df_journal["Status"].unique(), default=df_journal["Status"].unique())
            filter_strat = st.multiselect("Filter by Strategy / Asset Class:", df_journal["Strategy Type"].unique(), default=df_journal["Strategy Type"].unique())
            filter_tick = st.multiselect("Filter by Ticker Symbol:", df_journal["Ticker"].unique(), default=df_journal["Ticker"].unique())
        
        # Apply filter settings
        df_filtered_journal = df_journal[
            (df_journal["Status"].isin(filter_status)) &
            (df_journal["Strategy Type"].isin(filter_strat)) & 
            (df_journal["Ticker"].isin(filter_tick))
        ]
        
        with col_f2:
            st.write("📋 **Matching Positions Ledger:**")
            st.dataframe(df_filtered_journal.sort_values(by="Date", ascending=False), hide_index=True, use_container_width=True)
            
            # Performance Metric Blocks broken down by Strategy
            st.write("📈 **Performance Breakdown by Parameters:**")
            
            # Filter performance tracking using only realized items to ensure math accuracy
            df_stats_base = df_filtered_journal[df_filtered_journal["Status"] == "Closed (Realized PnL)"]
            
            if not df_stats_base.empty:
                stats_df = df_stats_base.groupby("Strategy Type")["Trade PnL ($)"].agg(["sum", "count", "mean"]).reset_index()
                stats_df.columns = ["Strategy Type", "Total Realized PnL ($)", "Trades Executed & Closed", "Average PnL / Setup ($)"]
                st.dataframe(stats_df, hide_index=True, use_container_width=True)
            else:
                st.info("No realized/closed performance metrics available for the currently selected filters.")
                
            # Quick check block for open exposure
            open_count = len(df_filtered_journal[df_filtered_journal["Status"] == "Open (Current Holding)"])
            if open_count > 0:
                st.warning(f"🚨 Note: You are currently displaying {open_count} 'Open' positions/holdings in your filter settings. Open positions do not inject raw PnL math into the milestone charts until you log their closing entries.")
    else:
        st.info("Your trade ledger is empty. Use the input form above to log your first trade or asset allocation setup!")
# Add this right below your table in Tab 4 to download a copy anytime
st.download_button(
    label="📥 Export Journal to Desktop CSV",
    data=df_journal.to_csv(index=False),
    file_name="my_options_journal_backup.csv",
    mime="text/csv"
)
