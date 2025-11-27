"""
Simple Cost Monitoring Dashboard
Real-time cost and usage tracking
"""

import streamlit as st
from cost_tracker import CostTracker
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

st.set_page_config(
    page_title="LawScout AI - Cost Dashboard",
    page_icon="📊",
    layout="wide"
)

# Initialize tracker
tracker = CostTracker()
tracker._load_state()

# Header
st.title("📊 LawScout AI - Cost Dashboard")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Overview metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    mvp_cost = tracker.get_total_cost('mvp_phase')
    st.metric("MVP Cost", f"${mvp_cost:.2f}", delta=None)

with col2:
    monthly_cost = tracker.get_total_cost('monthly_operational')
    st.metric("Monthly Cost", f"${monthly_cost:.2f}", delta=None)

with col3:
    annual_cost = monthly_cost * 12
    st.metric("Annual Projection", f"${annual_cost:.2f}", delta=None)

with col4:
    total_cost = mvp_cost + monthly_cost
    st.metric("Total to Date", f"${total_cost:.2f}", delta=None)

st.markdown("---")

# Cost breakdown charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("MVP Phase Costs")
    mvp_data = tracker.costs['mvp_phase']
    fig = go.Figure(data=[go.Pie(
        labels=[k.replace('_', ' ').title() for k in mvp_data.keys()],
        values=list(mvp_data.values()),
        hole=.3
    )])
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Monthly Operational Costs")
    monthly_data = tracker.costs['monthly_operational']
    fig = go.Figure(data=[go.Pie(
        labels=[k.replace('_', ' ').title() for k in monthly_data.keys()],
        values=list(monthly_data.values()),
        hole=.3
    )])
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Usage statistics
st.subheader("Usage Statistics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Queries Processed", f"{tracker.usage['queries_processed']:,}")

with col2:
    st.metric("Embeddings Generated", f"{tracker.usage['embeddings_generated']:,}")

with col3:
    st.metric("Documents Stored", f"{tracker.usage['documents_stored']:,}")

with col4:
    st.metric("API Calls", f"{tracker.usage['api_calls']:,}")

st.markdown("---")

# Unit economics
st.subheader("Unit Economics & Break-Even Analysis")

col1, col2 = st.columns(2)

with col1:
    if tracker.usage['queries_processed'] > 0:
        cost_per_query = total_cost / tracker.usage['queries_processed']
        st.metric("Cost per Query", f"${cost_per_query:.4f}")
        
        price_per_user = 49.00
        st.metric("Price per User/Month", f"${price_per_user:.2f}")
    else:
        st.info("No usage data yet")

with col2:
    if monthly_cost > 0:
        price_per_user = 49.00
        users_needed = monthly_cost / price_per_user
        st.metric("Users to Break Even", f"{users_needed:.0f}")
        
        margin = (price_per_user - (monthly_cost / max(1, users_needed))) / price_per_user
        st.metric("Gross Margin (at break-even)", f"{margin:.1%}")

# Detailed cost table
st.markdown("---")
st.subheader("Detailed Cost Breakdown")

import pandas as pd

# Create DataFrame
cost_data = []
for category, items in tracker.costs.items():
    for item, cost in items.items():
        cost_data.append({
            'Category': category.replace('_', ' ').title(),
            'Item': item.replace('_', ' ').title(),
            'Cost': f"${cost:.2f}"
        })

df = pd.DataFrame(cost_data)
st.dataframe(df, use_container_width=True)

# Download report
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    if st.button("📥 Download Report (TXT)"):
        report = tracker.generate_report()
        st.download_button(
            "Download",
            data=report,
            file_name=f"cost_report_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )

with col2:
    if st.button("📊 Download Report (CSV)"):
        csv = tracker.export_csv()
        st.download_button(
            "Download",
            data=csv,
            file_name=f"cost_report_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

