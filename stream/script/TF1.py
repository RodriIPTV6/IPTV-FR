# update_m3u8.py
import requests
import re
import os
import time

CONFIG = {
    "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "REFERER": "https://www.stream4free.tv/",
    "RETRY_DELAY": 5,
    "MAX_RETRIES": 3
}

def fetch_with_retries(url):
    session = requests.Session()
    session.headers.update({
        "User-Agent": CONFIG["USER_AGENT"],
        "Referer": CONFIG["REFERER"],
        "Accept-Language": "fr-FR,fr;q=0.9",
    })
    
    for attempt in range(CONFIG["MAX_RETRIES"]):
        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()
            
            # Détection Cloudflare
            if "cloudflare" in response.text.lower():
                raise Exception("Protection Cloudflare détectée")
                
            return response.text
            
        except Exception as e:
            print(f"⚠️ Tentative {attempt + 1} échouée : {str(e)}")
            if attempt < CONFIG["MAX_RETRIES"] - 1:
                time.sleep(CONFIG["RETRY_DELAY"])
    
    return None

def extract_m3u8(html):
    # Nouvelle regex avancée
    patterns = [
        r'(https?://[^\s"\']+\.m3u8(?:\?[^\s"\']+)?)',  # URL directe
        r'src:\s*["\']([^"\']+\.m3u8)',  # Sources JS
        r'fetch\("([^"]+\.m3u8)'  # Requêtes AJAX
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, html)
        if matches:
            return matches[0]
    return None

if __name__ == "__main__":
    target_url = "https://www.stream4free.tv/tf1-live-streaming"
    output_path = "streams/tf1.m3u8"
    
    print("🔍 Début de l'extraction...")
    html_content = fetch_with_retries(target_url)
    
    if html_content:
        m3u8_url = extract_m3u8(html_content)
        if m3u8_url:
            print(f"✅ Lien M3U8 trouvé : {m3u8_url}")
            os.makedirs("streams", exist_ok=True)
            with open(output_path, "w") as f:
                f.write(f"#EXTM3U\n#EXT-X-VERSION:3\n{m3u8_url}")
            print("💾 Fichier sauvegardé avec succès")
        else:
            print("❌ Aucun lien M3U8 trouvé dans le code source")
    else:
        print("❌ Échec de la récupération après plusieurs tentatives")
