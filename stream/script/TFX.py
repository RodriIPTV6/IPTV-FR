import requests
import os

SOURCE_M3U = "https://raw.githubusercontent.com/Paradise-91/ParaTV/refs/heads/main/playlists/paratv/main/paratv.m3u"
OUTPUT_FILE = "stream/tfx.m3u8"

def download_and_process():
    try:
        # Étape 1: Télécharger le fichier .m3u source
        response = requests.get(SOURCE_M3U, timeout=10)
        response.raise_for_status()
        lines = response.text.splitlines()
        
        # Vérifier qu'on a au moins 6 lignes
        if len(lines) < 42:
            raise ValueError("Le fichier source ne contient pas 6 lignes")
        # Étape 2: Extraire l'URL de la 6ème ligne
        m3u8_url = lines[41].strip()
        print(f"🔗 URL trouvée: {m3u8_url}")

        # Étape 3: Télécharger le contenu du fichier M3U8
        m3u8_response = requests.get(m3u8_url, timeout=15)
        m3u8_response.raise_for_status()
        
        # Étape 4: Sauvegarder le contenu brut
        os.makedirs("stream", exist_ok=True)
        with open(OUTPUT_FILE, "w") as f:
            f.write(m3u8_response.text)
        
        print(f"✅ Fichier sauvegardé: {OUTPUT_FILE}")
        return True

    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

if __name__ == "__main__":
    if not download_and_process():
        exit(1)
