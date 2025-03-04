import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from dotenv import load_dotenv
import os

# Explicitly specify the .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

load_dotenv(dotenv_path)

# Get the credentials from .env
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message):
    """Send a message to Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram-tunnukset puuttuvat.")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    response = requests.post(url, data=payload)
    return response.json()  # Debugging output

def check_product_availability(album_name, url):
    """Check if a product is available on the website."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com",
    }

    try:
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            print(f"❌ Virhe nettisivun lataamisessa albumille {album_name}. Status: {response.status_code}")
            return False

        soup = BeautifulSoup(response.text, "html.parser")

        # Tarkistetaan saatavuus
        button = soup.find("button", class_="button", string="Ei saatavilla")

        if button:
            print(f"❌ Albumi {album_name} ei ole saatavilla Rolling Recordista.")
            return False
        else:
            message = f"✅ Albumi {album_name} on saatavilla Rolling Recordista!\n🔗 Linkki: {url}"
            print(message)
            send_telegram_message(message)
            return True

    except requests.exceptions.RequestException as e:
        print(f"❌ Virhe nettisivun lataamisessa albumille {album_name}: {e}")
        return False

if __name__ == "__main__":
    excel_file = "levylista.xlsx"  # Excel muotoinen levylista
    
    try:
        df = pd.read_excel(excel_file, usecols=[0, 1], header=None)  # Luetaan kaksi saraketta
        for index, row in df.iterrows():
            album_name, product_url = row[0], row[1]
            check_product_availability(album_name, product_url)
    except FileNotFoundError:
        print("❌ Levylistaa ei löytynyt.")
    except Exception as e:
        print(f"❌ Virhe levylistan lukemisessa: {e}")
