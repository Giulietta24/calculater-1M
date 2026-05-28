import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Transparent Options Scaler", page_icon="⚡", layout="wide")

st.title("⚡ Aggressive Options Compounding Engine")
st.write("Track exactly how your options trading profits and your manual cash deposits combine to build your portfolio.")

st.divider()

# Sidebar for Inputs
st.sidebar.header("🕹️ Growth Levers")
starting_capital = st.sidebar.number_input("Starting Capital ($)", min_value=0.0, value=30000.0, step=1000.0)
target_goal = st.sidebar.number_input("Ultimate Goal Target ($)", min_value=0.0, value=1000000.0, step=50000.0)

st.sidebar.subheader("📈 Trading Strategy")
monthly_yield = st.sidebar.slider("Target Monthly Return (%)", min_value=0.0, max_value=20.0, value=20.0, step=0.5)

st.sidebar.subheader("💵 Capital Infusion")
monthly_deposit = st.sidebar.number_input("Monthly Contribution from Income ($)", min_value=0.0, value=1000.0, step=100.0,
                                         help="Fresh cash added to the portfolio at the end of each month.")

st.sidebar.subheader("🚨 Risk Management Rule")
risk_per_trade = st.sidebar.slider("Max Account Risk Per Trade (%)", min_value=0.5, max_value=20.0, value=5.0, step=0.5)

# Math engine to compute timeline
current_balance = starting_capital
months = 0
data = []

if monthly_yield == 0 and monthly_deposit == 0:
    st.error("You must have either a monthly return or a monthly deposit to grow the account!")
else:
    # Run simulation month-by-month until target is hit
    while current_balance < target_goal and months < 240:
        trading_profit = current_balance * (monthly_yield / 100)
        max_dollar_risk_per_trade = current_balance * (risk_per_trade / 100)
        
        data.append({
            "Month": months,
            "Starting Balance ($)": current_balance,
            "Options Profit ($)": trading_profit,
            "Weekly Profit Target ($)": trading_profit / 4.33,
            "Fresh Cash Added ($)": monthly_deposit,
            "Max Risk Per Trade ($)": max_dollar_risk_per_trade
        })
        
        # Balance compounds AND takes the manual deposit
        current_balance += trading_profit + monthly_deposit
        months += 1

    # Add final milestone row
    data.append({
        "Month": months,
        "Starting Balance ($)": current_balance,
        "Options Profit ($)": current_balance * (monthly_yield / 100),
        "Weekly Profit Target ($)": (current_balance * (monthly_yield / 100)) / 4.33,
        "Fresh Cash Added ($)": 0.0, # Target achieved, no more deposits needed
        "Max Risk Per Trade ($)": current_balance * (risk_per_trade / 100)
    })

df = pd.DataFrame(data)

# Dashboard KPI Metrics
st.subheader("🏁 Performance Timeline")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Time to $1M", f"{months} Months", f"{(months/12):.1f} Years")
col2.metric("Target Monthly Yield", f"{monthly_yield}%")
col3.metric("Monthly Deposit", f"${monthly_deposit:,.2f}")
col4.metric("Starting Base Risk Size", f"${starting_capital * (risk_per_trade / 100):,.2f}")

st.divider()

# Growth chart
st.subheader("📉 Capital Scaling Trajectory")
fig = px.area(
    df, x="Month", y="Starting Balance ($)", 
    title=f"Compounding Profile at {monthly_yield}% Per Month + ${monthly_deposit:,.2f} Deposits",
    labels={"Starting Balance ($)": "Account Balance ($)"}
)
fig.add_hline(y=target_goal, line_dash="dash", line_color="green", annotation_text="Million Dollar Goal")
st.plotly_chart(fig, use_container_width=True)

st.divider()

# Dynamic Trade Sizing Guide
st.subheader("📋 Step-by-Step Position Scaling Guide")
st.write("Watch how Month 0's **Starting Balance** + **Options Profit** + **Fresh Cash Added** perfectly equals Month 1's **Starting Balance**:")

# Format for clean web display
df_display = df.copy()
df_display["Starting Balance ($)"] = df_display["Starting Balance ($)"].map("${:,.2f}".format)
df_display["Options Profit ($)"] = df_display["Options Profit ($)"].map("${:,.2f}".format)
df_display["Weekly Profit Target ($)"] = df_display["Weekly Profit Target ($)"].map("${:,.2f}".format)
df_display["Fresh Cash Added ($)"] = df_display["Fresh Cash Added ($)"].map("${:,.2f}".format)
df_display["Max Risk Per Trade ($)"] = df_display["Max Risk Per Trade ($)"].map("${:,.2f}".format)

st.dataframe(df_display.set_index("Month"), use_container_width=True)
