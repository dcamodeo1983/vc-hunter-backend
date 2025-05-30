# vc_scraper_agent.py

import os
import json
import logging
import time
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

class VCScraperAgent:
    def __init__(self, base_url, output_dir="vc_hunter_v2/data/raw/vcs", max_scrolls=100, strategy="link"):
        self.base_url = base_url
        self.output_dir = output_dir
        self.max_scrolls = max_scrolls
        self.strategy = strategy  # 'link' or 'tile'
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
                if self.strategy == "tile":
                    tiles = self._scroll_and_extract_modal_tiles(page)
                    logging.info(f"🔗 Discovered {len(tiles)} portfolio tiles on {self.base_url}")
                    if not tiles:
                        self._dump_html(page, "modal_tile_debug.html")
                    scraped = self._scrape_modal_tiles(page, tiles)
                    errors = [r for r in scraped if 'error' in r]
                    scraped = [r for r in scraped if 'error' not in r]
                else:
                    self._wait_for_tiles(page)
                    tiles = self._extract_portfolio_tiles(page)
                    logging.info(f"🔗 Discovered {len(tiles)} portfolio tiles on {self.base_url}")
                    if not tiles:
                        self._dump_html(page, "link_tile_debug.html")
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
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2.5)
            new_height = page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                logging.info("✅ Reached end of content.")
                break
            last_height = new_height

    def _wait_for_tiles(self, page):
        try:
            page.wait_for_selector("a[href*='/companies/'], a[href*='/portfolio/']", timeout=10000)
        except PlaywrightTimeout:
            logging.warning("⚠️ Portfolio tile selector not found in time.")

    def _extract_portfolio_tiles(self, page):
        try:
            tiles = page.evaluate("""
                () => {
                    const anchors = Array.from(document.querySelectorAll("a"));
                    return anchors.map(a => a.href).filter(href =>
                        href.includes('/companies/') || href.includes('/portfolio/')
                    );
                }
            """)
            return list(set(tiles))
        except Exception as e:
            logging.error(f"❌ Error extracting portfolio tiles: {e}")
            return []

    def _scroll_and_extract_modal_tiles(self, page):
        logging.info("📥 Extracting modal-based tiles...")
        stable_scrolls = 0
        previous_count = 0

        for i in range(self.max_scrolls):
            tiles = page.query_selector_all("div[class*='tile'], div[class*='card'], div[class*='portfolio']")
            if len(tiles) == previous_count:
                stable_scrolls += 1
            else:
                stable_scrolls = 0
            if stable_scrolls >= 3:
                break
            previous_count = len(tiles)
            page.evaluate("window.scrollBy(0, window.innerHeight)")
            time.sleep(1.5)

        return [tile.get_attribute("outerHTML") for tile in tiles]

    def _scrape_modal_tiles(self, page, tile_html_snapshots):
        results = []
        for idx, html in enumerate(tile_html_snapshots):
            try:
                # Try to locate a fresh tile element matching snapshot
                tile = page.query_selector(f"div[class*='tile']:has-text('{html[:50]}')")
                if not tile:
                    raise Exception("Tile not found in DOM")
                tile.scroll_into_view_if_needed(timeout=5000)
                tile.click(timeout=10000)
                page.wait_for_selector("div[class*='modal'], div[class*='company-details']", timeout=10000)
                time.sleep(2)
                content_html = page.content()
                title = page.query_selector("h1")
                link = next((a.get_attribute("href") for a in page.query_selector_all("a") if a.get_attribute("href") and not a.get_attribute("href").startswith(self.base_url)), None)
                results.append({
                    "company_name": title.inner_text().strip() if title else f"Tile {idx+1}",
                    "html": content_html,
                    "external_url": link,
                    "source": self.base_url
                })
                page.keyboard.press("Escape")
                time.sleep(1)
            except Exception as e:
                results.append({"tile_index": idx + 1, "error": str(e)})
                logging.warning(f"⚠️ Failed to extract from tile {idx+1}: {e}")
        return results

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

    def _dump_html(self, page, filename):
        html = page.content()
        with open(os.path.join(self.output_dir, filename), "w", encoding="utf-8") as f:
            f.write(html)
        logging.info(f"🧪 Dumped HTML for inspection: {filename}")
