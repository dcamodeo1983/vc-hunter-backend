
import os
import json
import random
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from tqdm import tqdm

class VCScraperAgent:
    def __init__(self, vc_urls, output_dir="data/raw", sample_size=10):
        self.vc_urls = vc_urls
        self.output_dir = output_dir
        self.sample_size = sample_size
        os.makedirs(output_dir, exist_ok=True)

    def clean_html(self, html):
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return soup.get_text(separator="\n")

    def fetch_page(self, url):
        try:
            response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            return self.clean_html(response.text)
        except Exception as e:
            print(f"[ERROR] Failed to fetch {url}: {e}")
            return ""

    def discover_portfolio_links(self, homepage_html, base_url):
        soup = BeautifulSoup(homepage_html, "html.parser")
        links = []
        for a in soup.find_all("a", href=True):
            href = a['href']
            text = a.get_text().lower()
            if any(k in href.lower() or k in text for k in ["portfolio", "companies", "investments"]):
                full_url = href if href.startswith("http") else base_url + href
                links.append(full_url)
        return list(set(links))

    def extract_company_links(self, portfolio_page):
        soup = BeautifulSoup(portfolio_page, "html.parser")
        company_links = set()
        for a in soup.find_all("a", href=True):
            href = a['href']
            if href.startswith("http") and not any(s in href for s in ["linkedin", "twitter"]):
                company_links.add(href)
        return list(company_links)

    def scrape_company_shallow(self, url):
        html = self.fetch_page(url)
        soup = BeautifulSoup(html, "html.parser")
        meta = soup.find("meta", attrs={"name": "description"})
        description = meta["content"] if meta and "content" in meta.attrs else ""
        return {
            "company_url": url,
            "description": description,
            "raw_text": html[:1500]
        }

    def save_jsonl(self, filename, records):
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")

    def run(self):
        all_records = []

        for vc_url in tqdm(self.vc_urls, desc="Scraping VC websites"):
            base_domain = urlparse(vc_url).netloc.replace(".", "_")

            vc_home_html = self.fetch_page(vc_url)
            if not vc_home_html:
                continue

            all_records.append({
                "source": vc_url,
                "type": "vc_thesis",
                "content": vc_home_html
            })

            portfolio_links = self.discover_portfolio_links(vc_home_html, vc_url)
            if not portfolio_links:
                continue

            for portfolio_url in portfolio_links:
                portfolio_page = self.fetch_page(portfolio_url)
                company_urls = self.extract_company_links(portfolio_page)
                sampled = random.sample(company_urls, min(self.sample_size, len(company_urls)))

                for company_url in sampled:
                    data = self.scrape_company_shallow(company_url)
                    all_records.append({
                        "source": vc_url,
                        "type": "portfolio_shallow",
                        "company_url": company_url,
                        "content": data["description"] or data["raw_text"]
                    })

        self.save_jsonl("vc_scraped_data.jsonl", all_records)
        print(f"✅ Finished. Saved {len(all_records)} records to {self.output_dir}/vc_scraped_data.jsonl")
