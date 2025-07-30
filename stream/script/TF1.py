import re
import requests
import os
from urllib.parse import urlparse

def extract_m3u8_from_html(html):
    """Extrait les URLs M3U8 du code HTML"""
    patterns = [
        r'<source\s+src=["\'](https?://[^"\']+\.m3u8[^"\']*)["\']',
        r'videojs\(.*?\)\.setup\(.*?"sources"\s*:\s*\[(.*?)\]',
        r'var\s+streamUrl\s*=\s*["\'](https?://[^"\']+\.m3u8[^"\']*)["\']'
    ]
    
    found_urls = []
    for pattern in patterns:
        matches = re.findall(pattern, html, re.DOTALL)
        found_urls.extend(matches)
    
    # Nettoyage des URLs
    clean_urls = []
    for url in found_urls:
        if 'm3u8' in url:
            # Supprime les paramètres inutiles
            clean_url = url.split('?')[0] if '?' in url else url
            clean_urls.append(clean_url)
    
    return list(set(clean_urls))  # Supprime les doublons

def get_valid_m3u8(urls):
    """Teste les URLs et retourne la première valide"""
    for url in urls:
        try:
            response = requests.head(url, timeout=5)
            if response.status_code == 200:
                return url
        except:
            continue
    return None

def main():
    target_url = "https://www.stream4free.tv/tf1-live-streaming"
    output_dir = "stream"
    output_file = os.path.join(output_dir, "tf1.m3u8")
    
    try:
        # Récupération du HTML
        response = requests.get(target_url, timeout=10)
        response.raise_for_status()
        
        # Extraction des URLs M3U8
        m3u8_urls = extract_m3u8_from_html(response.text)
        
        if not m3u8_urls:
            print("❌ Aucune URL M3U8 trouvée dans le code source")
            exit(1)
        
        # Sélection de la meilleure URL
        best_url = get_valid_m3u8(m3u8_urls) or m3u8_urls[0]
        
        # Création du fichier M3U8
        os.makedirs(output_dir, exist_ok=True)
        with open(output_file, "w") as f:
            f.write("#EXTM3U\n")
            f.write("#EXT-X-VERSION:3\n")
            f.write(f"{best_url}\n")
        
        print(f"✅ Fichier M3U8 généré avec succès: {output_file}")
        print(f"🔗 URL du flux: {best_url}")
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
