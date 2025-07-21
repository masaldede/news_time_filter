import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import time
import random

def get_google_results_with_time(query, hours):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    encoded_query = quote_plus(query)
    
    if hours <= 24:
        time_param = f"qdr:h{hours}"
    else:
        days = hours // 24
        time_param = f"qdr:d{days}"
    
    url = f"https://www.google.com/search?q={encoded_query}&tbs={time_param}&tbm=nws"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        results = []
        
        for result in soup.find_all(['h3', 'div'], class_=lambda x: x and ('LC20lb' in str(x) or 'BNeawe' in str(x) or 'n0jPhd' in str(x))):
            if result.get_text().strip():
                parent = result.find_parent('a')
                link = parent.get('href') if parent else 'No link'
                if link and link.startswith('/url?q='):
                    link = link.split('/url?q=')[1].split('&')[0]
                results.append({
                    'title': result.get_text().strip(),
                    'link': link
                })
        
        if not results:
            for result in soup.find_all('a'):
                h3 = result.find('h3')
                if h3:
                    link = result.get('href', 'No link')
                    if link.startswith('/url?q='):
                        link = link.split('/url?q=')[1].split('&')[0]
                    results.append({
                        'title': h3.get_text().strip(),
                        'link': link
                    })
        
        return results[:10]
        
    except Exception as e:
        print(f"Error fetching results: {e}")
        return []

def check_recent_results():
    name = input("Enter the name/company to search: ")
    hours = int(input("Enter hours to check back (e.g., 24 for last 24 hours): "))
    
    print(f"\nSearching for '{name}' in the last {hours} hours...")
    
    results = get_google_results_with_time(name, hours)
    
    if results:
        print(f"\nFound {len(results)} results from the last {hours} hours:")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            if result['link'] != 'No link':
                print(f"   {result['link']}")
            print()
    else:
        print(f"\nNo results found for '{name}' in the last {hours} hours")
        print("This might be due to Google's anti-scraping measures or rate limiting.")

if __name__ == "__main__":
    check_recent_results()
