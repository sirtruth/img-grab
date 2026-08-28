import os
import sys
import re
import requests
from bs4 import BeautifulSoup

def scrape_images(url, limit=25):
    print(f"[+] Fetching images from: {url}")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"[-] Error fetching URL: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    img_urls = []

    # Find all <img> tags and extract 'src' or 'data-src'
    for img in soup.find_all('img'):
        src = img.get('src') or img.get('data-src')
        if src:
            # Handle relative links if necessary
            if src.startswith('//'):
                src = 'https:' + src
            elif src.startswith('/'):
                # Basic absolute path resolution
                base_match = re.match(r'(https?://[^/]+)', url)
                if base_match:
                    src = base_match.group(1) + src
            
            if src.startswith('http') and src not in img_urls:
                img_urls.append(src)
                if len(img_urls) >= limit:
                    break

    return img_urls

def save_to_python(img_urls, filename="saved_images.py"):
    with open(filename, "w") as f:
        f.write("# Auto-generated image link collection\n")
        f.write("SAVED_IMAGES = [\n")
        for link in img_urls:
            f.write(f"    \"{link}\",\n")
        f.write("]\n")
    print(f"[+] Successfully saved {len(img_urls)} links to {filename}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 image_scraper.py <URL>")
        sys.exit(1)
    
    target_url = sys.argv[1]
    urls = scrape_images(target_url, limit=25)
    if urls:
        save_to_python(urls)
    else:
        print("[-] No images found on the target page.")
