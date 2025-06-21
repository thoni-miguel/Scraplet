import json
import time
import requests
from urllib.parse import urlparse


def get_url_from_user():
    """
    Prompt the user to enter a URL with enhanced validation and feedback
    """
    print("Welcome to Scraplet!")
    print("Please enter the URL you want to scrape:")

    while True:
        url = input("URL: ").strip()

        if not url:
            print("ERROR: URL cannot be empty. Please try again.")
            continue

        # Better URL validation
        if not (url.startswith(("http://", "https://"))):
            print("ERROR: Please enter a valid URL starting with http:// or https://")
            continue

        # Test URL accessibility
        print("Testing URL accessibility...")
        try:
            response = requests.head(url, timeout=10)
            if response.status_code == 200:
                print("SUCCESS: URL is accessible!")
                return url
            else:
                print(f"WARNING: URL returned status code {response.status_code}")
                proceed = input("Continue anyway? (y/n): ").lower()
                if proceed == "y":
                    return url
        except Exception as e:
            print(f"WARNING: Could not verify URL ({e})")
            proceed = input("Continue anyway? (y/n): ").lower()
            if proceed == "y":
                return url


def print_selector_help():
    """
    Display help information for CSS selectors
    """
    print("\nSELECTOR HELP:")
    print("  .class-name     - Elements with specific class")
    print("  #id-name        - Element with specific ID")
    print("  tag-name        - All elements of that tag")
    print("  parent > child  - Direct child relationship")
    print("  ancestor descendant - Any descendant")
    print("  [attribute=value] - Elements with specific attribute")
    print("  tag.class       - Elements with specific tag and class")
    print("  tag#id          - Elements with specific tag and ID")
    print("\nEXAMPLES:")
    print("  .product-title")
    print("  #main-content h1")
    print("  .price||.title||.description")


def get_selectors_from_user():
    """
    Interactive selector builder with help and validation
    """
    print("\nCSS Selector Configuration")
    print("You can enter multiple selectors separated by '||' (double pipe)")
    print("Type 'help' for selector examples, 'done' when finished")

    selectors = []
    while True:
        selector = input(
            f"Selector {len(selectors) + 1} (or 'done' to finish): "
        ).strip()

        if selector.lower() == "done":
            break
        elif selector.lower() == "help":
            print_selector_help()
            continue
        elif not selector:
            print("ERROR: Selector cannot be empty.")
            continue

        selectors.append(selector)

        # Ask if user wants to add more
        if len(selectors) == 1:
            more = input("Add another selector? (y/n): ").lower()
            if more != "y":
                break

    if not selectors:
        print("ERROR: At least one selector is required.")
        return get_selectors_from_user()

    return "||".join(selectors)


def get_custom_filename():
    """
    Get custom filename from user
    """
    while True:
        filename = input("Enter filename (without extension): ").strip()
        if filename:
            return f"custom_{filename}"
        else:
            print("ERROR: Filename cannot be empty.")


def get_output_choice():
    """
    Enhanced output format selection with custom filename option
    """
    print("\nOutput Configuration")
    print("How would you like to export the results?")
    print("  1 - CSV file (output.csv)")
    print("  2 - Excel file (output.xlsx)")
    print("  3 - JSON file (output.json)")
    print("  4 - Display in terminal")
    print("  5 - Custom filename")

    while True:
        choice = input("Select an option (1-5): ").strip()

        if choice == "1":
            return "csv"
        elif choice == "2":
            return "excel"
        elif choice == "3":
            return "json"
        elif choice == "4":
            return "terminal"
        elif choice == "5":
            return get_custom_filename()
        else:
            print("ERROR: Invalid option. Please select 1-5.")


def save_configuration(url, selectors, output_format):
    """
    Save current configuration for future use
    """
    config = {
        "url": url,
        "selectors": selectors,
        "output_format": output_format,
        "timestamp": time.time(),
    }

    try:
        with open("scraplet_config.json", "w") as f:
            json.dump(config, f, indent=2)
        print("SUCCESS: Configuration saved to scraplet_config.json!")
    except Exception as e:
        print(f"WARNING: Could not save configuration: {e}")


def load_saved_configurations():
    """
    Load previously saved configurations
    """
    try:
        with open("scraplet_config.json", "r") as f:
            configs = json.load(f)
        return configs
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"WARNING: Could not load saved configuration: {e}")
        return None


