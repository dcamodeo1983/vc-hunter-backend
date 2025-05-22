# vc_scraper_agent_playwright.py

import os
import json
import random
from urllib.parse import urlparse
from tqdm import tqdm
from playwright.sync_api import sync_playwright

class VCScraperAgent:
    def __init__(self, vc_urls, output_dir="vc-hunter-v2/data/raw/vcs", sample_size=10):
        self.vc_urls = vc_urls
        self.output_dir = output_dir
        self.sample_size = sample_size
        os.makedirs(output_dir, exist_ok=True)

    def clean_html(self, html):
        import re
        clean_text = re.sub(r"<(script|style|footer|nav).*?>.*?</\1>", "", html, flags=re.DOTALL | re.IGNORECASE)
        clean_text = re.sub(r"<[^>]+>", "", clean_text)
        return clean_text.strip()

    def extract_company_links(self, html):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        links = set()
        for a in soup.find_all("a", href=True):
            href = a['href']
            if href.startswith("http") and not any(s in href for s in ["linkedin", "twitter", "mailto", "javascript"]):
                links.add(href)
        return list(links)

    def scrape_company_page(self, page, url):
        try:
            page.goto(url, timeout=10000)
            content = page.content()
            return {
                "company_url": url,
                "content": self.clean_html(content)[:2000]  # shallow-medium scrape
            }
        except Exception as e:
            print(f"[ERROR] Failed scraping portfolio page: {url} — {e}")
            return {
                "company_url": url,
                "content": ""
            }

    def run(self):
        all_records = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            for vc_url in tqdm(self.vc_urls, desc="Scraping VC websites"):
                print(f"🔍 Visiting {vc_url}")
                try:
                    page.goto(vc_url, timeout=15000)
                    homepage_html = page.content()
                    all_records.append({
                        "source": vc_url,
                        "type": "vc_thesis",
                        "content": self.clean_html(homepage_html)
                    })

                    # Try to find portfolio link(s)
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(homepage_html, "html.parser")
                    portfolio_links = []
                    for a in soup.find_all("a", href=True):
                        text = a.get_text().lower()
                        href = a['href']
                        if any(k in text or k in href.lower() for k in ["portfolio", "companies", "investments"]):
                            full_url = href if href.startswith("http") else vc_url.rstrip("/") + "/" + href.lstrip("/")
                            portfolio_links.append(full_url)

                    print(f"🔗 Discovered {len(portfolio_links)} portfolio links on {vc_url}")
                    for port_url in portfolio_links:
                        try:
                            page.goto(port_url, timeout=15000)
                            port_html = page.content()
                            company_urls = self.extract_company_links(port_html)

                            if not company_urls:
                                continue

                            sample_size = (
                                len(company_urls) if len(company_urls) <= 50
                                else max(10, int(len(company_urls) * 0.2))
                            )
                            sampled = random.sample(company_urls, min(sample_size, len(company_urls)))

                            for company_url in sampled:
                                data = self.scrape_company_page(page, company_url)
                                if data["content"]:
                                    all_records.append({
                                        "source": vc_url,
                                        "type": "portfolio_shallow",
                                        "company_url": company_url,
                                        "content": data["content"]
                                    })

                        except Exception as e:
                            print(f"[ERROR] Failed to load portfolio page: {port_url} — {e}")

                except Exception as e:
                    print(f"[ERROR] Failed to fetch {vc_url}: {e}")

            browser.close()

        # Save to JSONL
        filename = os.path.join(self.output_dir, "vc_scraped_data.jsonl")
        with open(filename, "w", encoding="utf-8") as f:
            for r in all_records:
                f.write(json.dumps(r) + "\n")
        print(f"✅ Finished. Saved {len(all_records)} records to {filename}")
