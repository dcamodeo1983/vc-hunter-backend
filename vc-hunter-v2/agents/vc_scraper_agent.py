# vc_scraper_agent.py

import os
import json
import random
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright

class VCScraperAgent:
    def __init__(self, vc_urls, output_dir="vc-hunter-v2/data/raw/vcs", sample_size=10):
        self.vc_urls = vc_urls
        self.output_dir = output_dir
        self.sample_size = sample_size
        os.makedirs(self.output_dir, exist_ok=True)

    def run(self):
        all_records = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            for vc_url in self.vc_urls:
                print(f"\n🔍 Visiting VC site: {vc_url}")
                try:
                    page.goto(vc_url, timeout=15000)
                    page.wait_for_load_state("load")
                except Exception as e:
                    print(f"[ERROR] Could not load {vc_url}: {e}")
                    continue

                base_url = f"{urlparse(vc_url).scheme}://{urlparse(vc_url).netloc}"
                html_text = page.content()
                all_records.append({
                    "source": vc_url,
                    "type": "vc_thesis",
                    "content": html_text
                })

                portfolio_links = self.discover_portfolio_links(page, base_url)
                print(f"🔗 Found {len(portfolio_links)} portfolio links")

                for portfolio_url in portfolio_links:
                    try:
                        page.goto(portfolio_url, timeout=15000)
                        page.wait_for_load_state("load")
                        company_links = self.extract_company_links(page)
                        print(f"🏢 Found {len(company_links)} company links on {portfolio_url}")

                        if not company_links:
                            continue

                        sample_count = min(self.sample_size, len(company_links))
                        sampled = random.sample(company_links, sample_count)

                        for company_url in sampled:
                            company_data = self.scrape_company_shallow(page, company_url)
                            all_records.append({
                                "source": vc_url,
                                "type": "portfolio_shallow",
                                "company_url": company_url,
                                "content": company_data["description"] or company_data["raw_text"]
                            })

                    except Exception as e:
                        print(f"[ERROR] Failed scraping portfolio page: {portfolio_url} — {e}")
                        continue

            context.close()
            browser.close()

        self.save_jsonl("vc_scraped_data.jsonl", all_records)
        print(f"\n✅ Finished. Saved {len(all_records)} records to {self.output_dir}/vc_scraped_data.jsonl")

    def discover_portfolio_links(self, page, base_url):
        anchors = page.query_selector_all("a")
        links = []
        for a in anchors:
            href = a.get_attribute("href") or ""
            text = (a.inner_text() or "").lower()
            if any(keyword in href.lower() or keyword in text for keyword in ["portfolio", "companies", "investments"]):
                full_url = urljoin(base_url, href)
                links.append(full_url)
        return list(set(links))

    def extract_company_links(self, page):
        anchors = page.query_selector_all("a")
        company_links = set()
        for a in anchors:
            href = a.get_attribute("href")
            if href and href.startswith("http") and not any(s in href for s in ["linkedin", "twitter", "mailto", "javascript"]):
                company_links.add(href)
        return list(company_links)

    def scrape_company_shallow(self, page, url):
        try:
            page.goto(url, timeout=10000)
            page.wait_for_load_state("load")
            html = page.content()
            meta = page.query_selector("meta[name='description']")
            desc = meta.get_attribute("content") if meta else ""
            return {
                "company_url": url,
                "description": desc.strip() if desc else "",
                "raw_text": html[:1500]
            }
        except Exception as e:
            print(f"[ERROR] Could not load company site {url}: {e}")
            return {
                "company_url": url,
                "description": "",
                "raw_text": ""
            }

    def save_jsonl(self, filename, records):
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            for record in records:
                f.write(json.dumps(record) + "\n")
