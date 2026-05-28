import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Options Compounding Planner", page_icon="📈", layout="wide")

st.title("💸 Options Portfolio Compounding & Income Planner")
st.write("Ditch fixed cash deposits. This model focuses on compounding returns and realistic percentage gains.")

st.divider()

# Layout layout split into sidebar configuration and main output
st.sidebar.header("🛡️ Portfolio Settings")
starting_capital = st.sidebar.number_input("Starting Capital ($)", min_value=0.0, value=30000.0, step=1000.0, format="%.2f")
target_goal = st.sidebar.number_input("Ultimate Goal Target ($)", min_value=0.0, value=1000000.0, step=50000.0, format="%.2f")

st.sidebar.subheader("Trading Performance Target")
# Realistic baseline for selling premium (Wheeling, Spreads) typically ranges between 1.5% to 5% monthly
monthly_yield = st.sidebar.slider("Target Monthly Return (%)", min_value=0.5, max_value=15.0, value=3.0, step=0.1)

st.sidebar.info(
    "💡 **Reality Check:**\n"
    "* 1%–2% / month: Conservative & highly sustainable (Beats index funds).\n"
    "* 3%–5% / month: Moderate. Requires active management (Wheeling, Spreads).\n"
    "* >5% / month: High Risk. Expect substantial drawdowns and volatility."
)

# Math calculations
monthly_rate = monthly_yield / 100
# Convert monthly compound rate to an implied weekly rate
weekly_rate = (1 + monthly_rate) ** (1 / 4.33) - 1

# Calculate time to hit target using logarithms
if monthly_rate > 0 and target_goal > starting_capital:
    months_needed = np.log(target_goal / starting_capital) / np.log(1 + monthly_rate)
    years_needed = months_needed / 12
else:
    months_needed = 0
    years_needed = 0

# Dashboard Summary Cards
st.subheader("📊 Timeline to Reach $1,000,000")
c1, c2, c3 = st.columns(3)
c1.metric(label="Target Monthly Yield", value=f"{monthly_yield}%")
c2.metric(label="Estimated Time to Goal", value=f"{months_needed:.1f} Months", delta=f"{years_needed:.1f} Years")
c3.metric(label="Implied Annualized Return", value=f"{((1 + monthly_rate)**12 - 1)*100:.1f}%")

st.divider()

# Generate the Compounding Data Frame
months_range = list(range(0, int(np.ceil(months_needed)) + 1))
balances = [starting_capital * ((1 + monthly_rate) ** m) for m in months_range]

# Keep lists bounded nicely
df_monthly = pd.DataFrame({
    "Month": months_range,
    "Portfolio Value ($)": balances,
})
# Calculate the required dollar income generated for THAT specific month
df_monthly["Monthly Income Target ($)"] = df_monthly["Portfolio Value ($)"] * monthly_rate
df_monthly["Weekly Income Target ($)"] = df_monthly["Portfolio Value ($)"] * weekly_rate

# Display the Growth Curve
st.subheader("📈 The Compounding Curve")
fig = px.line(
    df_monthly, 
    x="Month", 
    y="Portfolio Value ($)", 
    title="Exponential Account Growth",
    labels={"Portfolio Value ($)": "Account Net Liquidity ($)", "Month": "Months Elapsed"}
)
fig.add_hline(y=target_goal, line_dash="dash", line_color="gold", annotation_text="Milestone Target")
st.plotly_chart(fig, use_container_width=True)

st.divider()

# Interactive Milestone Breakdown
st.subheader("📅 Your Dynamic Scaling Milestones")
st.write("Notice how your required weekly dollar return starts small and naturally steps up as your account size grows:")

# Format table for cleaner user reading
df_display = df_monthly.copy()
df_display["Portfolio Value ($)"] = df_display["Portfolio Value ($)"].map("${:,.2f}".format)
df_display["Monthly Income Target ($)"] = df_display["Monthly Income Target ($)"].map("${:,.2f}".format)
df_display["Weekly Income Target ($)"] = df_display["Weekly Income Target ($)"].map("${:,.2f}".format)

# Slice table to look at the first 24 months or milestones
st.dataframe(df_display.set_index("Month"), use_container_width=True)
