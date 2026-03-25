import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Executive Analytics Dashboard",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for "Next Level" aesthetics
st.markdown("""
<style>
    /* Metric Cards */
    div[data-testid="stMetricValue"] {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1f77b4;
    }
    div[data-testid="stMetricDelta"] {
        font-size: 1rem;
    }
    /* Headers */
    h1 {
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #FF4B2B, #FF416C);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding-bottom: 20px;
    }
    h2, h3 {
        color: #2c3e50;
    }
    /* Main container styling */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    /* Enhance metric container background */
    [data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Generate Dummy Data
@st.cache_data
def load_data():
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    
    data = {
        'Date': dates,
        'Revenue': np.random.normal(50000, 15000, len(dates)).cumsum(),
        'Active Users': np.random.normal(1000, 50, len(dates)).cumsum(),
        'Server Load (%)': np.random.uniform(20, 95, len(dates)),
        'Conversion Rate': np.random.uniform(1.5, 5.5, len(dates)),
        'Region': np.random.choice(['North America', 'EMEA', 'APAC', 'LATAM'], len(dates)),
        'Product Category': np.random.choice(['Enterprise', 'Pro', 'Basic', 'Custom'], len(dates))
    }
    df = pd.DataFrame(data)
    # Add some seasonality to Revenue
    df['Revenue'] = df['Revenue'] * (1 + 0.2 * np.sin(np.arange(len(dates)) * np.pi / 180))
    return df

df = load_data()

# Sidebar
with st.sidebar:
    st.title("⚙️ Filters & Controls")
    st.markdown("Use the filters below to adjust the dashboard view.")
    
    # Date Range Filter
    date_range = st.date_input(
        "Date Range",
        value=(df['Date'].min(), df['Date'].max()),
        min_value=df['Date'].min(),
        max_value=df['Date'].max()
    )
    
    # Region Filter
    regions = st.multiselect(
        "Select Regions",
        options=df['Region'].unique(),
        default=df['Region'].unique()
    )
    
    # Category Filter
    categories = st.multiselect(
        "Product Category",
        options=df['Product Category'].unique(),
        default=df['Product Category'].unique()
    )
    
    st.markdown("---")
    st.markdown("### System Status")
    st.progress(85)
    st.caption("All systems operational. Last updated: Just now.")
    st.caption("v2.4.1")

# Ensure date_range has both start and end dates selected
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
    # Filter logic
    mask = (
        (df['Date'].dt.date >= start_date) & 
        (df['Date'].dt.date <= end_date) & 
        (df['Region'].isin(regions)) & 
        (df['Product Category'].isin(categories))
    )
    filtered_df = df[mask]
else:
    filtered_df = df

# Main Panel
st.title("Executive Analytics Command Center")
st.markdown("Real-time monitoring and high-level performance metrics of key business operations.")

# Ensure we have data to display after filtering
if filtered_df.empty:
    st.warning("No data available for the selected filters. Please adjust your criteria.")
else:
    # ------------------
    # Top Metrics Row
    # ------------------
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        current_rev = filtered_df['Revenue'].iloc[-1]
        st.metric(label="Total Revenue", value=f"${current_rev:,.0f}", delta="12.5% vs Last Month")
    with col2:
        current_users = filtered_df['Active Users'].iloc[-1]
        st.metric(label="Active Users", value=f"{current_users:,.0f}", delta="4.2% vs Last Month")
    with col3:
        avg_conv = filtered_df['Conversion Rate'].mean()
        st.metric(label="Avg Conversion", value=f"{avg_conv:.2f}%", delta="-0.5% vs Last Month", delta_color="inverse")
    with col4:
        avg_load = filtered_df['Server Load (%)'].mean()
        st.metric(label="Avg Server Load", value=f"{avg_load:.1f}%", delta="-5% vs Last Month")

    st.markdown("---")

    # ------------------
    # Charts Row 1
    # ------------------
    col_main, col_side = st.columns([2, 1])
    
    with col_main:
        st.subheader("Revenue Trajectory")
        fig_revenue = px.area(
            filtered_df, x='Date', y='Revenue', 
            color_discrete_sequence=['#00f2fe']
        )
        fig_revenue.update_layout(
            margin=dict(l=0, r=0, t=20, b=0), 
            height=350,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        # Adding gradient effect approximation via fillcolor
        fig_revenue.update_traces(fillcolor='rgba(0, 242, 254, 0.3)', mode='lines')
        st.plotly_chart(fig_revenue, use_container_width=True)
    
    with col_side:
        st.subheader("Revenue by Region")
        region_rev = filtered_df.groupby('Region')['Revenue'].last().reset_index()
        fig_donut = px.pie(
            region_rev, values='Revenue', names='Region', hole=0.6,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_donut.update_layout(
            showlegend=False, 
            margin=dict(l=0, r=0, t=20, b=0), 
            height=350,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        fig_donut.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_donut, use_container_width=True)

    # ------------------
    # Charts Row 2
    # ------------------
    col_chart3, col_chart4 = st.columns(2)
    
    with col_chart3:
        st.subheader("Active Users by Product Category")
        cat_data = filtered_df.groupby('Product Category')['Active Users'].sum().reset_index()
        fig_bar = px.bar(
            cat_data, x='Product Category', y='Active Users',
            color='Product Category',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_bar.update_layout(
            margin=dict(l=0, r=0, t=20, b=0), 
            height=350, 
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col_chart4:
        st.subheader("System Load Distribution")
        fig_box = px.box(
            filtered_df, x='Region', y='Server Load (%)',
            color='Region',
            color_discrete_sequence=px.colors.qualitative.Dark2
        )
        fig_box.update_layout(
            margin=dict(l=0, r=0, t=20, b=0), 
            height=350, 
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_box, use_container_width=True)

    st.markdown("---")

    # ------------------
    # Data Table functionality
    # ------------------
    st.subheader("Detailed Data Explorer")
    with st.expander("View raw data and extract reports", expanded=False):
        st.dataframe(filtered_df, use_container_width=True, height=250)
        
        # Download button for CSV
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Data as CSV",
            data=csv,
            file_name='dashboard_export.csv',
            mime='text/csv',
        )