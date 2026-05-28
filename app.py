import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Realistic Options Scaler", page_icon="🛡️", layout="wide")

st.title("🛡️ Realistic $30k to $1M Options Scaling Engine")
st.write("This engine combines realistic compounding trading returns with monthly cash deposits and strict risk parameters.")

st.divider()

# Sidebar for Inputs
st.sidebar.header("🕹️ Growth Levers")
starting_capital = st.sidebar.number_input("Starting Capital ($)", min_value=0.0, value=30000.0, step=1000.0)
target_goal = st.sidebar.number_input("Ultimate Goal Target ($)", min_value=0.0, value=1000000.0, step=50000.0)

st.sidebar.subheader("📈 Trading Strategy")
monthly_yield = st.sidebar.slider("Realistic Monthly Return (%)", min_value=1.0, max_value=8.0, value=3.5, step=0.1,
                                  help="1%-3% is professional-grade consistency. 4%-5% requires high-skill active trading.")

st.sidebar.subheader("💵 Capital Infusion")
monthly_deposit = st.sidebar.number_input("Monthly Contribution from Income ($)", min_value=0.0, value=1000.0, step=100.0,
                                         help="Adding fresh cash drastically shortens your timeline in the early years.")

st.sidebar.subheader("🚨 Risk Management Rule")
risk_per_trade = st.sidebar.slider("Max Account Risk Per Trade (%)", min_value=0.5, max_value=5.0, value=2.0, step=0.5,
                                   help="The % of your total account you are willing to lose if a single trade goes completely wrong.")

# Math engine to compute timeline with ongoing deposits
current_balance = starting_capital
months = 0
data = []

# Guard rail to prevent infinite loops if yields are 0 and no deposits
if monthly_yield == 0 and monthly_deposit == 0:
    st.error("You must have either a monthly return or a monthly deposit to grow the account!")
else:
    # Run simulation month-by-month until target is hit (capped at 240 months / 20 years for safety)
    while current_balance < target_goal and months < 240:
        trading_profit = current_balance * (monthly_yield / 100)
        
        # Calculate strict capital allocation for the month
        # Assumes a typical option trade risks a defined amount (e.g., width of a credit spread minus premium received)
        max_dollar_risk_per_trade = current_balance * (risk_per_trade / 100)
        
        data.append({
            "Month": months,
            "Portfolio Value ($)": current_balance,
            "Monthly Profit ($)": trading_profit,
            "Weekly Profit Target ($)": trading_profit / 4.33,
            "Max Risk Per Trade ($)": max_dollar_risk_per_trade
        })
        
        # Compound the account and inject fresh capital for the next month
        current_balance += trading_profit + monthly_deposit
        months += 1

    # Add final month milestone
    data.append({
        "Month": months,
        "Portfolio Value ($)": current_balance,
        "Monthly Profit ($)": current_balance * (monthly_yield / 100),
        "Weekly Profit Target ($)": (current_balance * (monthly_yield / 100)) / 4.33,
        "Max Risk Per Trade ($)": current_balance * (risk_per_trade / 100)
    })

df = pd.DataFrame(data)

# Dashboard KPI Metrics
st.subheader("🏁 Timeline Reality Check")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Time to $1M", f"{months} Months", f"{(months/12):.1f} Years")
col2.metric("Your Monthly Return Target", f"{monthly_yield}%")
col3.metric("Monthly Capital Added", f"${monthly_deposit:,.2f}")
col4.metric("Starting Base Risk Size", f"${starting_capital * (risk_per_trade / 100):,.2f}")

st.divider()

# Growth chart
st.subheader("📉 Your Capital Scaling Trajectory")
fig = px.area(
    df, x="Month", y="Portfolio Value ($)", 
    title="How Your Account Builds Over Time (Trading + Infusions)",
    labels={"Portfolio Value ($)": "Account Balance ($)"}
)
fig.add_hline(y=target_goal, line_dash="dash", line_color="red", annotation_text="Million Dollar Goal")
st.plotly_chart(fig, use_container_width=True)

st.divider()

# Dynamic Trade Sizing Guide
st.subheader("🛡️ Step-by-Step Risk Management Blueprint")
st.write(
    "To survive long enough to hit $1M, you must size your positions dynamically. "
    "As your account grows, your dollar-risk per trade can safely expand *without* expanding your percentage risk."
)

# Format for clean UX display
df_display = df.copy()
df_display["Portfolio Value ($)"] = df_display["Portfolio Value ($)"].map("${:,.2f}".format)
df_display["Monthly Profit ($)"] = df_display["Monthly Profit ($)"].map("${:,.2f}".format)
df_display["Weekly Profit Target ($)"] = df_display["Weekly Profit Target ($)"].map("${:,.2f}".format)
df_display["Max Risk Per Trade ($)"] = df_display["Max Risk Per Trade ($)"].map("${:,.2f}".format)

st.dataframe(df_display.set_index("Month"), use_container_width=True)
