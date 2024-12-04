import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import pandas as pd
import os

# Global WebDriver instance (so it doesn't open multiple browsers)
driver = None

def initialize_driver():
    """
    Initialize the Chrome WebDriver in headless mode.
    """
    global driver
    if driver is None:
        options = Options()
        options.headless = True  # Run in headless mode for Streamlit hosting
        driver = webdriver.Chrome(options=options)

def scrape_startups(start_page, end_page):
    """
    Scrape startup information from the Startup India website using Selenium.
    
    Parameters:
    - start_page: The starting page number to scrape.
    - end_page: The ending page number to scrape.

    Returns:
    - A pandas DataFrame containing the scraped startup data.
    """
    initialize_driver()  # Initialize driver only once

    base_url = "https://www.startupindia.gov.in/content/sih/en/search.html?roles=Startup&page="
    startup_list = []
    seen_startups = set()  # Set to track unique startups by a combination of 'name' and 'location'

    for page in range(start_page, end_page + 1):
        print(f"🔍 Scraping page {page}...")
        url = base_url + str(page)
        
        # Load the page
        driver.get(url)

        # Wait for the elements to load (adjust timeout if needed)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "events-details"))
            )
        except TimeoutException:
            print(f"⚠️ Timeout while waiting for page {page}.")
            driver.save_screenshot(f"screenshot_page_{page}.png")  # Save screenshot for debugging
            continue
        
        time.sleep(5)  # Allow extra time for dynamic content to load

        # Grab the page source after rendering
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Locate all startup entries
        startups = soup.find_all('div', class_='events-details')

        if not startups:
            print(f"⚠️ No startups found on page {page}.")
            continue

        for startup in startups:
            try:
                print(f"📜 Scraping startup...")

                # Extract startup name
                name = startup.find('h3').text.strip()
                print(f"✅ Name is scraped: {name}")

                # Extract startup stage
                stage = startup.find('span', class_='highlighted-text').text.strip()
                print(f"✅ Stage is scraped: {stage}")

                # Extract location details
                location_spans = startup.find('li', class_='location').find_all('span')
                location = ', '.join([span.text.strip() for span in location_spans])
                print(f"✅ Location is scraped: {location}")

                # Check if the startup is already seen (by its unique combination)
                unique_identifier = (name, location)
                if unique_identifier in seen_startups:
                    print(f"⚠️ Duplicate found: {name}, skipping.")
                    continue

                # Add to the seen set and append to the startup list
                seen_startups.add(unique_identifier)
                startup_list.append({
                    "Name": name,
                    "Stage": stage,
                    "Location": location
                })

            except AttributeError as e:
                print(f"⚠️ Skipping a startup due to missing data: {e}")
                continue

    return pd.DataFrame(startup_list)

def save_data(data, output_folder="output"):
    """
    Save scraped data to a CSV file.

    Parameters:
    - data: A pandas DataFrame containing the scraped data.
    - output_folder: The folder where the CSV file will be saved.
    """
    os.makedirs(output_folder, exist_ok=True)

    # Split data into smaller parts and save them to separate CSV files
    num_files = (len(data) // 50) + 1  # Create multiple files with 50 records each
    for i in range(num_files):
        start_index = i * 50
        end_index = (i + 1) * 50
        chunk = data.iloc[start_index:end_index]
        
        # Save each chunk as a separate CSV file
        csv_path = os.path.join(output_folder, f"startups_{i}.csv")
        chunk.to_csv(csv_path, index=False)
        print(f"✅ Data saved to {csv_path}")

    return os.path.join(output_folder, "startups_*.csv")

def close_driver():
    """
    Close the WebDriver instance.
    """
    global driver
    if driver:
        driver.quit()
        driver = None
        print("✅ WebDriver closed.")

# Example usage within Streamlit
if __name__ == "__main__":
    start_page = 1
    end_page = 5  # Modify the number of pages you want to scrape
    startups_data = scrape_startups(start_page, end_page)
    save_data(startups_data)
    close_driver()  # Ensure that the driver is closed after scraping is done
