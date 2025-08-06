import requests
from bs4 import BeautifulSoup
import re

# Étape 1 : Récupérer le HTML
url = "https://piratetv.pro/sport-tv-2/"
headers = {
    "User-Agent": "Mozilla/5.0"
}
response = requests.get(url, headers=headers)
html = response.text

# Étape 2 : Chercher un lien .m3u8 dans le HTML
m3u8_matches = re.findall(r'(https?://[^\s\'"]+\.m3u8)', html)

if m3u8_matches:
    m3u8_url = m3u8_matches[0]
    print("Lien M3U8 trouvé :", m3u8_url)

    # Étape 3 : Créer un fichier m3u8 de redirection
    with open("nouveau.m3u8", "w") as f:
        f.write("#EXTM3U\n")
        f.write("#EXT-X-STREAM-INF:BANDWIDTH=800000,RESOLUTION=1280x720\n")
        f.write(m3u8_url + "\n")
else:
    print("Aucun lien M3U8 trouvé.")
  
