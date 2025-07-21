# Google News Time Filter

A Python script to search for recent Google News results within a specified time frame for any given name or company.

## Features

- Search Google News for any name/company
- Filter results by hours (e.g., last 24 hours, 96 hours)
- Extracts titles and links from search results
- Handles both hourly and daily time filters automatically
- Anti-scraping measures bypass

## Requirements

```bash
pip install requests beautifulsoup4
```

## Usage

1. Run the script:
```bash
python google_results_checker.py
```

2. Enter the name/company you want to search for

3. Enter the number of hours to look back (e.g., 24 for last 24 hours)

4. View the results

## Example

```
Enter the name/company to search: Tesla
Enter hours to check back (e.g., 24 for last 24 hours): 48

Searching for 'Tesla' in the last 48 hours...

Found 8 results from the last 48 hours:
1. Tesla Stock Rises After Strong Q4 Earnings
   https://example.com/tesla-earnings

2. Elon Musk Announces New Tesla Model
   https://example.com/new-tesla-model
```

## How It Works

- Uses Google News search with time-based filters (`qdr:h` for hours, `qdr:d` for days)
- Scrapes search results using BeautifulSoup
- Handles different Google result page layouts
- Filters out duplicate results

## Limitations

- Google may block requests if used excessively
- Results depend on Google's anti-bot measures
- May require VPN or proxy for consistent access
- Limited to top 10 results per search

## Disclaimer

This tool is for educational purposes. Be respectful of Google's terms of service and implement appropriate delays between requests for production use.
