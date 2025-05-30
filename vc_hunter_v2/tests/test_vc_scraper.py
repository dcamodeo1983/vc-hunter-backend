# test_vc_scraper.py

import logging
from vc_hunter_v2.agents.vc_scraper_agent import VCScraperAgent

def test_scraper_on_single_vc():
    logging.basicConfig(level=logging.INFO)
    scraper = VCScraperAgent(
        base_url="https://www.8vc.com",
        output_dir="vc_hunter_v2/data/raw/vcs",
        max_scrolls=100,
        strategy="tile"
    )
    scraper.run()

if __name__ == "__main__":
    test_scraper_on_single_vc()