def list_saved_configurations():
    """
    List all saved configurations with details
    """
    saved_config = load_saved_configurations()
    if not saved_config:
        print("No saved configurations found.")
        print("Run the scraper in interactive mode and save a configuration first.")
        return

    print("\nSaved Configuration:")
    print("=" * 50)
    print(f"Created: {time.ctime(saved_config['timestamp'])}")
    print(f"URL: {saved_config['url']}")
    print(f"Selectors: {saved_config['selectors']}")
    print(f"Output Format: {saved_config['output_format']}")
    print("=" * 50)
    print("\nTo use this configuration:")
    print("  python scraplet.py --use-saved")
    print("  python scraplet.py  (interactive mode will prompt to use saved config)")


def ask_to_save_config(url, selectors, output_format):
    """
    Ask user if they want to save the current configuration
    """
    save = input("\nSave this configuration for future use? (y/n): ").lower()
    if save == "y":
        save_configuration(url, selectors, output_format)


def show_help():
    """
    Display comprehensive help information
    """
    print(
        """
Scraplet - Web Scraping Made Easy

USAGE:
  python scraplet.py                    # Interactive mode
  python scraplet.py -u URL -s SELECTOR # Command line mode
  python scraplet.py --use-saved        # Use saved configuration
  python scraplet.py --list-configs     # List saved configurations

EXAMPLES:
  python scraplet.py -u https://example.com -s ".title" -o csv
  python scraplet.py -u https://example.com -s ".price||.name" -o json
  python scraplet.py --use-saved

SELECTOR EXAMPLES:
  .class-name     - Elements with class
  #id-name        - Element with ID  
  tag-name        - All elements of tag
  parent > child  - Direct child
  [attr=value]    - Elements with attribute

OUTPUT FORMATS:
  csv     - Comma-separated values
  excel   - Excel spreadsheet
  json    - JSON format
  terminal- Display in console

CONFIGURATION MANAGEMENT:
  - Save configurations during interactive mode
  - Use --use-saved to load saved configuration
  - Use --list-configs to view saved configuration
  - Interactive mode automatically prompts to use saved config

TIPS:
  - Use browser developer tools to find selectors
  - Test selectors in browser console with document.querySelector()
  - Multiple selectors can be combined with ||
  - Save configurations for repeated scraping tasks
  - Check URL accessibility before scraping
"""
    )


def handle_selector_error(selector, page):
    """
    Provide helpful suggestions when selectors fail
    """
    print(f"\nERROR: Selector failed: {selector}")
    print("Suggestions:")
    print("  1. Check if the selector is correct")
    print("  2. The element might be loaded dynamically")
    print("  3. Try a more general selector")
    print("  4. Use browser developer tools to verify the selector")

    retry = input("Would you like to try a different selector? (y/n): ").lower()
    if retry == "y":
        new_selector = input("Enter new selector: ").strip()
        return new_selector
    return None


def show_scraping_summary(scraped_data, output_format):
    """
    Show a summary of what was scraped
    """
    print("\nScraping Summary:")
    print(f"  Total selectors processed: {len(scraped_data)}")

    for selector, data in scraped_data.items():
        if data and data[0] != "ERROR: Selector not found":
            print(f"  SUCCESS: {selector}: {len(data)} items")
        else:
            print(f"  FAILED: {selector}: No data found")

    print(f"\nOutput format: {output_format}")

    # Preview first few items
    if any(data for data in scraped_data.values()):
        print("\nPreview of scraped data:")
        for selector, data in scraped_data.items():
            if data and data[0] != "ERROR: Selector not found":
                preview = data[0][:50] + "..." if len(data[0]) > 50 else data[0]
                print(f"  {selector}: {preview}")


if __name__ == "__main__":
    print("Scraplet Interactive Mode")
    print("Type 'help' for usage information")

    # Check for help request
    help_request = input(
        "Enter 'help' for usage info or press Enter to continue: "
    ).strip()
    if help_request.lower() == "help":
        show_help()
        exit(0)

    # Check for saved configuration
    saved_config = load_saved_configurations()
    using_saved_config = False

    if saved_config:
        print(
            f"\nFound saved configuration from {time.ctime(saved_config['timestamp'])}"
        )
        use_saved = input("Use saved configuration? (y/n): ").lower()
        if use_saved == "y":
            url = saved_config["url"]
            selectors = saved_config["selectors"]
            output_choice = saved_config["output_format"]
            using_saved_config = True
            print(f"Using saved config: {url}")
        else:
            url = get_url_from_user()
            selectors = get_selectors_from_user()
            output_choice = get_output_choice()
    else:
        url = get_url_from_user()
        selectors = get_selectors_from_user()
        output_choice = get_output_choice()

    print(f"\nSelected URL: {url}")
    print(f"Selected selectors: {selectors}")
    print(f"Selected output format: {output_choice}")

    # Ask to save configuration only if not using saved config
    if not using_saved_config:
        ask_to_save_config(url, selectors, output_choice)
    else:
        print("\nUsing saved configuration - skipping save prompt.")
