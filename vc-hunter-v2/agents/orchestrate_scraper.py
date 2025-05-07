
import subprocess
import os

print("🚀 Starting requests-based scraper...")
subprocess.run(["python3", "agents/generalized_scraper.py"])

if os.path.exists("data/failed_scrapes.txt"):
    with open("data/failed_scrapes.txt") as f:
        if any(line.strip() for line in f):
            print("\n🔄 JS fallback scraper starting...")
            subprocess.run(["python3", "agents/js_fallback_scraper.py"])
        else:
            print("\n✅ No failed scrapes to retry.")
else:
    print("\n✅ No failed_scrapes.txt found.")
