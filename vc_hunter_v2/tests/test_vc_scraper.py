from vc_hunter_v2.agents.vc_scraper_agent import VCScraperAgent

def test_scraper_on_single_vc():
    output_dir = "vc-hunter-v2/data/raw/vcs"
    vc_urls = ["https://www.8vc.com"]

    scraper = VCScraperAgent(
        output_dir=output_dir,
        sample_size=20,               # Increase for better coverage
        timeout_ms=15000,
        max_retries=3,
        wait_after_navigation=1500
    )
    scraper.run(vc_urls)

if __name__ == "__main__":
    test_scraper_on_single_vc()
