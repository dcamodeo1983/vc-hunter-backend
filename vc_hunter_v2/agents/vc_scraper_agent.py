
import os
import time
import json
import random
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

class VCScraperAgent:
    def __init__(self, vc_urls, output_dir="vc-hunter-v2/data/raw/vcs", sample_size=10):
        self.vc_urls = vc_urls
        self.output_dir = output_dir
        self.sample_size = sample_size
        os.makedirs(output_dir, exist_ok=True)

    def extract_links(self, page):
        page.wait_for_timeout(3000)
        for _ in range(8):  # simulate scrolling to load JS content
            page.mouse.wheel(0, 1000)
            page.wait_for_timeout(1000)
        anchors = page.query_selector_all("a")
        hrefs = set()
        for anchor in anchors:
            href = anchor.get_attribute("href")
            if href and href.startswith("http"):
                hrefs.add(href)
        return list(hrefs)

    def scrape_company(self, page, url):
        for attempt in range(2):
            try:
                page.goto(url, timeout=20000)
                page.wait_for_timeout(2000)
                title = page.title()
                html = page.content()
                text = page.inner_text("body")
                if not text.strip():
                    raise ValueError("Empty body text")
                return {"title": title, "raw_html": html, "text": text}
            except Exception as e:
                if attempt == 1:
                    raise e
                page.wait_for_timeout(2000)

    def run(self):
        successes = []
        failures = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            for vc_url in self.vc_urls:
                print(f"🔍 Visiting {vc_url}")
                try:
                    page.goto(vc_url, timeout=20000)
                except PlaywrightTimeoutError:
                    print(f"[ERROR] Timeout while visiting {vc_url}")
                    continue

                all_links = self.extract_links(page)
                print(f"🔗 Discovered {len(all_links)} portfolio links on {vc_url}")

                portfolio_links = [
                    link for link in all_links
                    if not any(domain in link for domain in ["linkedin", "twitter", "termly", "login", "auth", "x.com"])
                ]

                sample = (
                    portfolio_links
                    if len(portfolio_links) <= 100
                    else random.sample(portfolio_links, min(self.sample_size, len(portfolio_links)))
                )

                for link in sample:
                    print(f"📥 Visiting portfolio page: {link}")
                    try:
                        result = self.scrape_company(page, link)
                        successes.append({
                            "source": vc_url,
                            "type": "portfolio_shallow",
                            "company_url": link,
                            "content": result.get("text"),
                            "title": result.get("title"),
                            "raw_html": result.get("raw_html"),
                        })
                    except Exception as e:
                        print(f"[ERROR] Could not scrape company page: {link} — {e}")
                        failures.append({"url": link, "error": str(e)})

            browser.close()

        jsonl_path = os.path.join(self.output_dir, "vc_scraped_data.jsonl")
        with open(jsonl_path, "w") as f:
            for entry in successes:
                f.write(json.dumps(entry) + "\n")

        error_path = os.path.join(self.output_dir, "scrape_errors.json")
        with open(error_path, "w") as f:
            json.dump(failures, f, indent=2)

        summary_path = os.path.join(self.output_dir, "scrape_summary.txt")
        with open(summary_path, "w") as f:
            f.write(f"✅ Scraped {len(successes)} records from {self.vc_urls[0]}\n")
            f.write(f"❌ Failed: {len(failures)} records\n")
            if failures:
                f.write("❌ Failures by URL:\n")
                for fail in failures:
                    f.write(f"- {fail['url']}: {fail['error']}\n")

        print(f"✅ Finished. Saved {len(successes)} records to {jsonl_path}")
        if failures:
            print(f"⚠️  {len(failures)} errors saved to {error_path}")
            print(f"📄 Summary written to {summary_path}")
