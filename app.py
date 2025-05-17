import streamlit as st
import asyncio
from scraper import scrape_startups, save_data
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Startup India Scraper",
    page_icon="🚀",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        margin-top: 1rem;
    }
    .stats-container {
        padding: 1rem;
        background-color: #f0f2f6;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.title("🚀 Startup India Scraper")
st.markdown("""
    This application scrapes startup data from the Startup India website and provides insights about the startup ecosystem.
""")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    start_page = st.number_input("Start Page", min_value=0, value=0, step=1)
    end_page = st.number_input("End Page", min_value=0, value=1, step=1)
    
    if st.button("🔍 Start Scraping", key="scrape_button"):
        if start_page > end_page:
            st.error("⚠️ Start page cannot be greater than end page!")
        else:
            with st.spinner(f"Scraping pages {start_page} to {end_page}..."):
                # Run the scraper
                data = asyncio.run(scrape_startups(start_page, end_page))
                
                if not data.empty:
                    # Save data
                    csv_path = save_data(data)
                    st.success(f"✅ Successfully scraped {len(data)} startups!")
                    
                    # Store data in session state for visualization
                    st.session_state.data = data
                    st.session_state.csv_path = csv_path
                else:
                    st.error("❌ No startups found. Try different page numbers.")

# Main content
if 'data' in st.session_state and not st.session_state.data.empty:
    data = st.session_state.data
    
    # Display statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Startups", len(data))
    with col2:
        st.metric("Unique Locations", data['Location'].nunique())
    with col3:
        st.metric("Unique Stages", data['Stage'].nunique())
    
    # Visualizations
    st.subheader("📊 Data Analysis")
    
    # Stage distribution
    stage_dist = data['Stage'].value_counts()
    fig_stage = px.pie(
        values=stage_dist.values,
        names=stage_dist.index,
        title="Startup Stage Distribution"
    )
    st.plotly_chart(fig_stage)
    
    # Location distribution (top 10)
    location_dist = data['Location'].value_counts().head(10)
    fig_location = px.bar(
        x=location_dist.index,
        y=location_dist.values,
        title="Top 10 Startup Locations",
        labels={'x': 'Location', 'y': 'Count'}
    )
    st.plotly_chart(fig_location)
    
    # Raw data table
    st.subheader("📋 Raw Data")
    st.dataframe(data)
    
    # Download button
    st.download_button(
        label="⬇️ Download CSV",
        data=data.to_csv(index=False),
        file_name="startups.csv",
        mime="text/csv"
    )