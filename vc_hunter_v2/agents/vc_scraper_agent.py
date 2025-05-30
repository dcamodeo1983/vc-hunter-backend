import os
import json
import random
import time
from pathlib import Path
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout


class VCScraperAgent:
    def __init__(self, vc_urls: List[str], output_dir: str = "data", sample_size: int = 25):
        self.vc_urls = vc_urls
        self.output_dir = output_dir
        self.sample_size = sample_size
        os.makedirs(self.output_dir, exist_ok=True)

    def run(self):
        all_data = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()

            for vc_url in self.vc_urls:
                print(f"🔍 Visiting {vc_url}")
                try:
                    page = context.new_page()
                    page.goto(vc_url, timeout=10000)
                    links = page.query_selector_all("a")
                    hrefs = [link.get_attribute("href") for link in links if link.get_attribute("href")]
                    portfolio_links = [href for href in hrefs if self.is_portfolio_link(href)]

                    print(f"🔗 Discovered {len(portfolio_links)} portfolio links on {vc_url}")
                    seen = set()
                    sampled_links = []

                    if len(portfolio_links) == 0:
                        continue

                    # Shuffle links for randomness
                    random.shuffle(portfolio_links)

                    for company_url in portfolio_links:
                        if company_url in seen:
                            continue
                        seen.add(company_url)

                        print(f"📥 Visiting portfolio page: {company_url}")
                        try:
                            result = self.scrape_company(context, company_url)
                            if result["text"].strip():
                                all_data.append({
                                    "source": vc_url,
                                    "type": "portfolio_shallow",
                                    "company_url": company_url,
                                    "content": result["text"],
                                    "title": result["title"],
                                    "raw_html": result["raw_html"],
                                })
                            else:
                                print(f"[WARN] Skipping {company_url} due to empty content.")
                        except Exception as e:
                            print(f"[ERROR] Could not scrape company page: {company_url} — {e}")

                    page.close()
                except Exception as e:
                    print(f"[ERROR] Failed visiting {vc_url} — {e}")

            context.close()
            browser.close()

        self.save_jsonl("vc_scraped_data.jsonl", all_data)
        print(f"✅ Finished. Saved {len(all_data)} records to {self.output_dir}/vc_scraped_data.jsonl")

    def scrape_company(self, context, url: str) -> Dict[str, Optional[str]]:
        page = context.new_page()
        try:
            page.goto(url, timeout=10000)
            title = page.title()
            raw_html = page.content()
            text_content = page.inner_text("body")
            return {
                "title": title,
                "raw_html": raw_html,
                "text": text_content,
            }
        except PWTimeout:
            raise Exception(f"Timeout while visiting {url}")
        finally:
            page.close()

    def is_portfolio_link(self, href: str) -> bool:
        if not href.startswith("http"):
            return False
        blacklist = ["linkedin.com", "twitter.com", "facebook.com", "instagram.com"]
        if any(bad in href for bad in blacklist):
            return False
        return True

    def save_jsonl(self, filename: str, data: List[Dict]):
        path = Path(self.output_dir) / filename
        with open(path, "w", encoding="utf-8") as f:
            for entry in data:
                f.write(json.dumps(entry) + "\n")
