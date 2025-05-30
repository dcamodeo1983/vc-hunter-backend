# test_vc_scraper.py

from vc_hunter_v2.agents.vc_scraper_agent import VCScraperAgent

def test_scraper_on_single_vc():
    scraper = VCScraperAgent(
        base_url="https://www.8vc.com",
        output_dir="vc_hunter_v2/data/raw/vcs",
        max_scrolls=300,
        strategy="tile"  # Use "link" for traditional portfolio pages
    )
    scraper.run()

if __name__ == "__main__":
    test_scraper_on_single_vc()
