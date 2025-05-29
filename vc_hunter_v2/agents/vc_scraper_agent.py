# vc_scraper_agent.py
import os
import json
import time
import random
from urllib.parse import urlparse, urljoin

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

    def discover_portfolio_links(self, page, homepage_url):
        print(f"🔍 Visiting {homepage_url}")
        try:
            page.goto(homepage_url, timeout=15000, wait_until="load")
            page.wait_for_timeout(3000)
            links = page.locator("a")
            urls = set()

            count = links.count()
            for i in range(min(count, 500)):  # limit to reduce long loops
                href = links.nth(i).get_attribute("href")
                text = links.nth(i).inner_text().lower() if links.nth(i) else ""
                if href and any(k in href.lower() or k in text for k in ["portfolio", "companies", "investments"]):
                    full_url = urljoin(homepage_url, href)
                    urls.add(full_url)

            print(f"🔗 Discovered {len(urls)} portfolio links on {homepage_url}")
            return list(urls)

        except Exception as e:
            print(f"[ERROR] Failed to discover portfolio links on {homepage_url} — {e}")
            return []

    def scrape_company(self, context, company_url):
        print(f"📥 Visiting portfolio page: {company_url}")
        try:
            page = context.new_page()
            page.goto(company_url, timeout=15000, wait_until="load")
            page.wait_for_timeout(3000)

            text = page.text_content("body") or ""
            title = page.title()
            raw_html = page.content()

            page.close()
            return {"text": text.strip(), "title": title.strip(), "raw_html": raw_html}

        except Exception as e:
            print(f"[ERROR] Could not scrape company page: {company_url} — {e}")
            return {"text": "", "title": "", "raw_html": ""}

    def save_jsonl(self, filename, data):
        path = os.path.join(self.output_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            for entry in data:
                json.dump(entry, f)
                f.write("\n")

    def run(self):
        all_data = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()

            for vc_url in self.vc_urls:
                page = context.new_page()
                portfolio_links = self.discover_portfolio_links(page, vc_url)
                page.close()

                for link in portfolio_links:
                    page = context.new_page()
                    try:
                        page.goto(link, timeout=15000, wait_until="load")
                        page.wait_for_timeout(3000)
                        company_links = set()

                        anchors = page.locator("a")
                        count = anchors.count()

                        for i in range(min(count, 500)):
                            href = anchors.nth(i).get_attribute("href")
                            if self.is_valid_link(href):
                                full_url = urljoin(link, href)
                                company_links.add(full_url)

                        company_links = list(company_links)
                        sample = (
                            company_links
                            if len(company_links) <= 50
                            else random.sample(company_links, max(self.sample_size, int(0.2 * len(company_links))))
                        )

                        for company_url in sample:
                            result = self.scrape_company(context, company_url)
                            if not result["text"]:
                                print(f"[WARN] Skipping {company_url} due to empty content.")
                                continue

                            all_data.append({
                                "source": vc_url,
                                "type": "portfolio_shallow",
                                "company_url": company_url,
                                "content": result["text"],
                                "title": result["title"],
                                "raw_html": result["raw_html"],
                            })

                    except Exception as e:
                        print(f"[ERROR] Failed to extract companies from {link} — {e}")
                    finally:
                        page.close()

            self.save_jsonl("vc_scraped_data.jsonl", all_data)
            browser.close()

        print(f"✅ Finished. Saved {len(all_data)} records to {self.output_dir}/vc_scraped_data.jsonl")
