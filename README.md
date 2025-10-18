# Google News Time Filter

A Python script to search for recent Google News results within a specified time frame for any given name or company.

## Features

- Search Google News for any name/company
- Filter results by hours (e.g., last 24 hours, 96 hours)
- Extracts titles and links from search results
- Handles both hourly and daily time filters automatically
- Anti-scraping measures bypass

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

## Limitations

- Google may block requests if used excessively
- Results depend on Google's anti-bot measures
- May require VPN or proxy for consistent access
- Limited to top 10 results per search

## Disclaimer

This tool is for educational purposes. Be respectful of Google's terms of service and implement appropriate delays between requests for production use.
