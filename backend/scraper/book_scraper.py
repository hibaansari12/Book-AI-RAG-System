"""
Web Scraper for Book Data Collection.

Uses Selenium for automation to scrape book information.
Currently configured for Open Library (free, no auth required).
Easily adaptable for Goodreads, Amazon, etc.
"""

import time
import random
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class BookScraper:
    """
    Selenium-based book scraper.
    
    Features:
    - Headless Chrome for server deployment
    - Smart waiting for dynamic content
    - Error handling and retry logic
    - Rate limiting to avoid blocks
    """
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None
    
    def _init_driver(self):
        """Initialize Chrome WebDriver with options."""
        options = Options()
        
        if self.headless:
            options.add_argument('--headless')
        
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.implicitly_wait(10)
    
    def _close_driver(self):
        """Close WebDriver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def _random_delay(self, min_sec: float = 1, max_sec: float = 3):
        """Random delay to mimic human behavior."""
        time.sleep(random.uniform(min_sec, max_sec))
    
    def scrape_open_library_search(self, query: str, max_books: int = 20) -> List[Dict]:
        """
        Scrape books from Open Library search results.
        
        Args:
            query: Search term (e.g., "python programming", "science fiction")
            max_books: Maximum number of books to scrape
            
        Returns:
            List of book dictionaries
        """
        books = []
        
        try:
            self._init_driver()
            
            # Navigate to search page
            search_url = f"[openlibrary search](https://openlibrary.org/search?q={query.replace(' ', '+')})"
            self.driver.get(search_url)
            
            self._random_delay(2, 4)
            
            # Wait for results to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "searchResultItem"))
            )
            
            # Get page source and parse with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Find all book items
            book_items = soup.find_all('li', class_='searchResultItem')[:max_books]
            
            for item in book_items:
                try:
                    book_data = self._parse_open_library_item(item)
                    if book_data:
                        books.append(book_data)
                        logger.info(f"Scraped: {book_data['title']}")
                except Exception as e:
                    logger.error(f"Error parsing book item: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Scraping error: {e}")
        finally:
            self._close_driver()
        
        return books
    
    def _parse_open_library_item(self, item) -> Optional[Dict]:
        """Parse a single book item from Open Library."""
        try:
            # Title
            title_elem = item.find('h3', class_='booktitle')
            if not title_elem:
                return None
            
            title_link = title_elem.find('a')
            title = title_link.get_text(strip=True) if title_link else None
            
            if not title:
                return None
            
            # Book URL
            book_path = title_link.get('href', '') if title_link else ''
            book_url = f"[openlibrary.org{book_path}](https://openlibrary.org{book_path})" if book_path else ''
            
            # Author
            author_elem = item.find('span', class_='bookauthor')
            author = None
            if author_elem:
                author_link = author_elem.find('a')
                author = author_link.get_text(strip=True) if author_link else author_elem.get_text(strip=True)
            
            # Description / First sentence
            desc_elem = item.find('span', class_='book-desc')
            description = desc_elem.get_text(strip=True) if desc_elem else None
            
            # Cover image
            cover_elem = item.find('img', class_='cover')
            cover_url = None
            if cover_elem:
                cover_url = cover_elem.get('src', '')
                if cover_url and not cover_url.startswith('http'):
                    cover_url = f"https:{cover_url}"
            
            # Rating (Open Library doesn't always have this)
            rating = None
            rating_elem = item.find('span', class_='rating')
            if rating_elem:
                try:
                    rating = float(rating_elem.get_text(strip=True))
                except:
                    pass
            
            return {
                'title': title,
                'author': author,
                'description': description,
                'rating': rating,
                'review_count': 0,
                'book_url': book_url,
                'cover_image_url': cover_url,
                'source_website': 'openlibrary'
            }
            
        except Exception as e:
            logger.error(f"Parse error: {e}")
            return None
    
    def scrape_book_details(self, book_url: str) -> Optional[Dict]:
        """
        Scrape detailed information from a book's page.
        
        Used for getting more info about a specific book.
        """
        try:
            self._init_driver()
            self.driver.get(book_url)
            self._random_delay(2, 4)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Get extended description
            desc_elem = soup.find('div', class_='book-description')
            description = desc_elem.get_text(strip=True) if desc_elem else None
            
            # Get subjects/genres
            subjects = []
            subject_elems = soup.find_all('a', {'data-ol-link-track': 'subject'})
            for subj in subject_elems[:5]:
                subjects.append(subj.get_text(strip=True))
            
            return {
                'description': description,
                'subjects': ', '.join(subjects)
            }
            
        except Exception as e:
            logger.error(f"Detail scrape error: {e}")
            return None
        finally:
            self._close_driver()
    
    def bulk_scrape(self, queries: List[str], books_per_query: int = 10) -> List[Dict]:
        """
        Scrape multiple queries for bulk collection.
        
        Args:
            queries: List of search terms
            books_per_query: Books to scrape per query
            
        Returns:
            All scraped books
        """
        all_books = []
        
        for query in queries:
            logger.info(f"Scraping query: {query}")
            books = self.scrape_open_library_search(query, books_per_query)
            all_books.extend(books)
            self._random_delay(5, 10)  # Longer delay between queries
        
        # Remove duplicates by URL
        seen_urls = set()
        unique_books = []
        for book in all_books:
            if book['book_url'] not in seen_urls:
                seen_urls.add(book['book_url'])
                unique_books.append(book)
        
        return unique_books


# Singleton instance
scraper = BookScraper()
