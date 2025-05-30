import os
import json
import time
import random
import logging
from urllib.parse import urlparse
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

class VCScraperAgent:
    def __init__(self, vc_url, output_dir="vc_hunter_v2/data/raw/vcs", timeout_ms=10000):
        self.vc_url = vc_url
        self.output_dir = output_dir
        self.timeout_ms = timeout_ms
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        self.scrape_errors = []

    def is_valid_company_link(self, href):
        if not href:
            return False
        parsed = urlparse(href)
        domain = parsed.netloc.lower()
        # Exclude known non-company patterns
        return not any(
            blocked in domain
            for blocked in ["linkedin.com", "twitter.com", "facebook.com", "youtube.com", "instagram.com"]
        )

    def save_jsonl(self, filename, data):
        path = Path(self.output_dir) / filename
        with path.open("w", encoding="utf-8") as f:
            for record in data:
                f.write(json.dumps(record) + "\n")

    def save_errors(self):
        if self.scrape_errors:
            self.save_jsonl("scrape_errors.json", self.scrape_errors)

    def extract_company_links(self, page):
        anchors = page.query_selector_all("a")
        links = [a.get_attribute("href") for a in anchors]
        valid_links = [link for link in links if self.is_valid_company_link(link)]
        return list(set(valid_links))

    def scrape_company_page(self, page, url):
        try:
            page.goto(url, timeout=self.timeout_ms)
            page.wait_for_load_state("domcontentloaded", timeout=self.timeout_ms)
            text = page.text_content("body")
            title = page.title()
            html = page.content()
            return {"url": url, "title": title, "text": text, "html": html}
        except PlaywrightTimeout:
            self.scrape_errors.append({"url": url, "error": "Timeout"})
            return None
        except Exception as e:
            self.scrape_errors.append({"url": url, "error": str(e)})
            return None

    def run(self):
        all_data = []
        print(f"🔍 Visiting {self.vc_url}")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            try:
                page.goto(self.vc_url, timeout=self.timeout_ms)
                page.wait_for_load_state("domcontentloaded", timeout=self.timeout_ms)
                links = self.extract_company_links(page)
                print(f"🔗 Discovered {len(links)} potential portfolio links on {self.vc_url}")

                for link in links:
                    print(f"📥 Visiting portfolio page: {link}")
                    result = self.scrape_company_page(page, link)
                    if result and result.get("text"):
                        all_data.append({
                            "vc": self.vc_url,
                            "company_url": result["url"],
                            "title": result["title"],
                            "content": result["text"],
                            "raw_html": result["html"],
                        })
                    else:
                        print(f"[WARN] Skipped {link} due to empty content or error.")

            except Exception as e:
                print(f"[FATAL] Failed to open {self.vc_url}: {e}")

            browser.close()

        self.save_jsonl("vc_scraped_data.jsonl", all_data)
        self.save_errors()

        print(f"✅ Scraped {len(all_data)} records from {self.vc_url}")
        if self.scrape_errors:
            print(f"⚠️  {len(self.scrape_errors)} errors saved to scrape_errors.json")
