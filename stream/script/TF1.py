import os
import requests
import re
import time
import random
import cloudscraper
from urllib.parse import urlparse

class StreamExtractor:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper()
        self.retry_delay = 3
        self.max_retries = 5
        
    def rotate_headers(self):
        """Génère des headers aléatoires pour chaque requête"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
            "Mozilla/5.0 (Linux; Android 10; SM-G980F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
        ]
        
        return {
            "User-Agent": random.choice(user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "fr-FR,fr;q=0.5",
            "Referer": "https://www.google.com/",
            "DNT": "1",
            "Upgrade-Insecure-Requests": "1"
        }

    def stealth_request(self, url):
        """Effectue une requête furtive avec contournement Cloudflare"""
        for attempt in range(self.max_retries):
            try:
                self.scraper.headers.update(self.rotate_headers())
                response = self.scraper.get(url, timeout=15)
                
                if response.status_code == 403:
                    raise requests.HTTPError("403 Forbidden")
                
                if "cloudflare" in response.text.lower():
                    print("⚠️ Protection Cloudflare détectée - Nouvelle tentative...")
                    raise Exception("Cloudflare challenge")
                
                return response.text
                
            except Exception as e:
                print(f"⏳ Tentative {attempt + 1} échouée: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
        
        return None

    def extract_m3u8(self, html):
        """Extrait les URLs M3U8 avec analyse approfondie"""
        # Recherche dans les balises video
        video_tags = re.findall(r'<video[^>]*>(.*?)</video>', html, re.DOTALL)
        for tag in video_tags:
            sources = re.findall(r'src=["\'](https?://[^"\']+\.m3u8[^"\']*)["\']', tag)
            if sources:
                return sources[0]
        
        # Recherche dans les configurations JS
        js_configs = re.findall(r'(?:videojs|player)\(.*?\).setup\(({.*?})\);', html)
        for config in js_configs:
            try:
                config_data = json.loads(config.replace("'", '"'))
                if 'sources' in config_data:
                    for source in config_data['sources']:
                        if source.get('type') == 'application/x-mpegURL':
                            return source['src']
            except:
                continue
                
        return None

if __name__ == "__main__":
    extractor = StreamExtractor()
    target_url = "https://www.stream4free.tv/tf1-live-streaming"
    output_path = "stream/tf1.m3u8"
    
    print("🔍 Lancement de l'extraction furtive...")
    html = extractor.stealth_request(target_url)
    
    if html:
        print("✅ HTML récupéré avec succès")
        m3u8_url = extractor.extract_m3u8(html)
        
        if m3u8_url:
            print(f"🎯 URL M3U8 trouvée: {m3u8_url}")
            os.makedirs("streams", exist_ok=True)
            with open(output_path, "w") as f:
                f.write("#EXTM3U\n#EXT-X-VERSION:3\n")
                f.write(f"{m3u8_url}\n")
            print(f"💾 Fichier sauvegardé: {output_path}")
        else:
            print("❌ Aucune URL M3U8 trouvée dans le code source")
    else:
        print("❌ Échec de la récupération après plusieurs tentatives")
