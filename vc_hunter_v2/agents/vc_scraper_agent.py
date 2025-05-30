# vc_scraper_agent.py

import os
import json
import logging
import random
import time
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

class VCScraperAgent:
    def __init__(self, base_url, output_dir="vc_hunter_v2/data/raw/vcs", max_scrolls=100, min_sample_ratio=0.25):
        self.base_url = base_url
        self.output_dir = output_dir
        self.max_scrolls = max_scrolls
        self.min_sample_ratio = min_sample_ratio
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
                tiles = self._find_tiles(page)
                logging.info(f"🔗 Discovered {len(tiles)} portfolio tiles on {self.base_url}")
                results, errors = self._sample_tiles_until_converged(page, tiles)
                self._save_results(results, errors, len(tiles))
            except PlaywrightTimeout:
                logging.error(f"❌ Timeout while visiting {self.base_url}")
            finally:
                browser.close()

    def _scroll_to_bottom(self, page):
        logging.info("📜 Scrolling until no new content appears...")
        last_count = -1
        for _ in range(self.max_scrolls):
            page.mouse.wheel(0, 5000)
            time.sleep(2)
            tiles = self._find_tiles(page)
            current_count = len(tiles)
            if current_count == last_count:
                logging.info("✅ Reached end of content.")
                break
            last_count = current_count

    def _find_tiles(self, page):
        selectors = ["[data-testid='portfolio-tile']", ".portfolio-tile", "div[data-portfolio-entry]", "div.card"]
        for selector in selectors:
            tiles = page.query_selector_all(selector)
            if tiles:
                return tiles
        return []

    def _scrape_tile_modal(self, page, tile):
        try:
            tile.scroll_into_view_if_needed()
            tile.click()
            page.wait_for_selector(".portfolio-detail, .modal-content", timeout=7000)
            time.sleep(1)
            raw_html = page.content()
            ext_links = [a.get_attribute("href") for a in page.query_selector_all("a[href^='http']") if a.get_attribute("href") and self.base_url not in a.get_attribute("href")]
            ext_link = ext_links[0] if ext_links else None
            if not raw_html.strip():
                return None, {"tile_index": str(tile), "error": "Empty modal content"}
            return {"html": raw_html, "external_url": ext_link, "source": self.base_url}, None
        except PlaywrightTimeout:
            return None, {"tile_index": str(tile), "error": "Timeout"}
        except Exception as e:
            return None, {"tile_index": str(tile), "error": str(e)}
        finally:
            try:
                page.keyboard.press("Escape")
                time.sleep(0.5)
            except:
                pass

    def _sample_tiles_until_converged(self, page, tiles):
        scraped = []
        errors = []
        attempted = set()
        info_chars = 0
        no_info_gain_count = 0
        min_sample_size = max(1, int(len(tiles) * self.min_sample_ratio))

        while len(scraped) < min_sample_size and len(attempted) < len(tiles):
            candidates = [i for i in range(len(tiles)) if i not in attempted]
            if not candidates:
                break
            idx = random.choice(candidates)
            attempted.add(idx)
            tile = tiles[idx]
            result, error = self._scrape_tile_modal(page, tile)
            if result:
                added_chars = len(result["html"])
                if added_chars > 500:
                    scraped.append(result)
                    if added_chars > info_chars:
                        info_chars = added_chars
                        no_info_gain_count = 0
                    else:
                        no_info_gain_count += 1
                else:
                    logging.info(f"[INFO] Skipped tile {idx} due to low info gain.")
            if error:
                errors.append(error)
            if no_info_gain_count >= 5:
                logging.info("📉 No new info gained in 5 attempts, stopping early.")
                break

        return scraped, errors

    def _save_results(self, scraped, errors, total_discovered):
        jsonl_path = os.path.join(self.output_dir, "vc_scraped_data.jsonl")
        with open(jsonl_path, "w") as f:
            for item in scraped:
                f.write(json.dumps(item) + "\n")
        error_path = os.path.join(self.output_dir, "scrape_errors.json")
        with open(error_path, "w") as f:
            json.dump(errors, f, indent=2)
        summary = {
            "base_url": self.base_url,
            "total_tiles_discovered": total_discovered,
            "unique_successful_scrapes": len(scraped),
            "failures": len(errors),
            "min_sample_required": max(1, int(total_discovered * self.min_sample_ratio)),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
        }
        summary_path = os.path.join(self.output_dir, "scrape_summary.json")
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)
        logging.info(f"✅ Scraped {len(scraped)} records from {self.base_url}")
        logging.info(f"⚠️  {len(errors)} errors saved to {error_path}")
