
import requests
from bs4 import BeautifulSoup
import json
import os

VISITED_DOMAINS = set()
RELATIONSHIPS = {
    "vc_to_companies": {},
    "company_to_vcs": {}
}

def scrape_site(url, depth=1):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"⚠️ Failed to scrape: {url}")
            return None
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
        return text[:10000]  # Trim long content
    except Exception as e:
        print(f"❌ Error scraping {url}: {str(e)}")
        return None

def process_vc(vc_entry):
    vc_name = vc_entry["name"]
    vc_url = vc_entry["url"]
    portfolio_urls = vc_entry.get("portfolio_urls", [])
    print(f"🔍 Scraping VC: {vc_name} - {vc_url}")
    
    content = scrape_site(vc_url)
    if content:
        save_jsonl(f"data/raw/vcs/{vc_name}.jsonl", {"url": vc_url, "type": "vc", "content": content})
    
    RELATIONSHIPS["vc_to_companies"][vc_name] = []

    for p_url in portfolio_urls:
        domain = p_url.split("//")[-1].split("/")[0]
        if domain not in VISITED_DOMAINS:
            VISITED_DOMAINS.add(domain)
            p_content = scrape_site(p_url)
            if p_content:
                save_jsonl(f"data/raw/portfolio/{domain}.jsonl", {"url": p_url, "type": "portfolio", "content": p_content})
        RELATIONSHIPS["vc_to_companies"][vc_name].append(domain)
        RELATIONSHIPS["company_to_vcs"].setdefault(domain, []).append(vc_name)

def save_jsonl(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj) + "\n")

def save_relationships():
    with open("data/relationships/vc_to_companies.json", "w") as f:
        json.dump(RELATIONSHIPS["vc_to_companies"], f, indent=2)
    with open("data/relationships/company_to_vcs.json", "w") as f:
        json.dump(RELATIONSHIPS["company_to_vcs"], f, indent=2)

if __name__ == "__main__":
    with open("data/vc_input.json", "r") as f:
        vcs = json.load(f)
        for vc in vcs:
            process_vc(vc)
    save_relationships()
