# test_vc_scraper.py

from vc_hunter_v2.agents.vc_scraper_agent import VCScraperAgent

if __name__ == "__main__":
    agent = VCScraperAgent(
        base_url="https://www.8vc.com",
        strategy="tile"  # <-- Ensures it uses the modal tile strategy
    )
    agent.run()
