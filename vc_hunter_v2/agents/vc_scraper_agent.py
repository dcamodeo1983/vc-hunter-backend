# vc_scraper_agent.py

import os
import json
import logging
import time
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

class VCScraperAgent:
    def __init__(self, base_url, output_dir="vc_hunter_v2/data/raw/vcs", max_scrolls=100):
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
                page.goto(self.base_url, timeout=30000)
                self._scroll_to_bottom(page)
                tiles = self._extract_portfolio_tiles(page)
                logging.info(f"🔗 Discovered {len(tiles)} portfolio tiles on {self.base_url}")
                scraped, errors = self._scrape_tiles(context, tiles)
                self._save_results(scraped, errors)
            except PlaywrightTimeout:
                logging.error(f"❌ Timeout while visiting {self.base_url}")
            finally:
                browser.close()

    def _scroll_to_bottom(self, page):
        logging.info("📜 Scrolling until no new content appears...")
        last_height = 0
        for _ in range(self.max_scrolls):
            page.mouse.wheel(0, 5000)
            time.sleep(2)
            new_height = page.evaluate("() => document.body.scrollHeight")
            if new_height == last_height:
                logging.info("✅ Reached end of content.")
                break
            last_height = new_height

    def _extract_portfolio_tiles(self, page):
        tiles = page.query_selector_all("a[href*='/companies/'], a[href*='/portfolio/']")
        results = []
        for tile in tiles:
            href = tile.get_attribute("href")
            if href:
                full_url = urljoin(self.base_url, href)
                results.append(full_url)
        return list(set(results))

    def _scrape_tiles(self, context, links):
        scraped = []
        errors = []
        visited = set()

        for url in links:
            if url in visited:
                continue
            visited.add(url)
            page = context.new_page()
            try:
                page.goto(url, timeout=15000)
                page.wait_for_load_state("domcontentloaded")
                time.sleep(2)
                ext_links = [a.get_attribute("href") for a in page.query_selector_all("a[href^='http']") if a.get_attribute("href") and self.base_url not in a.get_attribute("href")]
                ext_link = ext_links[0] if ext_links else None
                company_name = page.query_selector("h1")
                company_text = company_name.inner_text().strip() if company_name else "Unknown"
                raw_html = page.content()
                if raw_html.strip():
                    scraped.append({
                        "company_name": company_text,
                        "html": raw_html,
                        "external_url": ext_link,
                        "source": url
                    })
                else:
                    errors.append({"url": url, "error": "Empty page content"})
            except PlaywrightTimeout:
                errors.append({"url": url, "error": "Timeout"})
            except Exception as e:
                errors.append({"url": url, "error": str(e)})
            finally:
                page.close()
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
            "scraped_count": len(scraped),
            "error_count": len(errors),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
        }
        summary_path = os.path.join(self.output_dir, "scrape_summary.json")
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)

        logging.info(f"✅ Scraped {len(scraped)} records from {self.base_url}")
        logging.info(f"⚠️  {len(errors)} errors saved to {error_path}")
