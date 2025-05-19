
import asyncio
from playwright.async_api import async_playwright
import json
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
async def scrape_with_playwright(url):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=20000)
            content = await page.content()
            text = await page.evaluate("document.body.innerText")
            await browser.close()
            return text.strip()[:10000]
    except Exception as e:
        print(f"❌ Playwright failed for {url}: {e}")
        return None

def save_jsonl(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj) + "\n")

async def main():
    if not os.path.exists("data/failed_scrapes.txt"):
        print("No failed_scrapes.txt found.")
        return

    with open("data/failed_scrapes.txt", "r") as f:
        urls = list(set([line.strip() for line in f if line.strip()]))

    for url in urls:
        print(f"🌐 Retrying with Playwright: {url}")
        text = await scrape_with_playwright(url)
        if text:
            domain = url.split("//")[-1].split("/")[0]
            target_type = "portfolio" if "www." in domain else "vc"
            filename = f"data/raw/{target_type}/{domain}.jsonl"
            save_jsonl(filename, {"url": url, "type": target_type, "content": text})
            print(f"✅ Saved Playwright scrape: {filename}")

if __name__ == "__main__":
    asyncio.run(main())
