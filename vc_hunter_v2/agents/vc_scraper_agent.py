import os
import json
import random
import time
import logging
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

OUTPUT_PATH = "vc_hunter_v2/data/raw/vcs/vc_scraped_data.jsonl"
TIMEOUT_MS = 15000  # Increased timeout for slow-loading pages
MAX_COMPANIES = 50  # Safety limit for how many companies to scrape

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

class VCScraperAgent:
    def __init__(self, vc_url):
        self.vc_url = vc_url
        self.scraped_data = []
        self.failures = []

    def run(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            logging.info(f"\U0001F50D Visiting {self.vc_url}")
            try:
                page.goto(self.vc_url, timeout=TIMEOUT_MS)
                time.sleep(5)  # Let the JS render
                links = page.locator("a")
                hrefs = links.evaluate_all("nodes => nodes.map(n => n.href)")
                portfolio_links = list(set(h for h in hrefs if h and self._is_likely_portfolio_link(h)))
                logging.info(f"\U0001F517 Discovered {len(portfolio_links)} portfolio links on {self.vc_url}")
            except PlaywrightTimeoutError:
                logging.error(f"Timed out loading VC homepage: {self.vc_url}")
                browser.close()
                return

            random.shuffle(portfolio_links)
            portfolio_links = portfolio_links[:MAX_COMPANIES]

            for link in portfolio_links:
                logging.info(f"\U0001F4E5 Visiting portfolio page: {link}")
                try:
                    page.goto(link, timeout=TIMEOUT_MS)
                    time.sleep(3)  # Wait for content to load
                    html = page.content()
                    if not html.strip():
                        raise ValueError("Empty HTML content")
                    self.scraped_data.append({"url": link, "html": html})
                except PlaywrightTimeoutError:
                    logging.warning(f"Timeout while visiting {link}")
                    self.failures.append({"url": link, "reason": "timeout"})
                except Exception as e:
                    logging.warning(f"Could not scrape company page: {link} — {str(e)}")
                    self.failures.append({"url": link, "reason": str(e)})

            browser.close()
            self.save_data()
            self.print_summary()

    def _is_likely_portfolio_link(self, url):
        ignore_keywords = ["login", "policy", "terms", "privacy", "mailto:", ".pdf"]
        if not url.startswith("http"):
            return False
        if any(k in url.lower() for k in ignore_keywords):
            return False
        return True

    def save_data(self):
        os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
        with open(OUTPUT_PATH, "w") as f:
            for record in self.scraped_data:
                json.dump(record, f)
                f.write("\n")
        logging.info(f"\u2705 Finished. Saved {len(self.scraped_data)} records to {OUTPUT_PATH}")

    def print_summary(self):
        logging.info(f"\u2705 Scraped {len(self.scraped_data)} records from {self.vc_url}")
        for record in self.scraped_data:
            logging.info(f"\uD83D\uDD39 portfolio_shallow: {record['url']}")
        if self.failures:
            logging.info(f"\u26A0\uFE0F {len(self.failures)} portfolio scrapes failed:")
            for fail in self.failures:
                logging.info(f"\t- {fail['url']} — Reason: {fail['reason']}")


if __name__ == "__main__":
    scraper = VCScraperAgent("https://www.8vc.com")
    scraper.run()
