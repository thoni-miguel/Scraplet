import argparse
import requests
from bs4 import BeautifulSoup


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

response = requests.get(args.url)
soup = BeautifulSoup(response.text, "html.parser")

elements = soup.select(args.selector)

print("Elements found")
for element in elements:
    print(element.get_text(strip=True))
