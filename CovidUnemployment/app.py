import streamlit as st 
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="India Unemployment Dashboard", layout="wide")

# 2. Robust Data Loading
@st.cache_data
def load_data():
    try:
        df1 = pd.read_csv("Unemployment in India.csv")
        df2 = pd.read_csv("Unemployment_Rate_upto_11_2020.csv")

        # Clean df1
        df1.columns = df1.columns.str.strip()
        df1 = df1.dropna()
        df1['Date'] = pd.to_datetime(df1['Date'], dayfirst=True)

        # Clean df2
        df2.columns = df2.columns.str.strip()
        df2 = df2.dropna()
        df2['Date'] = pd.to_datetime(df2['Date'], dayfirst=True)
        
        return df1, df2
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), pd.DataFrame()

df_area, df_reg = load_data()

# Check if data loaded successfully
if df_reg.empty or df_area.empty:
    st.error("Could not load data. Please ensure the CSV files are in the same folder as this script.")
    st.stop()

# 3. Sidebar Filters
st.sidebar.header("Global Filters")
min_date = df_reg['Date'].min().to_pydatetime()
max_date = df_reg['Date'].max().to_pydatetime()

date_range = st.sidebar.slider("Select Date Range", min_date, max_date, (min_date, max_date))

# Filter logic
filter_df_reg = df_reg[(df_reg['Date'] >= date_range[0]) & (df_reg['Date'] <= date_range[1])]
filter_df_area = df_area[(df_area['Date'] >= date_range[0]) & (df_area['Date'] <= date_range[1])]

# 4. Main UI
st.title("📊 Unemployment Analysis Dashboard: India")
st.markdown("Analyzing the impact of COVID-19 and regional trends in the Indian labor market.")

tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Unemployment Trends", 
    "🗺️ State Comparison", 
    "🔍 Regional Analysis", 
    "🧪 What-If Analysis"
])

# --- TAB 1: Trends ---
with tab1:
    st.header("National Unemployment Trends")
    if not filter_df_reg.empty:
        trend_data = filter_df_reg.groupby('Date')['Estimated Unemployment Rate (%)'].mean().reset_index()
        
        fig_trend = px.line(trend_data, x='Date', y='Estimated Unemployment Rate (%)', 
                            title="Average Unemployment Rate Over Time",
                            markers=True, line_shape="spline", color_discrete_sequence=['#EF553B'])
        
        lockdown_date = "2020-03-24"
        fig_trend.add_vline(x=lockdown_date, line_dash="dash", line_color="red")
     
        fig_trend.add_annotation(x=lockdown_date, y=max(trend_data['Estimated Unemployment Rate (%)']),
                                 text="Lockdown Start", showarrow=True, arrowhead=1)
        
        st.plotly_chart(fig_trend, use_container_width=True)
        st.info("The sharp peak in April-May 2020 highlights the immediate impact of the nationwide lockdown.")
    else:
        st.warning("No data available for the selected date range.")

with tab2:
    st.header("Compare States Side-by-Side")
    all_states = sorted(df_reg['Region'].unique())
    selected_states = st.multiselect("Select States to Compare", all_states, default=all_states[:3])
    
    if selected_states and not filter_df_reg.empty:
        compare_df = filter_df_reg[filter_df_reg['Region'].isin(selected_states)]
        if not compare_df.empty:
            fig_compare = px.line(compare_df, x='Date', y='Estimated Unemployment Rate (%)', color='Region',
                                  title="Unemployment Rate Comparison", markers=True)
            st.plotly_chart(fig_compare, use_container_width=True)
            
            avg_comp = compare_df.groupby('Region')['Estimated Unemployment Rate (%)'].mean().sort_values().reset_index()
            fig_bar_comp = px.bar(avg_comp, x='Estimated Unemployment Rate (%)', y='Region', orientation='h',
                                  title="Average Rate in Selected States", color='Region')
            st.plotly_chart(fig_bar_comp, use_container_width=True)
        else:
            st.warning("No data found for selected states in this date range.")
    else:
        st.info("Please select states to view comparison.")

# --- TAB 3: Regional Analysis ---
with tab3:
    col1, col2 = st.columns(2)
    with col1:
        if not filter_df_area.empty:
            st.subheader("Rural vs Urban Split")
            fig_area = px.box(filter_df_area, x='Area', y='Estimated Unemployment Rate (%)', color='Area',
                              title="Distribution: Rural vs Urban")
            st.plotly_chart(fig_area, use_container_width=True)
    
    with col2:
        if not filter_df_reg.empty:
            st.subheader("Regional Hierarchy")
            fig_sun = px.sunburst(filter_df_reg, path=['Region.1', 'Region'], values='Estimated Unemployment Rate (%)',
                                  title="Unemployment by Macro-Region")
            st.plotly_chart(fig_sun, use_container_width=True)

# --- TAB 4: What-If Analysis ---
with tab4:
    st.header("Hypothetical 'What-If' Scenario")
    target_state = st.selectbox("Select a State for Analysis", all_states)
    
    state_data = df_reg[df_reg['Region'] == target_state]
    avg_lp = state_data['Estimated Labour Participation Rate (%)'].mean()
    avg_ur = state_data['Estimated Unemployment Rate (%)'].mean()
    
    st.write(f"**Current Average for {target_state}:**")
    st.write(f"Labour Participation: {avg_lp:.2f}% | Unemployment: {avg_ur:.2f}%")
    
    st.divider()
    lp_change = st.slider("Simulate change in Labour Participation (%)", -20.0, 20.0, 0.0)
    
    simulated_ur = max(0, avg_ur - (lp_change * 0.45))
    
    c1, c2 = st.columns(2)
    c1.metric("New Participation Rate", f"{avg_lp + lp_change:.2f}%", f"{lp_change}%")
    c2.metric("Simulated Unemployment Rate", f"{simulated_ur:.2f}%", f"{simulated_ur - avg_ur:.2f}%", delta_color="inverse")

st.markdown("---")
st.caption("Data Source: India Unemployment Dataset | Final Stable Build")