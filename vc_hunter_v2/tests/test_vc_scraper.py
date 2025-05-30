from vc_hunter_v2.agents.vc_scraper_agent import VCScraperAgent

def test_scraper_on_single_vc():
    vc_url = "https://www.8vc.com"
    scraper = VCScraperAgent(vc_url=vc_url)
    scraper.run()

if __name__ == "__main__":
    test_scraper_on_single_vc()
