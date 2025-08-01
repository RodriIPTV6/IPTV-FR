import requests
import os
import re

SOURCE_URL = "https://raw.githubusercontent.com/schumijo/iptv/main/playlists/mytf1/tf1.m3u8"
OUTPUT_PATH = "stream/tf1.m3u8"

def extract_and_clean():
    try:
        # Téléchargement du fichier
        response = requests.get(SOURCE_URL, timeout=10)
        response.raise_for_status()
        
        # Extraction de la 7ème ligne (index 6 en Python)
        lines = response.text.splitlines()
        if len(lines) >= 7:
            # Modification spécifique pour supprimer _1 seulement dans index_1.m3u8
            stream_url = re.sub(r'(index)_1(\.m3u8)$', r'\1\2', lines[6])
            
            # Création du dossier et écriture
            os.makedirs("streams", exist_ok=True)
            with open(OUTPUT_PATH, "w") as f:
                f.write("#EXTM3U\n")
                f.write("#EXT-X-VERSION:3\n")
                f.write(stream_url + "\n")
            
            print(f"✅ Fichier généré avec succès : {OUTPUT_PATH}")
            print(f"🔗 URL finale : {stream_url}")  # Pour vérification
            return True
            
        raise ValueError("Le fichier source n'a pas le format attendu")
        
    except Exception as e:
        print(f"❌ Erreur : {str(e)}")
        return False

if __name__ == "__main__":
    if not extract_and_clean():
        exit(1)
