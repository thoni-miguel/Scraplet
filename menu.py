def get_url_from_user():
    """
    Prompt the user to enter a URL
    """
    print("Welcome to Scraplet!")
    print("Please enter the URL you want to scrape:")

    while True:
        url = input("URL: ").strip()

        if url:
            # Basic URL validation
            if url.startswith(("http://", "https://")):
                return url
            else:
                print("Please enter a valid URL starting with http:// or https://")
        else:
            print("URL cannot be empty. Please try again.")


def get_selectors_from_user():
    """
    Prompt the user to enter one or more CSS selectors.
    """
    print("Please enter the CSS selector(s) you want to use.")
    print("You can enter multiple selectors separated by '||' (double pipe).")

    while True:
        selectors = input("Selector(s): ").strip()
        if selectors:
            return selectors
        else:
            print("Selectors cannot be empty. Please try again.")


def get_output_choice():
    """
    Prompt the user to select an output format.
    """
    print("How would you like to output the results?")
    print("  1 - Export to CSV")
    print("  2 - Export to Excel")
    print("  3 - Export to JSON")
    print("  4 - Log to terminal")

    while True:
        choice = input("Select an option (1-4): ").strip()
        if choice == "1":
            return "csv"
        elif choice == "2":
            return "excel"
        elif choice == "3":
            return "json"
        elif choice == "4":
            return "terminal"
        else:
            print("Invalid option. Please select a number between 1 and 4.")


if __name__ == "__main__":
    url = get_url_from_user()
    print(f"Selected URL: {url}")

    selectors = get_selectors_from_user()
    print(f"Selected selectors: {selectors}")

    output_choice = get_output_choice()
    print(f"Selected output format: {output_choice}")
