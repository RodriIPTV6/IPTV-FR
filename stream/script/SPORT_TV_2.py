import os
import re
import time
import cloudscraper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_scraper():
    """Configure le scraper avec des paramètres anti-détection"""
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True,
            'mobile': False
        }
    )
    return scraper

def extract_with_selenium(url):
    """Utilise Selenium pour contourner les protections JavaScript"""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    
    try:
        # Attendre que le player soit chargé
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, 'video'))
        
        # Extraire les sources vidéo
        html = driver.page_source
        m3u8_urls = re.findall(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', html)
        
        return m3u8_urls[0] if m3u8_urls else None
        
    finally:
        driver.quit()

def save_m3u8(content, filename="streams/sporttv.m3u8"):
    os.makedirs("streams", exist_ok=True)
    with open(filename, "w") as f:
        f.write("#EXTM3U\n")
        f.write("#EXT-X-VERSION:3\n")
        f.write(content + "\n")

if __name__ == "__main__":
    TARGET_URL = "https://piratetv.pro/sport-tv-2/"
    
    print("🔍 Début de l'extraction...")
    
    # Essayer d'abord avec cloudscraper
    scraper = setup_scraper()
    try:
        response = scraper.get(TARGET_URL, timeout=15)
        if "cloudflare" in response.text.lower():
            raise Exception("Protection Cloudflare détectée")
        
        m3u8_url = re.search(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', response.text)
        if m3u8_url:
            save_m3u8(m3u8_url.group(0))
            print("✅ Flux trouvé via cloudscraper")
            exit(0)
    except Exception as e:
        print(f"⚠️ Erreur cloudscraper: {str(e)}")
    
    # Fallback sur Selenium si échec
    print("🔄 Tentative avec Selenium...")
    try:
        m3u8_url = extract_with_selenium(TARGET_URL)
        if m3u8_url:
            save_m3u8(m3u8_url)
            print("✅ Flux trouvé via Selenium")
        else:
            print("❌ Aucun flux M3U8 trouvé")
            exit(1)
    except Exception as e:
        print(f"❌ Échec critique: {str(e)}")
        exit(1)
