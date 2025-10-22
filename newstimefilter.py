import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import time
import random
import logging
from typing import List, Dict, Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('google_news_search.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GoogleNewsSearcher:
    """Enhanced Google News Searcher with anti-detection and improved parsing"""
    
    CONFIG = {
        'MAX_RESULTS': 15,
        'TIMEOUT': 12,
        'DELAY_RANGE': (2, 5),
        'USER_AGENTS': [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
    }
    
    SELECTORS = {
        'primary': [
            ['h3', lambda x: x and any(cls in str(x) for cls in ['LC20lb', 'BNeawe', 'n0jPhd', 'ynAwRc', 'WUxB0c', 'DB1d3'])],
            ['div', lambda x: x and any(cls in str(x) for cls in ['BNeawe', 'n0jPhd', 'ynAwRc', 'WUxB0c'])]
        ],
        'secondary': [
            ['a', lambda x: x and 'href' in x and any(cls in str(x) for cls in ['lRVwie', 'VFACy', 'DB1d3'])]
        ]
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self._get_base_headers())
        self.search_count = 0
    
    def _get_base_headers(self) -> Dict[str, str]:
        """Dynamic headers with random user agent"""
        return {
            'User-Agent': random.choice(self.CONFIG['USER_AGENTS']),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1'
        }
    
    def _anti_detection_delay(self):
        """Smart delay between requests"""
        self.search_count += 1
        if self.search_count > 1:
            delay = random.uniform(*self.CONFIG['DELAY_RANGE'])
            logger.info(f"Anti-detection delay: {delay:.1f}s")
            time.sleep(delay)
    
    def _extract_enhanced_data(self, soup: BeautifulSoup, result_element: Any) -> Dict[str, str]:
        """Extract title, link, source, time, and snippet"""
        data = {}
        
        # Title
        title_elem = result_element.find(['h3', 'h4']) or result_element
        data['title'] = title_elem.get_text().strip()
        
        # Link
        parent_a = result_element.find_parent('a') or result_element.find('a')
        link = parent_a.get('href') if parent_a else None
        
        if link:
            if link.startswith('/url?q='):
                link = link.split('/url?q=')[1].split('&')[0]
            elif link.startswith('/search'):
                link = None
            elif not link.startswith('http'):
                link = 'https://www.google.com' + link
        
        data['link'] = link or ''
        
        # Source
        source_elem = result_element.find(class_=lambda x: x and any(
            word in str(x).lower() for word in ['source', 'publisher']
        ))
        data['source'] = source_elem.get_text().strip() if source_elem else 'Unknown'
        
        # Time
        time_elem = result_element.find(class_=lambda x: x and 'time' in str(x).lower())
        data['time'] = time_elem.get_text().strip() if time_elem else ''
        
        # Snippet
        snippet_elem = result_element.find_next_sibling('div') or \
                      result_element.find(class_=lambda x: x and 'snippet' in str(x).lower())
        data['snippet'] = snippet_elem.get_text().strip() if snippet_elem else ''
        
        return data
    
    def search(self, query: str, hours: int, max_results: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Enhanced Google News search with time filter
        
        Args:
            query: Search query
            hours: Hours to look back
            max_results: Max results to return
            
        Returns:
            List of enhanced result dictionaries
        """
        max_results = max_results or self.CONFIG['MAX_RESULTS']
        
        self._anti_detection_delay()
        
        encoded_query = quote_plus(query)
        
        # Time filter
        if hours <= 24:
            time_param = f"qdr:h{hours}"
        else:
            days = hours // 24
            time_param = f"qdr:d{days}"
        
        url = f"https://www.google.com/search?q={encoded_query}&tbs={time_param}&tbm=nws"
        
        logger.info(f"Searching: '{query}' for last {hours}h | URL: {url}")
        
        try:
            # Rotate headers for each request
            self.session.headers.update(self._get_base_headers())
            
            response = self.session.get(url, timeout=self.CONFIG['TIMEOUT'])
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            all_results = []
            
            # Primary parsing strategy
            for tag_name, class_matcher in self.SELECTORS['primary']:
                for result in soup.find_all(tag_name, class_=class_matcher):
                    if result.get_text().strip():
                        enhanced_data = self._extract_enhanced_data(soup, result)
                        if enhanced_data['title'] and enhanced_data['link']:
                            all_results.append(enhanced_data)
            
            # Secondary parsing strategy (fallback)
            if len(all_results) < 5:
                logger.info("Using secondary parsing strategy")
                for tag_name, class_matcher in self.SELECTORS['secondary']:
                    for result in soup.find_all(tag_name, class_=class_matcher):
                        if result.get_text().strip():
                            enhanced_data = self._extract_enhanced_data(soup, result)
                            if enhanced_data['title'] and enhanced_data['link']:
                                all_results.append(enhanced_data)
            
            # Remove duplicates preserving order
            seen_links = set()
            unique_results = []
            for result in all_results:
                if result['link'] not in seen_links:
                    seen_links.add(result['link'])
                    unique_results.append(result)
            
            final_results = unique_results[:max_results]
            
            logger.info(f"Found {len(final_results)} unique results")
            return final_results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error: {e}")
            return []
        except Exception as e:
            logger.error(f"Parsing error: {e}")
            return []

def main():
    """Enhanced CLI interface"""
    print("=" * 70)
    print("🚀 ENHANCED GOOGLE NEWS TIME FILTER SEARCHER")
    print("=" * 70)
    
    searcher = GoogleNewsSearcher()
    
    try:
        name = input("\n🔍 Enter name/company to search: ").strip()
        if not name:
            print("❌ Error: Search query cannot be empty!")
            return
        
        hours_input = input("⏰ Enter hours to check back (e.g., 24): ").strip()
        hours = int(hours_input)
        if hours <= 0:
            print("❌ Error: Hours must be positive!")
            return
        
        print(f"\n🔎 Searching '{name}' in last {hours} hours...")
        print("⏳ Please wait (anti-detection active)...")
        print("-" * 70)
        
        results = searcher.search(name, hours)
        
        if results:
            print(f"\n✅ Found {len(results)} results:\n")
            print("📋 RESULTS:")
            print("-" * 70)
            
            for i, result in enumerate(results, 1):
                print(f"{i:2d}. {result['title']}")
                print(f"     🔗 {result['link']}")
                if result.get('source'):
                    print(f"     📰 {result['source']}")
                if result.get('time'):
                    print(f"     🕐 {result['time']}")
                if result.get('snippet'):
                    print(f"     💬 {result['snippet'][:100]}...")
                print()
        else:
            print("\n❌ No results found")
            print("\n🔧 Troubleshooting:")
            print("• Try broader time range")
            print("• Check logs: google_news_search.log")
            print("• Use VPN if blocked")
        
        print("-" * 70)
        
    except ValueError:
        print("❌ Error: Invalid number for hours!")
    except KeyboardInterrupt:
        print("\n\n⏹️ Search cancelled by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
