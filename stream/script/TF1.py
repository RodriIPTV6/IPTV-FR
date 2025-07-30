import os
import requests
import re
import time
import random

# Configuration anti-blocage
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.stream4free.tv/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.5",
    "DNT": "1",  # Do Not Track
}

PROXY_URL = "http://" + os.getenv("PROXY_KEY") + ":@proxy.zenrows.com:8001" if os.getenv("PROXY_KEY") else None

def fetch_with_retry(url, max_retries=3):
    session = requests.Session()
    for attempt in range(max_retries):
        try:
            # Rotation des headers et délai aléatoire
            current_headers = HEADERS.copy()
            current_headers["User-Agent"] = f"Mozilla/5.0 ({random.choice(['Windows', 'Macintosh', 'Linux'])}) AppleWebKit/{random.randint(500, 600)}.36"
            
            response = session.get(
                url,
                headers=current_headers,
                proxies={"http": PROXY_URL, "https": PROXY_URL} if PROXY_URL else None,
                timeout=15
            )
            
            if response.status_code == 403:
                raise requests.HTTPError("403 Forbidden")
                
            response.raise_for_status()
            return response.text
            
        except Exception as e:
            print(f"⚠️ Tentative {attempt + 1} échouée : {str(e)}")
            time.sleep(2 ** attempt)  # Backoff exponentiel
    
    return None

def extract_m3u8(html):
    # Détection multi-méthodes
    patterns = [
        r'(https?:\/\/[^\s"\']+\.m3u8\b[^\s"\']*)',  # URL directe
        r'player\.setup\({\s*file:\s*["\']([^"\']+\.m3u8)',  # JWPlayer
        r'var\s+streamUrl\s*=\s*["\']([^"\']+\.m3u8)'  # Variables JS
    ]
    
    for pattern in patterns:
        match = re.search(pattern, html)
        if match:
            return match.group(1)
    return None

if __name__ == "__main__":
    TARGET_URL = "https://www.stream4free.tv/tf1-live-streaming"
    OUTPUT_DIR = "streams"
    OUTPUT_FILE = os.path.join(OUTPUT_DIR, "tf1.m3u8")
    
    print("🔍 Lancement de l'extraction...")
    html = fetch_with_retry(TARGET_URL)
    
    if html:
        m3u8_url = extract_m3u8(html)
        if m3u8_url:
            print(f"✅ Lien extrait : {m3u8_url}")
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            with open(OUTPUT_FILE, "w") as f:
                f.write(f"#EXTM3U\n#EXT-X-VERSION:3\n{m3u8_url}")
            print("💾 Fichier M3U8 généré avec succès")
            exit(0)
    
    print("❌ Échec critique : Impossible de contourner les protections")
    exit(1)
