# vc_hunter_v2/tests/test_vc_scraper.py

from vc_hunter_v2.agents.vc_scraper_agent import VCScraperAgent

def test_scraper_on_single_vc():
    base_url = "https://www.8vc.com/companies"
    output_dir = "vc_hunter_v2/data/raw/vcs"
    scraper = VCScraperAgent(base_url=base_url, output_dir=output_dir)
    scraper.run()

if __name__ == "__main__":
    test_scraper_on_single_vc()
