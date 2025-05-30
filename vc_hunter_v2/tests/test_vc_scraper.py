# vc_hunter_v2/tests/test_vc_scraper.py

import os
from vc_hunter_v2.agents.vc_scraper_agent import VCScraperAgent

def test_scraper_on_single_vc():
    # Set a single VC to test
    vc_urls = ["https://www.8vc.com"]

    # Output directory for the scraped data
    output_dir = "vc_hunter_v2/data/raw/vcs"

    # Create the scraper agent
    scraper = VCScraperAgent(
        vc_urls=vc_urls,
        output_dir=output_dir,
        sample_size=50  # Adjust as needed
    )

    # Run the scraper
    scraper.run()

    # Validate output
    output_file = os.path.join(output_dir, "vc_scraped_data.jsonl")
    if os.path.exists(output_file):
        with open(output_file, "r") as f:
            lines = f.readlines()
            print(f"\n✅ Scraped {len(lines)} records from {vc_urls[0]}")
            for line in lines[:5]:  # Preview first 5 entries
                print("🔹", line.strip())
    else:
        print(f"\n❌ No output file found at {output_file}")

    # Check for error report
    error_file = os.path.join(output_dir, "scrape_errors.json")
    if os.path.exists(error_file):
        with open(error_file, "r") as f:
            error_lines = f.readlines()
            print(f"\n⚠️  {len(error_lines)} errors saved to {error_file}")
    else:
        print("\n✅ No scrape errors logged.")

if __name__ == "__main__":
    test_scraper_on_single_vc()
