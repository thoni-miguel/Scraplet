import argparse
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import sys
import time
from menu import get_url_from_user, get_selectors_from_user, get_output_choice
import pandas as pd
import json
from itertools import zip_longest


def get_scraping_params():
    """
    Get URL, selector, and output format from user via menu or command line.
    """
    parser = argparse.ArgumentParser(
        description="Scraplet: Extract HTML elements using css selectors"
    )
    parser.add_argument("-u", "--url", help="URL to scrape")
    parser.add_argument(
        "-s",
        "--selector",
        help="CSS selector to extract elements(Ex: #title_class)",
    )
    parser.add_argument(
        "-o",
        "--output",
        choices=["csv", "excel", "json", "terminal"],
        help="Output format",
    )
    args = parser.parse_args()

    # If parameters are not provided via CLI, prompt the user
    if not args.url:
        args.url = get_url_from_user()

    if not args.selector:
        args.selector = get_selectors_from_user()

    if not args.output:
        args.output = get_output_choice()

    return args


def get_selectors(selector):
    separator = "||"
    if separator in selector:
        selectors = selector.split(separator)
    else:
        selectors = [selector]
    return selectors


def export_to_csv(data, filename="output.csv"):
    """
    Export scraped data to a CSV file.
    The keys of the dictionary are selectors (columns), and values are the scraped text.
    """
    df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in data.items()]))
    df.to_csv(filename, index=False)
    print(f"Data successfully exported to {filename}")


def export_to_excel(data, filename="output.xlsx"):
    """
    Export scraped data to an Excel file.
    """
    df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in data.items()]))
    df.to_excel(filename, index=False)
    print(f"Data successfully exported to {filename}")


def export_to_json(data, filename="output.json"):
    """
    Export scraped data to a JSON file.
    """
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Data successfully exported to {filename}")


def print_to_terminal(data):
    """
    Prints the scraped data to the terminal in a well-formatted table.
    """
    print("--- SCRAPED DATA ---")

    if not data:
        print("No data to display.")
        return

    headers = data.keys()

    # Use zip_longest to handle columns of different lengths
    rows = zip_longest(*data.values(), fillvalue="")

    # Create a formatted table
    header_line = " | ".join(f"{h:<30}" for h in headers)
    print(header_line)
    print("-" * len(header_line))

    for row in rows:
        row_line = " | ".join(f"{str(item):<30}" for item in row)
        print(row_line)

    print("--------------------")


def main():
    args = get_scraping_params()
    selectors = get_selectors(args.selector)
    scraped_data = {}

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
                    sys.exit(1)

                for selector in selectors:
                    try:
                        time.sleep(5)
                        page.wait_for_selector(selector, timeout=10000)
                        elements = page.query_selector_all(selector)
                        if not elements:
                            print(
                                f"Warning: No elements found for selector: '{selector}'"
                            )
                            scraped_data[selector] = []
                        else:
                            scraped_data[selector] = [
                                element.inner_text() for element in elements
                            ]
                    except PlaywrightTimeoutError:
                        print(f"Error: Selector '{selector}' not found on the page.")
                        scraped_data[selector] = ["ERROR: Selector not found"]

                if not scraped_data:
                    print(
                        f"Warning: No elements found matching selector(s): {args.selector}"
                    )
                else:
                    if args.output == "csv":
                        export_to_csv(scraped_data)
                    elif args.output == "excel":
                        export_to_excel(scraped_data)
                    elif args.output == "json":
                        export_to_json(scraped_data)
                    else:
                        print_to_terminal(scraped_data)

            except Exception as e:
                print(f"Error: Browser operation failed: {e}")
                sys.exit(1)
            finally:
                if "browser" in locals() and browser.is_connected():
                    browser.close()

    except Exception as e:
        print(f"Error: Failed to initialize Playwright: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
