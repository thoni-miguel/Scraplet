# Scraplet

**Scraplet** is a powerful CLI tool to extract elements from any webpage using CSS selectors.  
Point it at a URL, tell it what HTML tag or class to look for, and get the results in multiple formats.

## Features

- **Interactive Mode**: User-friendly prompts with validation and help
- **Command Line Mode**: Direct parameter passing for automation
- **Multiple Output Formats**: CSV, Excel, JSON, or terminal display
- **Multiple Selectors**: Extract multiple elements using `||` separator
- **Configuration Management**: Save and load scraping configurations
- **Enhanced Error Handling**: Helpful suggestions when selectors fail
- **URL Validation**: Test URL accessibility before scraping
- **Progress Feedback**: Real-time status updates during scraping
- **Comprehensive Help**: Built-in documentation and examples

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Interactive Mode
```bash
python scraplet.py
```

### Command Line Mode
```bash
python scraplet.py -u https://example.com -s ".title" -o csv
python scraplet.py -u https://example.com -s ".price||.name" -o json
```

### Using Saved Configurations
```bash
python scraplet.py --use-saved        # Use saved configuration
python scraplet.py --list-configs     # List saved configuration details
```

### Help Mode
```bash
python scraplet.py --help-mode
```

## Examples

### Basic Usage
```bash
# Extract all elements with class "product-title"
python scraplet.py -u https://shop.example.com -s ".product-title" -o csv

# Extract multiple elements
python scraplet.py -u https://shop.example.com -s ".price||.title||.description" -o json
```

### Selector Examples
- `.class-name` - Elements with specific class
- `#id-name` - Element with specific ID
- `tag-name` - All elements of that tag
- `parent > child` - Direct child relationship
- `ancestor descendant` - Any descendant
- `[attribute=value]` - Elements with specific attribute

## Output Formats

1. **CSV** - Comma-separated values (output.csv)
2. **Excel** - Excel spreadsheet (output.xlsx)
3. **JSON** - JSON format (output.json)
4. **Terminal** - Display in console

## Configuration Management

Scraplet can save your scraping configurations for future use:
- Automatically prompts to save after successful scraping
- Loads saved configurations on startup
- Useful for repeated scraping tasks

### How to Use Saved Configurations

1. **Save a Configuration**: Run the scraper in interactive mode and choose to save when prompted
2. **Use Saved Configuration**: 
   - Interactive mode: `python scraplet.py` (will prompt to use saved config)
   - Command line: `python scraplet.py --use-saved`
3. **View Saved Configuration**: `python scraplet.py --list-configs`

**Smart Save Behavior**: When using a saved configuration, the app won't prompt you to save again at the end - it only asks to save new configurations.

### Example Workflow
```bash
# First time - save configuration
python scraplet.py
# Enter URL, selectors, output format
# Choose 'y' when asked to save configuration

# Later - use saved configuration
python scraplet.py --use-saved

# Or check what's saved
python scraplet.py --list-configs
```

## Error Handling

When selectors fail, Scraplet provides:
- Clear error messages
- Helpful suggestions
- Option to retry with different selectors
- Detailed troubleshooting tips

## Tips

- Use browser developer tools to find selectors
- Test selectors in browser console with `document.querySelector()`
- Multiple selectors can be combined with `||`
- Save configurations for repeated scraping tasks
- Check URL accessibility before scraping

## Requirements

- Python 3.7+
- Playwright
- Pandas
- Requests
- BeautifulSoup4
- OpenPyXL (for Excel export)

---
