import requests
from bs4 import BeautifulSoup
import pandas as pd

def check_product_availability(album_name, url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com",
    }

    try:
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            print(f"Virhe nettisivun lataamisessa albumille  {album_name}. Status: {response.status_code}")
            return False

        soup = BeautifulSoup(response.text, "html.parser")

        # Tarkistetaan saatavuus
        button = soup.find("button", class_="button", string="Ei saatavilla")

        if button:
            print(f"❌ Albumi {album_name} ei ole saatavilla Rolling Recordista.")
            return False
        else:
            print(f"✅ Albumi {album_name} on saatavilla Rolling Recordista!")
            return True

    except requests.exceptions.RequestException as e:
        print(f"Virhe nettisivun lataamisessa albumille {album_name}: {e}")
        return False

if __name__ == "__main__":
    excel_file = "levylista.xlsx"  # Excel muotoinen levylista
    
    try:
        df = pd.read_excel(excel_file, usecols=[0, 1], header=None)  # Luetaan kaksi kolumnia, joista toinen on levyn URL ja toinen on nimi 
        for index, row in df.iterrows():
            album_name, product_url = row[0], row[1]
            check_product_availability(album_name, product_url)
    except FileNotFoundError:
        print("Levylistaa ei löytynyt.")
    except Exception as e:
        print(f"Virhe levylistan {e}", " lukemisessa")