import requests
import os
from datetime import datetime

SOURCE_URL = "https://raw.githubusercontent.com/schumijo/iptv/refs/heads/main/playlists/mytf1/tf1.m3u8"
OUTPUT_DIR = "stream"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "tf1.m3u8")

def sync_m3u8():
    try:
        # Création du dossier si inexistant
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Téléchargement du fichier source
        response = requests.get(SOURCE_URL, timeout=10)
        response.raise_for_status()
        
        # Sauvegarde avec timestamp
        with open(OUTPUT_FILE, "w") as f:
            f.write(f"# Last Updated: {datetime.utcnow().isoformat()}\n")
            f.write(response.text)
        
        print(f"✅ Fichier synchronisé avec succès : {OUTPUT_FILE}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la synchronisation : {str(e)}")
        return False

if __name__ == "__main__":
    if not sync_m3u8():
        exit(1)
