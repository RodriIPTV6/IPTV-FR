import requests
import re

def fetch_m3u8_from_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Recherche du lien M3U8 dans le code source ou les requêtes réseau simulées
        m3u8_urls = re.findall(r'https?://[^\s"\']+\.m3u8', response.text)
        return m3u8_urls[0] if m3u8_urls else None
    except Exception as e:
        print(f"❌ Erreur lors de la récupération : {e}")
        return None

def generate_proper_m3u8(m3u8_url, output_file="output.m3u8"):
    try:
        # Télécharge le contenu du M3U8 principal
        response = requests.get(m3u8_url, timeout=10)
        response.raise_for_status()
        m3u8_content = response.text

        # Formatage du M3U8 pour qu'il soit lisible
        formatted_m3u8 = "#EXTM3U\n"
        formatted_m3u8 += "#EXT-X-VERSION:3\n"
        formatted_m3u8 += "#EXT-X-STREAM-INF:BANDWIDTH=2000000,RESOLUTION=1280x720\n"
        formatted_m3u8 += m3u8_url + "\n"  # Utilise le lien direct ou ajuste selon besoin

        # Sauvegarde dans un fichier
        with open(output_file, "w") as f:
            f.write(formatted_m3u8)
        
        print(f"✅ Fichier M3U8 généré : {output_file}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la génération du M3U8 : {e}")
        return False

if __name__ == "__main__":
    STREAM_URL = "https://www.stream4free.tv/tf1-live-streaming"
    OUTPUT_DIR = "stream"
    OUTPUT_FILE = os.path.join(OUTPUT_DIR, "tf1.m3u8")  # Chemin complet
    
    print("🔍 Recherche du lien M3U8...")
    m3u8_link = fetch_m3u8_from_page(STREAM_URL)
    
    if m3u8_link:
        print(f"📡 Lien M3U8 trouvé : {m3u8_link}")
        success = generate_proper_m3u8(m3u8_link, OUTPUT_FILE)
        if success:
            print("🎉 Terminé avec succès !")
        else:
            print("⚠️ Échec de la génération du M3U8.")
    else:
        print("❌ Aucun lien M3U8 trouvé.")
