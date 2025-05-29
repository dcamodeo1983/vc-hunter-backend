
# vc_scraper_agent.py
import os
import json
import time
import random
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout


class VCScraperAgent:
    def __init__(self, vc_urls, output_dir="vc-hunter-v2/data/raw/vcs", sample_size=20):
        self.vc_urls = vc_urls
        self.output_dir = output_dir
        self.sample_size = sample_size
        os.makedirs(self.output_dir, exist_ok=True)

    def is_valid_link(self, href):
        return (
            href
            and href.startswith("http")
            and "linkedin" not in href
            and "twitter" not in href
            and "mailto:" not in href
            and "javascript:" not in href
        )

    def fetch_with_retries(self, page, url, retries=3, timeout=10000):
        for attempt in range(retries):
            try:
                page.goto(url, timeout=timeout)
                page.wait_for_timeout(3000)  # Let JS render
                return page.content()
            except Exception as e:
                print(f"[ERROR] Failed scraping portfolio page: {url} — {e}")
        return ""

    def discover_portfolio_links(self, page, homepage_url):
        print(f"🔍 Visiting {homepage_url}")
        try:
            page.goto(homepage_url, timeout=10000)
            page.wait_for_timeout(3000)  # Wait for JS load
            links = page.locator("a")
            urls = set()

            for i in range(links.count()):
                href = links.nth(i).get_attribute("href")
                text = links.nth(i).inner_text().lower() if links.nth(i) else ""
                if href and any(k in href.lower() or k in text for k in ["portfolio", "companies", "investments"]):
                    full_url = href if href.startswith("http") else homepage_url + href
                    urls.add(full_url)
        except Exception as e:
            print(f"[ERROR] Failed to discover portfolio links on {homepage_url} — {e}")
            return []
        print(f"🔗 Discovered {len(urls)} portfolio links on {homepage_url}")
        return list(urls)

    def extract_company_links(self, page):
        links = page.locator("a")
        company_urls = set()

        for i in range(links.count()):
            href = links.nth(i).get_attribute("href")
            if self.is_valid_link(href):
                company_urls.add(href)
        return list(company_urls)

    def scrape_company(self, page, url):
        try:
            page.goto(url, timeout=10000)
            page.wait_for_timeout(3000)
            title = page.title()
            content = page.inner_text("body")
            raw_html = page.content()
            return {"title": title, "text": content, "raw_html": raw_html}
        except Exception as e:
            print(f"[ERROR] Could not scrape company page: {url} — {e}")
            return {"title": None, "text": None, "raw_html": None}

    def save_jsonl(self, filename, data):
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            for item in data:
                f.write(json.dumps(item) + "\n")

    def run(self):
        all_data = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            for vc_url in self.vc_urls:
                portfolio_pages = self.discover_portfolio_links(page, vc_url)

                for portfolio_url in portfolio_pages:
                    print(f"📥 Visiting portfolio page: {portfolio_url}")
                    html = self.fetch_with_retries(page, portfolio_url)
                    if not html.strip():
                        print(f"[WARN] Skipping {portfolio_url} due to empty content.")
                        continue

                    try:
                        page.set_content(html)
                    except Exception as e:
                        print(f"[ERROR] Failed to set content for {portfolio_url}: {e}")
                        continue

                    company_urls = self.extract_company_links(page)
                    if not company_urls:
                        continue

                    sample = (
                        company_urls
                        if len(company_urls) <= 50
                        else random.sample(company_urls, max(self.sample_size, int(0.2 * len(company_urls))))
                    )

                    for company_url in sample:
                        result = self.scrape_company(page, company_url)
                        all_data.append({
                            "source": vc_url,
                            "type": "portfolio_shallow",
                            "company_url": company_url,
                            "content": result.get("text"),
                            "title": result.get("title"),
                            "raw_html": result.get("raw_html"),
                        })

            self.save_jsonl("vc_scraped_data.jsonl", all_data)
            browser.close()

        print(f"✅ Finished. Saved {len(all_data)} records to {self.output_dir}/vc_scraped_data.jsonl")
