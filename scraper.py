import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import os
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Global WebDriver instance (so it doesn't open multiple browsers)
driver = None

def initialize_driver():
    """
    Initialize the Chrome WebDriver with necessary configurations for the current environment.
    """
    global driver
    if driver is None:
        try:
            options = Options()
            options.headless = False  # Set to True for headless mode
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")

            # Use WebDriver Manager to automatically handle ChromeDriver
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            print("✅ WebDriver initialized successfully.")
        except Exception as e:
            print(f"⚠️ Error initializing WebDriver: {e}")
            driver = None  # Set driver to None in case of error

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

    if driver is None:
        print("⚠️ Driver initialization failed. Exiting scraping.")
        return pd.DataFrame()  # Return empty dataframe if driver initialization fails

    base_url = "https://www.startupindia.gov.in/content/sih/en/search.html?roles=Startup&page="
    startup_list = []
    seen_startups = set()  # Set to track unique startups (using name as unique identifier)

    for page in range(start_page, end_page + 1):
        print(f"🔍 Scraping page {page}...")
        url = base_url + str(page)

        try:
            # Load the page
            driver.get(url)

            # Wait for the elements to load (adjust timeout if needed)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "events-details"))
            )

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

                    # Skip if the startup has already been seen
                    if name in seen_startups:
                        print(f"⚠️ Duplicate startup found: {name}. Skipping...")
                        continue

                    # Extract startup stage
                    stage = startup.find('span', class_='highlighted-text').text.strip()
                    print(f"✅ Stage is scraped: {stage}")

                    # Extract location details
                    location_spans = startup.find('li', class_='location').find_all('span')
                    location = ', '.join([span.text.strip() for span in location_spans])
                    print(f"✅ Location is scraped: {location}")

                    # Append the startup data to the list
                    startup_list.append({
                        "Name": name,
                        "Stage": stage,
                        "Location": location
                    })

                    # Mark this startup as seen
                    seen_startups.add(name)

                except AttributeError as e:
                    print(f"⚠️ Skipping a startup due to missing data: {e}")
                    continue

        except Exception as e:
            print(f"⚠️ Error on page {page}: {e}")
            continue  # Proceed to the next page even if one page fails

    return pd.DataFrame(startup_list)


def save_data(data, output_folder="output"):
    """
    Save scraped data to a CSV file.

    Parameters:
    - data: A pandas DataFrame containing the scraped data.
    - output_folder: The folder where the CSV file will be saved.
    """
    if data.empty:
        print("⚠️ No data to save.")
        return

    os.makedirs(output_folder, exist_ok=True)
    
    # Check for existing files and find the correct file name
    existing_files = [f for f in os.listdir(output_folder) if f.startswith("startups")]
    file_num = len(existing_files)  # Find the number of existing files to append the correct number
    
    # Save the new data with a unique filename
    csv_path = os.path.join(output_folder, f"startups({file_num}).csv")
    data.to_csv(csv_path, index=False)
    print(f"✅ Data saved to {csv_path}")
    return csv_path


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
    end_page = 25  # Modify the number of pages you want to scrape
    startups_data = scrape_startups(start_page, end_page)
    save_data(startups_data)
    close_driver()  # Ensure that the driver is closed after scraping is done
