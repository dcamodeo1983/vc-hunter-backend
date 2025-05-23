# test_vc_scraper.py

import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from vc_hunter.agents.vc_scraper_agent import VCScraperAgent



def test_scraper_on_single_vc():
    vc_urls = ["https://www.8vc.com"]
    output_dir = "vc-hunter-v2/data/raw/vcs"

    scraper = VCScraperAgent(vc_urls=vc_urls, output_dir=output_dir, sample_size=5)
    scraper.run()

    output_file = os.path.join(output_dir, "vc_scraped_data.jsonl")
    assert os.path.exists(output_file), "Output file was not created."

    with open(output_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    print(f"✅ Scraped {len(lines)} records from {vc_urls[0]}")
    for line in lines[:5]:
        record = json.loads(line)
        print(f"🔹 {record.get('type')}: {record.get('company_url', '')[:60]}")

if __name__ == "__main__":
    test_scraper_on_single_vc()
