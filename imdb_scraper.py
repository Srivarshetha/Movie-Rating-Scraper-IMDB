from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

url = "https://www.imdb.com/chart/top/"

options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) "
                     "Chrome/118.0.5993.90 Safari/537.36")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(url)

print("🌐 Loading IMDb Top 250 page in headless mode...")
time.sleep(5)

try:
    # Scroll down fully to load all movies
    for _ in range(5):
        driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
        time.sleep(2)

    WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, 'li.ipc-metadata-list-summary-item')
        )
    )

    movies = driver.find_elements(By.CSS_SELECTOR, 'li.ipc-metadata-list-summary-item')
    print(f"✅ Found {len(movies)} movies on the page")

    data = []
    for idx, movie in enumerate(movies, start=1):
        # --- Movie title ---
        try:
            title_elem = movie.find_element(By.CSS_SELECTOR, 'h3.ipc-title__text')
            title_full = title_elem.text.strip()
            if '.' in title_full:
                rank, title = title_full.split('.', 1)
                title = title.strip()
            else:
                rank = str(idx)
                title = title_full
        except:
            rank, title = str(idx), "N/A"

        # --- Year ---
        try:
            year = movie.find_element(By.CSS_SELECTOR, 'span.cli-title-metadata-item:nth-of-type(1)').text
        except:
            year = "N/A"

        # --- Rating ---
        try:
            rating_elem = movie.find_element(By.CSS_SELECTOR, 'span.ipc-rating-star--rating')
            rating_value = rating_elem.text.strip()
            # Add the ⭐ emoji
            rating = rating_value + " ⭐"
        except:
            rating = "N/A"

        data.append({
            "Rank": rank,
            "Title": title,
            "Year": year,
            "Rating": rating
        })

    # --- Save to CSV ---
    df = pd.DataFrame(data)
    df.to_csv("imdb_top_250.csv", index=False, encoding="utf-8-sig")  # utf-8-sig keeps emoji visible
    print(f"🎬 Scraping complete! Saved {len(df)} movies to imdb_top_250.csv")

except Exception as e:
    print("⚠ Could not load movie data properly.")
    print("Error:", e)

finally:
    driver.quit()
