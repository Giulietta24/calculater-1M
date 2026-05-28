import streamlit as st
import pandas as pd
import numpy as np

st.title("🎯 The Options Wheel Strategy Tracker")
st.write("Model your income via Cash-Secured Puts and Covered Calls safely.")

# Sidebar Adjustments
starting_capital = st.sidebar.number_input("Portfolio Size ($)", value=30000.0)
target_monthly_pct = st.sidebar.slider("Target Monthly Premium Yield (%)", 1.0, 20.0, 3.0)

# Display realities of target choices
if target_monthly_pct > 5.0:
    st.warning("⚠️ High Yield Warning: Generating over 5% a month requires trading high-volatility underlyings. This significantly increases your risk of capital destruction if the underlying stock craters.")
else:
    st.success("✅ Sustainable Yield Goal: 1% - 4% targets allow you to sell options on stable, institutional-grade stocks or index ETFs.")

# Math calculations
monthly_income = starting_capital * (target_monthly_pct / 100)
weekly_income = monthly_income / 4.33

st.metric("Expected Monthly Income", f"${monthly_income:,.2f}")
st.metric("Expected Weekly Income", f"${weekly_income:,.2f}")
