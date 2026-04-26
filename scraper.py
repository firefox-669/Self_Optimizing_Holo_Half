"""
Web Scraper for Extracting Article Titles from News Websites
"""

import requests
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewsArticleScraper:
    """A web scraper to extract article titles from news websites."""
    
    def __init__(self, url: str, selectors: list = None):
        """
        Initialize the scraper.
        
        Args:
            url: The URL of the news website to scrape
            selectors: List of CSS selectors to try for finding article titles
        """
        self.url = url
        self.selectors = selectors or [
            'article h2',
            'article h3',
            '.article-title',
            '.post-title',
            'h2.title',
            '.entry-title',
            'a.headline'
        ]
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def fetch_page(self) -> str:
        """
        Fetch the webpage content.
        
        Returns:
            HTML content as string
        """
        try:
            logger.info(f"Fetching URL: {self.url}")
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            logger.info(f"Successfully fetched page. Status code: {response.status_code}")
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching page: {e}")
            raise
    
    def extract_titles(self, html_content: str) -> list:
        """
        Extract article titles from HTML content.
        
        Args:
            html_content: The HTML content to parse
            
        Returns:
            List of article titles
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        titles = []
        
        # Try each selector until we find titles
        for selector in self.selectors:
            elements = soup.select(selector)
            if elements:
                titles = [elem.get_text(strip=True) for elem in elements if elem.get_text(strip=True)]
                logger.info(f"Found {len(titles)} titles using selector: {selector}")
                break
        
        if not titles:
            # Fallback: try to find any h2 or h3 elements
            for tag in ['h2', 'h3']:
                elements = soup.find_all(tag)
                if elements:
                    titles = [elem.get_text(strip=True) for elem in elements if elem.get_text(strip=True)]
                    logger.info(f"Found {len(titles)} titles using fallback tag: {tag}")
                    break
        
        return titles
    
    def scrape(self) -> list:
        """
        Main method to scrape article titles.
        
        Returns:
            List of article titles
        """
        html_content = self.fetch_page()
        titles = self.extract_titles(html_content)
        return titles


def main():
    """Main function to demonstrate the scraper."""
    # Example usage with a sample news site
    # You can replace this with any news website URL
    sample_urls = [
        'https://news.ycombinator.com/',
        'https://example.com'
    ]
    
    for url in sample_urls:
        print(f"\n{'='*60}")
        print(f"Scraping: {url}")
        print('='*60)
        
        try:
            scraper = NewsArticleScraper(url)
            titles = scraper.scrape()
            
            if titles:
                print(f"\nFound {len(titles)} article titles:\n")
                for i, title in enumerate(titles[:10], 1):  # Show first 10
                    print(f"{i}. {title}")
            else:
                print("No titles found.")
                
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()