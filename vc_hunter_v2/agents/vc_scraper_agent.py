# vc_scraper_agent.py

import os
import json
import logging
import random
import time
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

class VCScraperAgent:
    def __init__(self, base_url, output_dir="vc_hunter_v2/data/raw/vcs", max_scrolls=75):
        self.base_url = base_url
        self.output_dir = output_dir
        self.max_scrolls = max_scrolls
        os.makedirs(self.output_dir, exist_ok=True)

    def run(self):
        logging.info(f"🔍 Visiting {self.base_url}")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            try:
                page.goto(self.base_url, timeout=15000)
                self._scroll_to_bottom(page)
                raw_links = page.query_selector_all("a")
                all_links = [link.get_attribute("href") for link in raw_links if link.get_attribute("href")]
                portfolio_links = self._filter_valid_links(all_links)
                logging.info(f"🔗 Discovered {len(portfolio_links)} potential portfolio links on {self.base_url}")
                results, errors = self._scrape_portfolios(page, portfolio_links)
                self._save_results(results, errors)
            except PlaywrightTimeout:
                logging.error(f"❌ Timeout while visiting {self.base_url}")
            finally:
                browser.close()

    def _scroll_to_bottom(self, page):
        logging.info(f"📜 Scrolling until no new content appears...")
        last_count = -1
        for _ in range(self.max_scrolls):
            page.mouse.wheel(0, 5000)
            time.sleep(2)
            anchors = page.query_selector_all("a")
            current_count = len(anchors)
            if current_count == last_count:
                logging.info("✅ Reached end of content.")
                break
            last_count = current_count

    def _filter_valid_links(self, links):
        seen = set()
        filtered = []
        for link in links:
            full_url = urljoin(self.base_url, link)
            if any(social in full_url for social in ["linkedin.com", "twitter.com", "facebook.com"]):
                continue
            if full_url not in seen:
                seen.add(full_url)
                filtered.append(full_url)
        return filtered

    def _scrape_portfolios(self, page, portfolio_links):
        scraped = []
        errors = []
        for link in portfolio_links:
            try:
                logging.info(f"📥 Visiting portfolio page: {link}")
                page.goto(link, timeout=10000)
                time.sleep(2)
                raw_html = page.content()
                if not raw_html.strip():
                    logging.warning(f"[WARN] Skipped {link} due to empty content or error.")
                    continue
                scraped.append({"url": link, "html": raw_html})
            except PlaywrightTimeout:
                logging.error(f"[ERROR] Timeout while visiting {link}")
                errors.append({"url": link, "error": "Timeout"})
            except Exception as e:
                logging.error(f"[ERROR] Failed to scrape {link}: {e}")
                errors.append({"url": link, "error": str(e)})
        return scraped, errors

    def _save_results(self, scraped, errors):
        jsonl_path = os.path.join(self.output_dir, "vc_scraped_data.jsonl")
        with open(jsonl_path, "w") as f:
            for item in scraped:
                f.write(json.dumps(item) + "\n")
        error_path = os.path.join(self.output_dir, "scrape_errors.json")
        with open(error_path, "w") as f:
            json.dump(errors, f, indent=2)
        summary = {
            "base_url": self.base_url,
            "total_links_discovered": len(scraped) + len(errors),
            "scraped": len(scraped),
            "errors": len(errors),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
        }
        summary_path = os.path.join(self.output_dir, "scrape_summary.json")
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)
        logging.info(f"✅ Scraped {len(scraped)} records from {self.base_url}")
        logging.info(f"⚠️  {len(errors)} errors saved to {error_path}")
