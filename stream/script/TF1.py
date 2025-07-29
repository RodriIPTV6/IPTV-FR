import os  # ⚠️ Import manquant !
import requests
from bs4 import BeautifulSoup
import re

def fetch_m3u8_from_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        m3u8_urls = re.findall(r'https?://[^\s"\']+\.m3u8', response.text)
        return m3u8_urls[0] if m3u8_urls else None
    except Exception as e:
        print(f"❌ Erreur lors de la récupération du M3U8 : {e}")
        return None

def generate_proper_m3u8(m3u8_url, output_path):
    """Génère un fichier M3U8 valide."""
    try:
        response = requests.get(m3u8_url, timeout=10)
        response.raise_for_status()
        
        with open(output_path, "w") as f:
            f.write("#EXTM3U\n")
            f.write("#EXT-X-VERSION:3\n")
            f.write("#EXT-X-STREAM-INF:BANDWIDTH=2000000,RESOLUTION=1280x720\n")
            f.write(f"{m3u8_url}\n")
        print(f"✅ Fichier M3U8 mis à jour : {output_path}")
    except Exception as e:
        print(f"❌ Erreur lors de l'écriture du fichier : {e}")

if __name__ == "__main__":
    STREAM_URL = "https://endirecttv.com/tf1-direct/"
    OUTPUT_DIR = "stream"  # Dossier existant
    OUTPUT_FILE = os.path.join(OUTPUT_DIR, "tf1.m3u8")  # Chemin complet

    # Vérifie que le dossier existe (optionnel, si vous êtes sûr qu'il existe)
    if not os.path.exists(OUTPUT_DIR):
        print(f"⚠️ Le dossier '{OUTPUT_DIR}' n'existe pas. Création...")
        os.makedirs(OUTPUT_DIR, exist_ok=True)  # Crée le dossier si absent

    print("🔍 Recherche du lien M3U8...")
    m3u8_link = fetch_m3u8_from_page(STREAM_URL)
    
    if m3u8_link:
        print(f"📡 Lien M3U8 trouvé : {m3u8_link}")
        generate_proper_m3u8(m3u8_link, OUTPUT_FILE)
    else:
        print("❌ Aucun lien M3U8 valide trouvé.")
