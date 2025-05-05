from agents.vc_scraper_agent import VCScraperAgent

vc_urls = [
    "https://www.8vc.com",
    "https://www.foundersfund.com",
    "https://www.sequoiacap.com",
    "https://www.greylock.com",
    "https://www.xyz.vc"
]

if __name__ == "__main__":
    scraper = VCScraperAgent(vc_urls=vc_urls, output_dir="data/raw", sample_size=5)
    scraper.run()
