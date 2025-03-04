# Levyjen Saatavuuden Tarkistin

Tämä Python-skripti tarkistaa, ovatko tietyt levyt saatavilla Rolling Records -verkkokaupasta. Se lukee levyjen nimet ja URL-osoitteet **Excel-tiedostosta (`levylista.xlsx`)** ja tarkistaa saatavuuden verkkosivulta.

## 🔧 Asennus

1. **Asenna vaaditut kirjastot**:
   ```sh
   pip install requests beautifulsoup4 pandas openpyxl
   ```

2. **Varmista, että sinulla on `levylista.xlsx` oikeassa muodossa**:
   - Ensimmäinen sarake: **Levyn nimi**
   - Toinen sarake: **Levyn URL**

## 🚀 Käyttö

1. Lisää levyt `levylista.xlsx`-tiedostoon oikeassa muodossa.
2. Suorita skripti:
   ```sh
   python webscraper.py
   ```
3. Skripti tarkistaa jokaisen levyn saatavuuden ja tulostaa:
   - *Albumi X on saatavilla Rolling Recordista!*
   - ❌ *Albumi X ei ole saatavilla Rolling Recordista.*

##  Huomioitavaa
- Varmista, että `levylista.xlsx` ei sisällä tyhjiä rivejä tai otsikoita.
- Jos verkkosivusto muuttaa rakennettaan, `button`-elementin valinta voi tarvita päivitystä.

## 🛠 Tulevia Parannuksia
-  **Telegram-ilmoitukset, kun levy tulee saataville**
-  **Tulosten tallennus tiedostoon tai tietokantaan**
-  **Useamman verkkokaupan tuki**

 **Tekijä:** Tämä projekti on tarkoitettu henkilökohtaiseen käyttöön ja oppimiseen. 

