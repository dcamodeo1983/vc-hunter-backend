import os
import json
import time
import random
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

class VCScraperAgent:
    def __init__(self, output_dir, sample_size=10, timeout_ms=10000, max_retries=2, wait_after_navigation=1000):
        self.output_dir = output_dir
        self.sample_size = sample_size
        self.timeout_ms = timeout_ms
        self.max_retries = max_retries
        self.wait_after_navigation = wait_after_navigation
        os.makedirs(self.output_dir, exist_ok=True)

    def run(self, vc_urls):
        all_data = []
        errors = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()

            for vc_url in vc_urls:
                print(f"🔍 Visiting {vc_url}")
                page = context.new_page()

                try:
                    page.goto(vc_url, timeout=self.timeout_ms)
                    portfolio_links = self.extract_portfolio_links(page)

                    if not portfolio_links:
                        print(f"[WARN] No portfolio links found at {vc_url}")
                        continue

                    print(f"🔗 Discovered {len(portfolio_links)} portfolio links on {vc_url}")

                    sample = random.sample(portfolio_links, min(len(portfolio_links), self.sample_size))
                    scraped_count = 0

                    for company_url in sample:
                        print(f"📥 Visiting portfolio page: {company_url}")
                        result = self.scrape_company(context, company_url)

                        if not result["text"]:
                            print(f"[WARN] Skipping {company_url} due to empty content.")
                            errors.append({"url": company_url, "reason": "empty content"})
                            continue

                        all_data.append({
                            "source": vc_url,
                            "type": "portfolio_shallow",
                            "company_url": company_url,
                            "content": result["text"],
                            "title": result["title"],
                            "raw_html": result["raw_html"],
                        })
                        scraped_count += 1

                    print(f"✅ Scraped {scraped_count} records from {vc_url}")

                except Exception as e:
                    print(f"[ERROR] Failed to process VC site: {vc_url} — {e}")
                    errors.append({"url": vc_url, "reason": str(e)})

            self.save_jsonl("vc_scraped_data.jsonl", all_data)
            self.save_json("scrape_errors.json", errors)
            browser.close()

        print(f"✅ Finished. Saved {len(all_data)} records to {self.output_dir}/vc_scraped_data.jsonl")
        print(f"⚠️  {len(errors)} errors saved to {self.output_dir}/scrape_errors.json")

    def extract_portfolio_links(self, page):
        anchors = page.query_selector_all("a[href]")
        links = [a.get_attribute("href") for a in anchors if a.get_attribute("href")]
        full_links = [link for link in links if link.startswith("http")]
        return list(set(full_links))

    def scrape_company(self, context, company_url):
        for attempt in range(self.max_retries):
            page = context.new_page()
            try:
                page.goto(company_url, timeout=self.timeout_ms)
                time.sleep(self.wait_after_navigation / 1000)
                text = page.text_content("body") or ""
                title = page.title()
                raw_html = page.content()
                return {"text": text.strip(), "title": title, "raw_html": raw_html}
            except PlaywrightTimeoutError:
                print(f"[ERROR] Could not scrape company page: {company_url} — Timeout while visiting {company_url}")
            except Exception as e:
                print(f"[ERROR] Could not scrape company page: {company_url} — {str(e)}")
            finally:
                page.close()
        return {"text": "", "title": "", "raw_html": ""}

    def save_jsonl(self, filename, data):
        path = os.path.join(self.output_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            for record in data:
                f.write(json.dumps(record) + "\n")

    def save_json(self, filename, data):
        path = os.path.join(self.output_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
