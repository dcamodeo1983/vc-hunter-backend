# test_vc_scraper.py
import sys
import os

# Ensure the parent directory is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.vc_scraper_agent import VCScraperAgent

if __name__ == "__main__":
    vc_urls = ["https://www.8vc.com"]
    scraper = VCScraperAgent(vc_urls=vc_urls, output_dir="vc-hunter-v2/data/raw/vcs", sample_size=5)
    scraper.run()
