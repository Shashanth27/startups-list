import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import os
from typing import List, Dict

async def scrape_startups(start_page: int, end_page: int) -> pd.DataFrame:
    """
    Scrape startup information from the Startup India website using Playwright.
    """
    startup_list = []
    seen_startups = set()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        for current_page in range(start_page, end_page + 1):
            try:
                url = f"https://www.startupindia.gov.in/content/sih/en/search.html?roles=Startup&page={current_page}"
                await page.goto(url, wait_until="networkidle")
                
                # Wait for startup elements to load
                await page.wait_for_selector(".events-details", timeout=10000)
                
                # Extract startup information
                startups = await page.query_selector_all(".events-details")
                
                for startup in startups:
                    name = await startup.query_selector("h3")
                    name_text = await name.text_content() if name else "N/A"
                    
                    if name_text in seen_startups:
                        continue
                        
                    stage = await startup.query_selector(".highlighted-text")
                    stage_text = await stage.text_content() if stage else "N/A"
                    
                    location = await startup.query_selector("li.location")
                    location_spans = await location.query_selector_all("span") if location else []
                    location_parts = []
                    for span in location_spans:
                        text = await span.text_content()
                        if text:
                            location_parts.append(text.strip())
                    location_text = ", ".join(location_parts) if location_parts else "N/A"
                    
                    startup_list.append({
                        "Name": name_text.strip(),
                        "Stage": stage_text.strip(),
                        "Location": location_text
                    })
                    seen_startups.add(name_text)
                    
            except Exception as e:
                print(f"Error on page {current_page}: {e}")
                continue
                
        await browser.close()
    
    return pd.DataFrame(startup_list)

def save_data(data: pd.DataFrame, output_folder: str = "output") -> str:
    """
    Save scraped data to a CSV file.
    """
    if data.empty:
        return ""
        
    os.makedirs(output_folder, exist_ok=True)
    existing_files = [f for f in os.listdir(output_folder) if f.startswith("startups")]
    file_num = len(existing_files)
    
    csv_path = os.path.join(output_folder, f"startups({file_num}).csv")
    data.to_csv(csv_path, index=False)
    return csv_path