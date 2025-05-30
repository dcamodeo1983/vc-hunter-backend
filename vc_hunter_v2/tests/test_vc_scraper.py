# test_vc_scraper.py

import logging
import os
from vc_hunter_v2.agents.vc_scraper_agent import VCScraperAgent

def test_scraper_on_single_vc():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    vc_url = "https://www.8vc.com"
    output_dir = "vc_hunter_v2/data/raw/vcs"

    scraper = VCScraperAgent(
        base_url=vc_url,
        output_dir=output_dir,
        max_scrolls=75  # Adjust as needed
    )

    scraper.run()

if __name__ == "__main__":
    test_scraper_on_single_vc()
