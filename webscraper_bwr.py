import os
import requests
import time
import re
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

def normalize_name(name):
    """Normalize album names by removing unnecessary words and special characters."""
    name = name.lower()
    name = re.sub(r"\b(lp|2-lp|vinyl|reissue|special edition|deluxe|limited)\b", "", name)  # Remove common suffixes
    name = re.sub(r"[^a-z0-9 ]", "", name)  # Remove special characters
    return name.strip()

def search_artist(artist, album, found_albums):
    """Search for an artist and check if the album exists in search results (LP format only)."""
    base_url = "https://blackandwhite.fi/fi/index.php?fc=module&module=iqitsearch&controller=searchiqit&id_lang=4&search_query="
    search_url = f"{base_url}{artist.replace(' ', '+')}&formaatti=lp"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com",
    }
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"❌ Failed to search for {artist}. Status Code: {response.status_code}")
            return
        
        soup = BeautifulSoup(response.text, "html.parser")
        album_elements = soup.select("h2.h3.product-title a")
        
        for album_element in album_elements:
            album_text = album_element.get_text(strip=True)
            if ":" in album_text:
                scraped_album = album_text.split(":", 1)[1].strip()  # Extract part after ':'
            else:
                scraped_album = album_text  # Fallback if ':' is missing
            
            scraped_album = normalize_name(scraped_album)
            formatted_album = normalize_name(album)
            
            if formatted_album == scraped_album:
                message = f"✅ Album '{album}' by '{artist}' is available at Black and White Records!\nLink: {search_url}"
                print(message)
                send_telegram_message(message)
                found_albums.add((artist, album))
                return  # Stop checking once found
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Error searching for {artist}: {e}")

def main():
    start_time = time.time()
    
    excel_file = "levylista_bw.xlsx"  # Album list Excel file
    try:
        df = pd.read_excel(excel_file, usecols=[0, 1], header=None, names=["Artist", "Album"])  # Read two columns
        album_list = [tuple(row) for row in df.dropna().values.tolist()]  # Convert to list of (Artist, Album) tuples
        
        searched_albums = set(album_list)  # Track all albums searched
        found_albums = set()  # Track albums that were found
        
        # Search for each artist and check for the album (LP format only)
        for artist, album in album_list:
            search_artist(artist, album, found_albums)
        
        # Determine which albums were not found
        not_found_albums = searched_albums - found_albums
        for artist, album in not_found_albums:
            print(f"❌ Album '{album}' by '{artist}' was not found in Black and White Records.")
    
    except FileNotFoundError:
        print("❌ Album list not found.")
    except Exception as e:
        print(f"❌ Error processing album list: {e}")
    
    end_time = time.time()
    print(f"⏱️ Runtime: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()