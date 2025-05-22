from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://a16z.com/portfolio", timeout=15000)
    print(page.title())
    browser.close()
