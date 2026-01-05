import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Set page config
st.set_page_config(
    page_title="Operations Overview | Portfolio Demo",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data
@st.cache_data
def load_data():
    data_dir = "data"
    resources_df = pd.read_csv(os.path.join(data_dir, 'resources.csv'))
    delays_df = pd.read_csv(os.path.join(data_dir, 'delays.csv'))
    
    # ensure date columns are datetime
    resources_df['Start Date'] = pd.to_datetime(resources_df['Start Date'])
    resources_df['End Date'] = pd.to_datetime(resources_df['End Date'])
    delays_df['Expected Arrival'] = pd.to_datetime(delays_df['Expected Arrival'])
    delays_df['Actual Arrival'] = pd.to_datetime(delays_df['Actual Arrival'])
    
    return resources_df, delays_df

try:
    resources_df, delays_df = load_data()
except FileNotFoundError:
    st.error("Data files not found. Please run 'generate_data.py' first.")
    st.stop()

# Sidebar
with st.sidebar:
    st.title("Filters")
    
    # Global Date Filter (mock functionality for demo)
    date_range = st.date_input("Date Range", [])
    
    st.markdown("---")
    st.info("**Portfolio Demo**\n\nThis dashboard demonstrates data visualization skills using Python & Streamlit.")

st.title("Operations & Logistics Dashboard")
st.markdown("Real-time visibility into resource utilization and supply chain risks.")

# Tabs
tab1, tab2 = st.tabs(["👥 Resource Allocation", "🚚 Delay Anticipation"])

with tab1:
    st.header("Resource Utilization Overview")
    
    # Key Metrics
    total_resources = len(resources_df)
    active_resources = len(resources_df[resources_df['Status'] == 'Active'])
    avg_utilization = resources_df['Utilization (%)'].mean()
    overutilized = len(resources_df[resources_df['Utilization (%)'] > 100])
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Consultants", total_resources)
    col2.metric("Active Now", active_resources, delta=f"{active_resources/total_resources:.0%}")
    col3.metric("Avg Utilization", f"{avg_utilization:.1f}%", delta="-2%" if avg_utilization > 85 else "OK")
    col4.metric("Overutilized (>100%)", overutilized, delta_color="inverse")
    
    st.markdown("### Utilization by Department")
    
    # Prepare data for charts
    dept_stats = resources_df.groupby('Department')['Utilization (%)'].mean().reset_index()
    
    # Bar Chart
    fig_bar = px.bar(dept_stats, x='Department', y='Utilization (%)', 
                     color='Utilization (%)', title="Average Load per Department",
                     color_continuous_scale='Blues')
    st.plotly_chart(fig_bar, use_container_width=True)
    
    st.markdown("### Resource Details")
    st.dataframe(resources_df, use_container_width=True)

with tab2:
    st.header("Supply Chain Delay Intelligence")
    
    # Key Metrics
    total_shipments = len(delays_df)
    # Status "On Time" or "Scheduled" vs others
    on_time_count = len(delays_df[delays_df['Status'].isin(['On Time', 'Scheduled'])])
    on_time_rate = (on_time_count / total_shipments) * 100
    avg_delay = delays_df[delays_df['Delay Days'] > 0]['Delay Days'].mean()
    high_risk_count = len(delays_df[delays_df['Risk Score'] > 80])
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Shipments", total_shipments)
    col2.metric("On-Time Rate", f"{on_time_rate:.1f}%", delta="-5%" if on_time_rate < 90 else "+2%")
    col3.metric("Avg Delay (Days)", f"{avg_delay:.1f}" if pd.notnull(avg_delay) else "0")
    col4.metric("High Risk Shipments", high_risk_count, delta_color="inverse")
    
    # Delay Reason Breakdown
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Primary Causes of Delay")
        reasons = delays_df[delays_df['Status'] == 'Delayed']['Primary Delay Reason'].value_counts().reset_index()
        fig_pie = px.pie(reasons, values='count', names='Primary Delay Reason', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col_chart2:
        st.subheader("Expected vs Actual Timeline")
        # Filter only completed (where we have actual arrival)
        completed_df = delays_df.dropna(subset=['Actual Arrival'])
        fig_scatter = px.scatter(completed_df, x='Expected Arrival', y='Actual Arrival', 
                                 color='Status', hover_data=['Shipment ID', 'Origin'],
                                 title="Delivery Performance Analysis")
        # Add 1:1 line
        fig_scatter.add_shape(type="line",
            line=dict(dash="dash"),
            x0=completed_df['Expected Arrival'].min(), y0=completed_df['Actual Arrival'].min(),
            x1=completed_df['Expected Arrival'].max(), y1=completed_df['Actual Arrival'].max()
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    st.markdown("### Upcoming High Risk Delay Predictions")
    # Show items that are 'At Risk' or have high risk scores
    risk_df = delays_df[delays_df['Risk Score'] > 50].sort_values(by='Risk Score', ascending=False)
    
    def color_risk(val):
        color = 'red' if val > 80 else 'orange' if val > 50 else 'green'
        return f'color: {color}'

    st.dataframe(
        risk_df[['Shipment ID', 'Origin', 'Destination', 'Expected Arrival', 'Status', 'Risk Score', 'Primary Delay Reason']]
        .style.map(color_risk, subset=['Risk Score']),
        use_container_width=True
    )
    
# Footer
st.markdown("---")
st.caption("Built by Yassir Ghlalou for Upwork Portfolio Demo")
