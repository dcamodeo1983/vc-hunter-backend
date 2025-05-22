# test_vc_scraper.py

from vc_hunter_v2.agents.vc_scraper_agent import VCScraperAgent

# 🔍 Test with one known VC URL
vc_urls = ["https://www.8vc.com"]

scraper = VCScraperAgent(vc_urls=vc_urls, output_dir="vc-hunter-v2/data/raw/vcs", sample_size=5)
scraper.run()
