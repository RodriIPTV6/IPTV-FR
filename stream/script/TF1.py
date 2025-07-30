import os
import re
import requests
import time
import json
from urllib.parse import urljoin

# Configuration du header dynamique
def get_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.stream4free.tv/",
        "X-Requested-With": "XMLHttpRequest"  # Important pour les requêtes AJAX
    }

def extract_videojs_config(html):
    """Extrait la configuration Video.js depuis le code JavaScript"""
    pattern = r'videojs\(.*?\).setup\(({.*?})\);'
    match = re.search(pattern, html, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).replace("'", '"'))
        except json.JSONDecodeError:
            pass
    return None

def get_m3u8_url():
    url = "https://www.stream4free.tv/tf1-live-streaming"
    
    try:
        # Première requête pour obtenir le HTML
        response = requests.get(url, headers=get_headers(), timeout=10)
        response.raise_for_status()
        
        # Analyse de la configuration Video.js
        config = extract_videojs_config(response.text)
        if config and 'sources' in config:
            for source in config['sources']:
                if source.get('type') == 'application/x-mpegURL':
                    return source['src']
        
        # Fallback: Recherche alternative
        m3u8_matches = re.findall(r'(https?://[^\s"\']+\.m3u8)', response.text)
        if m3u8_matches:
            return m3u8_matches[0]
            
    except Exception as e:
        print(f"Erreur: {e}")
    
    return None

if __name__ == "__main__":
    m3u8_url = get_m3u8_url()
    if m3u8_url:
        print(f"Lien M3U8 trouvé: {m3u8_url}")
        os.makedirs("streams", exist_ok=True)
        with open("streams/tf1.m3u8", "w") as f:
            f.write("#EXTM3U\n")
            f.write("#EXT-X-VERSION:3\n")
            f.write(f"{m3u8_url}\n")
    else:
        print("Aucun lien M3U8 trouvé")
        exit(1)
