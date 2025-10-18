import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import time

def search_google_news(query, hours):
    """
    Search Google News for a query within specified hours
    
    Args:
        query: Name or company to search for
        hours: Number of hours to look back
    
    Returns:
        List of dictionaries containing title and link
    """
    # Enhanced headers to mimic a real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    encoded_query = quote_plus(query)
    
    # Determine time filter - FIXED: using tbs parameter
    if hours <= 24:
        time_param = f"qdr:h{hours}"
    else:
        days = hours // 24
        time_param = f"qdr:d{days}"
    
    # Correct URL construction with tbs parameter
    url = f"https://www.google.com/search?q={encoded_query}&tbs={time_param}&tbm=nws"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Use response.content for better encoding handling
        soup = BeautifulSoup(response.content, 'html.parser')
        
        results = []
        
        # Primary strategy: Multiple CSS class targeting
        for result in soup.find_all(['h3', 'div'], class_=lambda x: x and any(cls in str(x) for cls in ['LC20lb', 'BNeawe', 'n0jPhd', 'ynAwRc'])):
            if result.get_text().strip():
                parent = result.find_parent('a')
                link = parent.get('href') if parent else None
                
                # Clean up Google redirect links
                if link and link.startswith('/url?q='):
                    link = link.split('/url?q=')[1].split('&')[0]
                elif link and not link.startswith('http'):
                    link = 'https://www.google.com' + link
                
                if link:
                    results.append({
                        'title': result.get_text().strip(),
                        'link': link
                    })
        
        # Fallback strategy: If primary method fails
        if not results:
            for result in soup.find_all('a'):
                h3 = result.find('h3')
                if h3:
                    link = result.get('href', '')
                    
                    # Clean up link
                    if link.startswith('/url?q='):
                        link = link.split('/url?q=')[1].split('&')[0]
                    elif link and not link.startswith('http'):
                        continue  # Skip invalid links
                    
                    if link and link.startswith('http'):
                        results.append({
                            'title': h3.get_text().strip(),
                            'link': link
                        })
        
        # Remove duplicates while preserving order
        seen = set()
        unique_results = []
        for r in results:
            if r['link'] not in seen:
                seen.add(r['link'])
                unique_results.append(r)
        
        return unique_results[:10]
        
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return []
    except Exception as e:
        print(f"Error parsing results: {e}")
        return []

def main():
    """Main function to run the Google News search"""
    print("=" * 60)
    print("Google News Time Filter")
    print("=" * 60)
    
    try:
        name = input("\nEnter the name/company to search: ").strip()
        
        if not name:
            print("Error: Search query cannot be empty!")
            return
        
        hours = int(input("Enter hours to check back (e.g., 24 for last 24 hours): ").strip())
        
        if hours <= 0:
            print("Error: Hours must be a positive number!")
            return
        
        print(f"\nSearching for '{name}' in the last {hours} hours...")
        print("-" * 60)
        
        results = search_google_news(name, hours)
        
        if results:
            print(f"\nFound {len(results)} results from the last {hours} hours:\n")
            for i, result in enumerate(results, 1):
                print(f"{i}. {result['title']}")
                print(f"   {result['link']}\n")
        else:
            print(f"\nNo results found for '{name}' in the last {hours} hours")
            print("\nPossible reasons:")
            print("- Google may be blocking automated requests")
            print("- No news articles in the specified time frame")
            print("- Rate limiting or CAPTCHA required")
            print("\nTips:")
            print("- Wait a few minutes before trying again")
            print("- Use a VPN or proxy")
            print("- Try a different time range")
        
        print("-" * 60)
        
    except ValueError:
        print("Error: Please enter a valid number for hours!")
    except KeyboardInterrupt:
        print("\n\nSearch cancelled by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
