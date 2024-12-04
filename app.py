import streamlit as st
from scraper import scrape_startups, save_data
import pandas as pd

# Streamlit UI
st.title("Startup India Scraper")
st.write("This app scrapes startup data from the Startup India website.")

# Input fields for start and end page
start_page = st.number_input("Start Page", min_value=0, value=0, step=1)
end_page = st.number_input("End Page", min_value=0, value=1, step=1)

# Output folder
output_folder = "output"  # Adjust this path as needed

if st.button("Scrape"):
    if start_page > end_page:
        st.error("Start page cannot be greater than end page!")
    else:
        st.write(f"Scraping startups from page {start_page} to {end_page}...")
        
        # Scrape data
        data = scrape_startups(start_page, end_page)
        if not data.empty:
            st.success(f"Scraped {len(data)} startups!")
            st.write(data)

            # Save data
            csv_path = save_data(data, output_folder)
            st.success(f"Data saved to `{csv_path}`")

            # Provide CSV download link
            st.download_button(
                label="Download CSV",
                data=data.to_csv(index=False),
                file_name="startups.csv",
                mime="text/csv"
            )
        else:
            st.error("No startups found. Try again with different pages.")
