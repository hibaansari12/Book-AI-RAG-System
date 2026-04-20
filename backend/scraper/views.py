"""
Scraper API Views.

Endpoints:
- POST /api/scraper/scrape/ - Trigger book scraping
- GET /api/scraper/status/ - Check scraping status
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from books.models import Book
from books.serializers import BookCreateSerializer
from .book_scraper import BookScraper
from ai_engine.insight_generator import insight_generator
from ai_engine.rag_pipeline import rag_pipeline


class ScrapeView(APIView):
    """
    POST /api/scraper/scrape/
    
    Trigger web scraping for books.
    """
    
    def post(self, request):
        query = request.data.get('query', 'bestseller books')
        max_books = request.data.get('max_books', 10)
        generate_insights = request.data.get('generate_insights', True)
        
        # Validate
        if max_books > 50:
            max_books = 50  # Limit to prevent abuse
        
        # Scrape
        scraper = BookScraper(headless=True)
        scraped_books = scraper.scrape_open_library_search(query, max_books)
        
        # Save to database
        created_books = []
        errors = []
        
        for book_data in scraped_books:
            serializer = BookCreateSerializer(data=book_data)
            if serializer.is_valid():
                book = serializer.save()
                created_books.append(book)
                
                # Generate insights if requested
                if generate_insights:
                    try:
                        insight_generator.generate_all_insights(book)
                        rag_pipeline.index_book(book)
                    except Exception as e:
                        errors.append(f"Insight generation failed for {book.title}: {str(e)}")
            else:
                errors.append({
                    'title': book_data.get('title'),
                    'errors': serializer.errors
                })
        
        return Response({
            'query': query,
            'books_found': len(scraped_books),
            'books_created': len(created_books),
            'errors': errors,
            'message': f'Successfully scraped and saved {len(created_books)} books'
        })


class BulkScrapeView(APIView):
    """
    POST /api/scraper/bulk-scrape/
    
    Scrape multiple queries for comprehensive collection.
    """
    
    def post(self, request):
        queries = request.data.get('queries', [
            'fiction bestsellers',
            'science fiction',
            'mystery thriller',
            'self help',
            'biography'
        ])
        books_per_query = request.data.get('books_per_query', 5)
        
        scraper = BookScraper(headless=True)
        all_books = scraper.bulk_scrape(queries, books_per_query)
        
        created_count = 0
        for book_data in all_books:
            serializer = BookCreateSerializer(data=book_data)
            if serializer.is_valid():
                book = serializer.save()
                created_count += 1
                
                # Process with AI
                try:
                    insight_generator.generate_all_insights(book)
                    rag_pipeline.index_book(book)
                except:
                    pass
        
        return Response({
            'queries': queries,
            'total_scraped': len(all_books),
            'books_created': created_count
        })
