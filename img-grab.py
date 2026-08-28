import os
import sys
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

def get_search_query_name(url):
    """Extracts a clean folder name from a search URL or domain."""
    parsed = urlparse(url)
    if "google" in parsed.netloc:
        query = parse_qs(parsed.query).get('q', ['search_results'])[0]
        return re.sub(r'[^a-zA-Z0-9]', '_', query).lower()
    return re.sub(r'[^a-zA-Z0-9]', '_', parsed.netloc).lower()

def scrape_images(url, limit=25):
    print(f"[+] Fetching images from: {url}")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"[-] Error fetching URL: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    img_urls = []

    for img in soup.find_all('img'):
        src = img.get('src') or img.get('data-src') or img.get('data-original')
        if src:
            if src.startswith('//'):
                src = 'https:' + src
            elif src.startswith('/'):
                base_match = re.match(r'(https?://[^/]+)', url)
                if base_match:
                    src = base_match.group(1) + src
            
            if src.startswith('http') and src not in img_urls:
                img_urls.append(src)
                if len(img_urls) >= limit:
                    break

    return img_urls

def download_and_create_gallery(url, limit=25):
    folder_name = get_search_query_name(url)
    os.makedirs(folder_name, exist_ok=True)
    
    img_urls = scrape_images(url, limit)
    if not img_urls:
        print("[-] No valid images found to download.")
        return

    saved_files = []
    print(f"[+] Downloading images into folder: {folder_name}/")
    
    for i, link in enumerate(img_urls):
        try:
            img_data = requests.get(link, headers={"User-Agent": "Mozilla/5.0"}, timeout=5).content
            ext = link.split('.')[-1].split('?')[0]
            if ext not in ['jpg', 'jpeg', 'png', 'webp']:
                ext = 'jpg'
            
            filename = f"image_{i+1}.{ext}"
            filepath = os.path.join(folder_name, filename)
            
            with open(filepath, 'wb') as handler:
                handler.write(img_data)
            saved_files.append(filename)
            print(f"[{i+1}] Downloaded")
        except Exception:
            print(f"[-] Failed to download image {i+1}")

    # Auto-generate local slide/gallery HTML inside the folder
    html_path = os.path.join(folder_name, "index.html")
    with open(html_path, "w") as f:
        f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gallery: {folder_name}</title>
    <style>
        body {{ font-family: sans-serif; background: #121212; color: #fff; text-align: center; margin: 0; padding: 20px; }}
        h1 {{ text-transform: capitalize; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; max-width: 1000px; margin: 0 auto; }}
        .card {{ background: #1e1e1e; padding: 10px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
        img {{ width: 100%; height: 200px; object-fit: cover; border-radius: 4px; }}
    </style>
</head>
<body>
    <h1>Search Result: {folder_name}</h1>
    <div class="grid">
""")
        for file in saved_files:
            f.write(f'        <div class="card"><img src="{file}" alt="Saved Image"></div>\n')
        f.write("""    </div>
</body>
</html>""")

    print(f"\n[+] Success! Local slide viewer created.")
    print(f"[+] Run server and open: http://localhost:8080/{folder_name}/index.html")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 image_scraper.py <URL>")
        sys.exit(1)
    
    download_and_create_gallery(sys.argv[1], limit=25)
