import os
import re
import time
import random
import cloudscraper
from urllib.parse import urljoin

class UltimateStreamExtractor:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True,
                'mobile': False
            }
        )
        self.retry_pattern = [3, 5, 8, 13]  # Backoff fibonacci

    def _generate_headers(self):
        """Génère des headers réalistes avec empreinte navigateur"""
        browsers = [
            {'chrome': '120.0.0.0', 'webkit': '537.36', 'os': 'Windows NT 10.0'},
            {'chrome': '119.0.6045', 'webkit': '537.36', 'os': 'Macintosh'},
            {'chrome': '120.0.0.0', 'webkit': '537.36', 'os': 'Linux'}
        ]
        browser = random.choice(browsers)
        
        return {
            'User-Agent': f'Mozilla/5.0 ({browser["os"]}) AppleWebKit/{browser["webkit"]} (KHTML, like Gecko) Chrome/{browser["chrome"]} Safari/{browser["webkit"]}',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9',
            'Referer': random.choice([
                'https://www.google.com/',
                'https://www.facebook.com/',
                'https://twitter.com/'
            ]),
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1'
        }

    def _extract_with_retry(self, url):
        """Tentative intelligente avec rotation d'empreinte"""
        for i, delay in enumerate(self.retry_pattern):
            try:
                self.scraper.headers = self._generate_headers()
                response = self.scraper.get(url, timeout=20)
                
                if response.status_code == 403:
                    raise Exception(f"403 Forbidden (attempt {i+1})")
                
                if response.status_code == 200:
                    if "access denied" in response.text.lower():
                        raise Exception("Blockpage detected")
                    return response.text
                
            except Exception as e:
                print(f"⚠️ Attempt {i+1} failed: {str(e)}")
                if i < len(self.retry_pattern) - 1:
                    sleep_time = delay + random.uniform(0, 2)
                    print(f"⏳ Waiting {sleep_time:.1f}s...")
                    time.sleep(sleep_time)
        
        return None

    def _find_hidden_m3u8(self, html):
        """Recherche avancée avec analyse DOM virtuel"""
        # Méthode 1: Extraction directe
        direct_sources = re.findall(
            r'src=["\'](https?://[^"\']+\.m3u8(?:\?[^"\']+)?)["\']',
            html,
            re.IGNORECASE
        )
        
        # Méthode 2: Décodage JSON
        json_matches = re.findall(
            r'(?s)\bsources\s*:\s*(\[[^\]]+\])',
            html
        )
        for match in json_matches:
            try:
                sources = json.loads(match.replace("'", '"'))
                for source in sources:
                    if isinstance(source, dict) and source.get('type') == 'application/x-mpegURL':
                        return source['src']
            except:
                continue
                
        return direct_sources[0] if direct_sources else None

    def get_stream(self, url):
        """Processus complet d'extraction"""
        print("🔍 Starting advanced extraction...")
        html = self._extract_with_retry(url)
        
        if not html:
            print("❌ Failed to bypass protections")
            return None
            
        print("✅ Successfully retrieved page content")
        m3u8_url = self._find_hidden_m3u8(html)
        
        if not m3u8_url:
            print("⚠️ No M3U8 found in initial scan - Trying fallback methods...")
            # Méthode alternative: recherche dans les scripts
            scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
            for script in scripts:
                matches = re.search(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', script)
                if matches:
                    m3u8_url = matches.group(1)
                    break
        
        return m3u8_url

if __name__ == "__main__":
    extractor = UltimateStreamExtractor()
    target_url = "https://www.stream4free.tv/tf1-live-streaming"
    
    m3u8_url = extractor.get_stream(target_url)
    
    if m3u8_url:
        print(f"🎯 Found stream URL: {m3u8_url}")
        os.makedirs("streams", exist_ok=True)
        with open("streams/tf1.m3u8", "w") as f:
            f.write("#EXTM3U\n")
            f.write("#EXT-X-VERSION:3\n")
            f.write(f"{m3u8_url}\n")
        print("💾 Stream file saved successfully")
    else:
        print("❌ Critical failure - Could not extract stream")
        exit(1)
