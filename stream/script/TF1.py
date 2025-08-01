import requests
import os

SOURCE_URL = "https://raw.githubusercontent.com/schumijo/iptv/refs/heads/main/playlists/mytf1/tf1.m3u8"
OUTPUT_DIR = "stream"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "tf1.m3u8")

def sync_m3u8():
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        response = requests.get(SOURCE_URL, timeout=10)
        response.raise_for_status()
        
        # Écriture directe sans ligne supplémentaire
        with open(OUTPUT_FILE, "w") as f:
            f.write(response.text)  # Écrit seulement le contenu original
        
        print(f"✅ Fichier synchronisé : {OUTPUT_FILE}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur : {str(e)}")
        return False

if __name__ == "__main__":
    if not sync_m3u8():
        exit(1)
