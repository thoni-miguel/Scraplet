import argparse
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import sys


def main():
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

    try:

        with sync_playwright() as pw:
            try:
                browser = pw.chromium.launch(headless=True)
                page = browser.new_page()

                try:
                    page.goto(args.url, timeout=30000)
                except PlaywrightTimeoutError:
                    print(f"Error: Timeout while loading URL: {args.url}")
                    sys.exit(1)
                except Exception as e:
                    print(f"Error: Failed to load URL: {args.url}")
                    print(f"Details: {str(e)}")
                    sys.exit(1)

                try:
                    page.wait_for_selector(args.selector, timeout=10000)
                except PlaywrightTimeoutError:
                    print(f"Error: Selector '{args.selector}' not found on the page")
                    sys.exit(1)

                response = page.query_selector_all(args.selector)

                if not response:
                    print(
                        f"Warning: No elements found matching selector: {args.selector}"
                    )
                else:
                    for info in response:
                        print("- ", info.inner_text())

            except Exception as e:
                print(f"Error: Browser operation failed")
                print(f"Details: {str(e)}")
                sys.exit(1)
            finally:
                browser.close()

    except Exception as e:
        print(f"Error: Failed to initialize Playwright")
        print(f"Details: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
