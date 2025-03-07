import os
import requests
import time
from bs4 import BeautifulSoup
import pandas as pd
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message):
    """Send a message to Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials missing.")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, data=payload)

def scrape_albums(base_url, page_limit, album_list, found_albums):
    """Scrapes the given website for album availability."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com",
    }
    
    for page in range(1, page_limit + 1):
        url = f"{base_url}?page={page}"
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            
            # Find all album elements (Filtering only relevant links)
            album_elements = soup.select("a[href*='/fi/kaeytetyt-vinyylit/'], a[href*='/fi/uudet-vinyylit/']")
            
            page_albums = set()
            for album in album_elements:
                album_name = album.get_text(strip=True)
                if album_name and ":" in album_name:  # Ensuring it's a valid album format
                    page_albums.add(album_name.lower())
            
            # Check if any albums in our list exist on this page
            for album in album_list:
                formatted_album = album.lower().strip()
                if any(formatted_album in found_album for found_album in page_albums):
                    message = f"✅ Album '{album}' is available at Black and White Records!\nLink: {url}"
                    print(message)
                    send_telegram_message(message)
                    found_albums.add(album)  # Track found albums
            
            # Stop searching if all albums have been found
            if len(found_albums) == len(album_list):
                break
        
        except requests.exceptions.RequestException:
            continue

def main():
    start_time = time.time()
    
    excel_file = "levylista_bw.xlsx"  # Album list Excel file
    new_records_url = "https://blackandwhite.fi/fi/22-uudet-vinyylit"
    used_records_url = "https://blackandwhite.fi/fi/23-kaeytetyt-vinyylit"
    page_limit = 10

    try:
        df = pd.read_excel(excel_file, usecols=[0], header=None)  # Read first column only
        album_list = df[0].dropna().tolist()  # Convert to list and remove NaN values
        
        searched_albums = set(album_list)  # Track all albums searched
        found_albums = set()  # Track albums that were found
        
        # Scrape both new and used records
        scrape_albums(new_records_url, page_limit, album_list, found_albums)
        scrape_albums(used_records_url, page_limit, album_list, found_albums)
        
        # Determine which albums were not found
        not_found_albums = searched_albums - found_albums
        for album in not_found_albums:
            print(f"❌ Album '{album}' was not found in Black and White Records.")

    except FileNotFoundError:
        print("❌ Album list not found.")
    except Exception:
        pass
    
    end_time = time.time()
    print(f"Runtime: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()