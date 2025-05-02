import argparse
from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser(
    description="Scraplet: Extract HTML elements using css selectors"
)
parser.add_argument("-u", "--url", required=True, help="URL to scrape")
parser.add_argument(
    "-s",
    "--selector",
    required=True,
    help="CSS selector to extract elements(Ex: #title_class)",
)
args = parser.parse_args()

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto(args.url)

    page.wait_for_selector(args.selector)

    response = page.query_selector_all(args.selector)

    for info in response:
        print("- ", info.inner_text())

    browser.close()
