from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    print("Chromium launched successfully!")
    browser.close()
