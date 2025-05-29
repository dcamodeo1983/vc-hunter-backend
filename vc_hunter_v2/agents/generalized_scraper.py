
import os
import json
import requests
from bs4 import BeautifulSoup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
def scrape_site(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"⚠️ Failed to scrape: {url} (status {response.status_code})")
            log_failed(url)
            return None
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text(separator=" ", strip=True)[:10000]
    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
        log_failed(url)
        return None

def log_failed(url):
    os.makedirs("data", exist_ok=True)
    with open("data/failed_scrapes.txt", "a") as f:
        f.write(url + "\n")

def save_jsonl(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj) + "\n")

def process_vc(vc):
    vc_name = vc["name"]
    vc_url = vc["url"]
    portfolio_urls = vc.get("portfolio_urls", [])

    print(f"🔍 Scraping VC: {vc_name} - {vc_url}")
    content = scrape_site(vc_url)
    if content:
        save_jsonl(f"data/raw/vcs/{vc_name}.jsonl", {"url": vc_url, "type": "vc", "content": content})

    for p_url in portfolio_urls:
        p_content = scrape_site(p_url)
        domain = p_url.split("//")[-1].split("/")[0]
        if p_content:
            save_jsonl(f"data/raw/portfolio/{domain}.jsonl", {"url": p_url, "type": "portfolio", "content": p_content})

def load_input_vcs():
    with open("data/vc_input.json", "r") as f:
        return json.load(f)

if __name__ == "__main__":
    vcs = load_input_vcs()
    for vc in vcs:
        process_vc(vc)
