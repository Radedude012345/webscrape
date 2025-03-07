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
    """Lähetä viesti Telegramiin."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram-kirjautumistiedot puuttuvat.")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, data=payload)

def normalize_name(name):
    """Normalisoi albumien nimet poistamalla turhat sanat ja erikoismerkit."""
    name = name.lower()
    name = re.sub(r"\b(lp|2-lp|vinyl|reissue|special edition|deluxe|limited)\b", "", name)  # Poista yleiset suffiksit
    name = re.sub(r"[^a-z0-9 ]", "", name)  # Poista erikoismerkit
    return name.strip()

def search_artist(artist, album, found_albums):
    """Hakee artistia ja tarkistaa, onko albumi saatavilla hakutuloksissa (vain LP-formaatti)."""
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
            print(f"❌ Haku epäonnistui artistille {artist}. Statuskoodi: {response.status_code}")
            return
        
        soup = BeautifulSoup(response.text, "html.parser")
        album_elements = soup.select("h2.h3.product-title a")
        
        for album_element in album_elements:
            album_text = album_element.get_text(strip=True)
            if ":" in album_text:
                scraped_album = album_text.split(":", 1)[1].strip()  # Ota osa ':' jälkeen
            else:
                scraped_album = album_text  # Varmuuskopio jos ':' puuttuu
            
            scraped_album = normalize_name(scraped_album)
            formatted_album = normalize_name(album)
            
            if formatted_album == scraped_album:
                message = f"✅ Albumi '{album}' artistilta '{artist}' on saatavilla Black and White Recordsissa!\nLinkki: {search_url}"
                print(message)
                send_telegram_message(message)
                found_albums.add((artist, album))
                return  # Lopeta tarkistus, kun albumi löytyy
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Virhe haettaessa artistia {artist}: {e}")

def main():
    start_time = time.time()
    
    excel_file = "levylista_bw.xlsx"  # Excel-tiedosto, jossa albumilista
    try:
        df = pd.read_excel(excel_file, usecols=[0, 1], header=None, names=["Artist", "Album"])  # Lue kaksi saraketta
        album_list = [tuple(row) for row in df.dropna().values.tolist()]  # Muunna lista (Artist, Album) -pareiksi
        
        searched_albums = set(album_list)  # Seurataan kaikkia haettuja albumeita
        found_albums = set()  # Seurataan löydettyjä albumeita
        
        # Etsi jokainen artisti ja tarkista albumi (vain LP-formaatti)
        for artist, album in album_list:
            search_artist(artist, album, found_albums)
        
        # Tarkista, mitkä albumit eivät löytyneet
        not_found_albums = searched_albums - found_albums
        for artist, album in not_found_albums:
            print(f"❌ Albumia '{album}' artistilta '{artist}' ei löytynyt Black and White Recordsista.")
    
    except FileNotFoundError:
        print("❌ Albumilistaa ei löydetty.")
    except Exception as e:
        print(f"❌ Virhe käsiteltäessä albumilistaa: {e}")
    
    end_time = time.time()
    print(f"⏱️ Suoritusaika: {end_time - start_time:.2f} sekuntia")

if __name__ == "__main__":
    main()