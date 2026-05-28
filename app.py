import streamlit as st
import pandas as pd
import plotly.express as px

# Set up page configurations
st.set_page_config(page_title="1-Year Goal Calculator", page_icon="💰", layout="centered")

st.title("🎯 1-Year Financial Goal Calculator")
st.write("Track how much you need to make weekly to hit your target in exactly 52 weeks.")

st.divider()

# Sidebar for User Inputs
st.sidebar.header("Configure Your Goal")
starting_capital = st.sidebar.number_input(
    "Starting Capital ($)", min_value=0.0, value=1000.0, step=100.0, format="%.2f"
)
target_goal = st.sidebar.number_input(
    "Target Goal ($)", min_value=0.0, value=10000.0, step=500.0, format="%.2f"
)

# Core Calculations
if target_goal <= starting_capital:
    st.error("🚨 Your target goal must be greater than your starting capital!")
else:
    total_needed = target_goal - starting_capital
    weeks_in_year = 52
    weekly_target = total_needed / weeks_in_year

    # Display Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Total Gap to Close", value=f"${total_needed:,.2f}")
    col2.metric(label="Weekly Target", value=f"${weekly_target:,.2f}", delta="- Required")
    col3.metric(label="Timeframe", value="52 Weeks (1 Year)")

    st.divider()

    # Create a visual growth projection dataframe
    weeks = list(range(0, weeks_in_year + 1))
    balances = [starting_capital + (weekly_target * w) for w in weeks]
    
    df = pd.DataFrame({
        "Week": weeks,
        "Projected Balance ($)": balances
    })

    # Plotly Chart for Interactive Visualization
    st.subheader("📈 Your 52-Week Growth Trajectory")
    fig = px.line(
        df, 
        x="Week", 
        y="Projected Balance ($)", 
        title="Weekly Path to Target",
        labels={"Projected Balance ($)": "Account Value ($)", "Week": "Week Number"}
    )
    
    # Highlight the goal line
    fig.add_hline(y=target_goal, line_dash="dash", line_color="green", annotation_text="Goal Target")
    st.plotly_chart(fig, use_container_width=True)

    # Breakdowns / Milestones Accordion
    with st.expander("📌 View Monthly Milestones"):
        milestones = []
        for month in range(1, 13):
            # Roughly 4.33 weeks per month
            m_week = min(int(month * 4.33), 52)
            milestones.append({
                "Month": f"Month {month}",
                "Target Week": m_week,
                "Expected Balance": f"${balances[m_week]:,.2f}"
            })
        st.table(pd.DataFrame(milestones))