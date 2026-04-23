from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("http://localhost:1234")
    page.wait_for_load_state("load")
    time.sleep(10)  # keep the page open for 10 seconds
    browser.close()