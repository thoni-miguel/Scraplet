import argparse
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import sys
import time
import warnings

# Suppress urllib3 SSL warnings
warnings.filterwarnings("ignore", message=".*urllib3.*OpenSSL.*")

from menu import (
    get_url_from_user,
    get_selectors_from_user,
    get_output_choice,
    save_configuration,
    load_saved_configurations,
    show_help,
    handle_selector_error,
    show_scraping_summary,
    list_saved_configurations,
)
import pandas as pd
import json
from itertools import zip_longest


def get_scraping_params():
    """
    Get URL, selector, and output format from user via menu or command line.
    Returns a tuple: (args, using_saved_config)
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
    parser.add_argument(
        "--help-mode", action="store_true", help="Show detailed help information"
    )
    parser.add_argument(
        "--use-saved", action="store_true", help="Use saved configuration if available"
    )
    parser.add_argument(
        "--list-configs", action="store_true", help="List saved configurations"
    )
    args = parser.parse_args()

    # Show help if requested
    if args.help_mode:
        show_help()
        sys.exit(0)

    # List saved configurations if requested
    if args.list_configs:
        list_saved_configurations()
        sys.exit(0)

    # Check if running in interactive mode (no CLI args provided)
    interactive_mode = not any([args.url, args.selector, args.output, args.use_saved])

    # If in interactive mode, check for saved configuration
    if interactive_mode:
        saved_config = load_saved_configurations()
        if saved_config:
            print(
                f"\nFound saved configuration from {time.ctime(saved_config['timestamp'])}"
            )
            print(f"URL: {saved_config['url']}")
            print(f"Selectors: {saved_config['selectors']}")
            print(f"Output format: {saved_config['output_format']}")

            use_saved = input("\nUse saved configuration? (y/n): ").lower()
            if use_saved == "y":
                args.url = saved_config["url"]
                args.selector = saved_config["selectors"]
                args.output = saved_config["output_format"]
                print("Using saved configuration!")
                return args, True  # Using saved config

    # If use-saved flag is provided, try to load saved config
    if args.use_saved:
        saved_config = load_saved_configurations()
        if saved_config:
            args.url = saved_config["url"]
            args.selector = saved_config["selectors"]
            args.output = saved_config["output_format"]
            print(
                f"Using saved configuration from {time.ctime(saved_config['timestamp'])}"
            )
            return args, True  # Using saved config
        else:
            print(
                "ERROR: No saved configuration found. Run in interactive mode first to save a configuration."
            )
            sys.exit(1)

    # If parameters are not provided via CLI, prompt the user
    if not args.url:
        args.url = get_url_from_user()

    if not args.selector:
        args.selector = get_selectors_from_user()

    if not args.output:
        args.output = get_output_choice()

    return args, False  # Not using saved config


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
    print(f"SUCCESS: Data exported to {filename}")


def export_to_excel(data, filename="output.xlsx"):
    """
    Export scraped data to an Excel file.
    """
    df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in data.items()]))
    df.to_excel(filename, index=False)
    print(f"SUCCESS: Data exported to {filename}")


def export_to_json(data, filename="output.json"):
    """
    Export scraped data to a JSON file.
    """
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    print(f"SUCCESS: Data exported to {filename}")


def print_to_terminal(data):
    """
    Prints the scraped data to the terminal in a well-formatted table.
    """
    print("\n" + "=" * 60)
    print("SCRAPED DATA")
    print("=" * 60)

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

    print("=" * 60)


def main():
    args, using_saved_config = get_scraping_params()
    selectors = get_selectors(args.selector)
    scraped_data = {}

    print(f"\nStarting scrape of: {args.url}")
    print(f"Using {len(selectors)} selector(s)")
    print(f"Output format: {args.output}")

    try:
        with sync_playwright() as pw:
            print("Launching browser...")
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page()

            try:
                print("Loading page...")
                try:
                    page.goto(args.url, timeout=30000)
                    print("SUCCESS: Page loaded successfully!")
                except PlaywrightTimeoutError:
                    print("ERROR: Timeout while loading page")
                    return
                except Exception as e:
                    print(f"ERROR: Failed to load URL: {args.url}")
                    print(f"Error details: {e}")
                    return

                for i, selector in enumerate(selectors, 1):
                    print(f"Processing selector {i}/{len(selectors)}: {selector}")
                    try:
                        page.wait_for_selector(selector, timeout=10000)
                        elements = page.query_selector_all(selector)

                        if not elements:
                            print(f"WARNING: No elements found for: {selector}")
                            scraped_data[selector] = []
                        else:
                            scraped_data[selector] = [
                                element.inner_text() for element in elements
                            ]
                            print(f"SUCCESS: Found {len(elements)} elements")

                    except PlaywrightTimeoutError:
                        print(f"ERROR: Selector not found: {selector}")

                        # Offer to retry with a different selector
                        new_selector = handle_selector_error(selector, page)
                        if new_selector:
                            try:
                                page.wait_for_selector(new_selector, timeout=10000)
                                elements = page.query_selector_all(new_selector)
                                if elements:
                                    scraped_data[new_selector] = [
                                        element.inner_text() for element in elements
                                    ]
                                    print(
                                        f"SUCCESS: Found {len(elements)} elements with new selector"
                                    )
                                else:
                                    scraped_data[new_selector] = []
                            except:
                                scraped_data[new_selector] = [
                                    "ERROR: Selector not found"
                                ]
                        else:
                            scraped_data[selector] = ["ERROR: Selector not found"]

                if not scraped_data:
                    print(
                        f"WARNING: No elements found matching selector(s): {args.selector}"
                    )
                else:
                    # Show scraping summary
                    show_scraping_summary(scraped_data, args.output)

                    # Export data
                    if args.output == "csv":
                        export_to_csv(scraped_data)
                    elif args.output == "excel":
                        export_to_excel(scraped_data)
                    elif args.output == "json":
                        export_to_json(scraped_data)
                    else:
                        print_to_terminal(scraped_data)

                    # Ask to save configuration
                    if not using_saved_config:
                        save = input(
                            "\nSave this configuration for future use? (y/n): "
                        ).lower()
                        if save == "y":
                            save_configuration(args.url, args.selector, args.output)
                    else:
                        print("\nUsing saved configuration - skipping save prompt.")

            except Exception as e:
                print(f"ERROR: Browser operation failed: {e}")
            finally:
                # Close browser within the Playwright context
                if "browser" in locals() and browser.is_connected():
                    browser.close()

    except Exception as e:
        print(f"ERROR: Failed to initialize Playwright: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
