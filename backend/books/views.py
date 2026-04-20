"""
API Views for book operations.
Implements all required GET and POST endpoints.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from django.core.cache import cache

from .models import Book, ChatHistory
from .serializers import (
    BookListSerializer, 
    BookDetailSerializer,
    BookCreateSerializer,
    ChatHistorySerializer
)


class BookViewSet(viewsets.ModelViewSet):
    """
    ViewSet providing CRUD operations for books.
    
    GET /api/books/ - List all books (paginated)
    GET /api/books/{id}/ - Get single book details
    POST /api/books/ - Create/upload new book
    GET /api/books/{id}/recommendations/ - Get related books
    """
    
    queryset = Book.objects.all()
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return BookListSerializer
        elif self.action == 'create':
            return BookCreateSerializer
        return BookDetailSerializer
    
    def list(self, request):
        """
        GET /api/books/
        Lists all books with optional filtering.
        Supports: ?search=, ?genre=, ?min_rating=
        """
        queryset = self.get_queryset()
        
        # Search filter
        search = request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(author__icontains=search)
            )
        
        # Genre filter
        genre = request.query_params.get('genre', None)
        if genre:
            queryset = queryset.filter(ai_genre__icontains=genre)
        
        # Rating filter
        min_rating = request.query_params.get('min_rating', None)
        if min_rating:
            queryset = queryset.filter(rating__gte=float(min_rating))
        
        # Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def recommendations(self, request, pk=None):
        """
        GET /api/books/{id}/recommendations/
        Returns related books based on genre and author.
        Implements "If you like X, you'll like Y" logic.
        """
        book = self.get_object()
        
        # Cache key for recommendations
        cache_key = f"book_recommendations_{pk}"
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)
        
        # Find similar books by genre and author
        similar_books = Book.objects.exclude(id=book.id)
        
        if book.ai_genre:
            # Primary: Same genre
            genre_matches = similar_books.filter(
                ai_genre__icontains=book.ai_genre.split(',')[0].strip()
            )[:5]
        else:
            genre_matches = Book.objects.none()
        
        if book.author:
            # Secondary: Same author
            author_matches = similar_books.filter(
                author__icontains=book.author.split()[0]
            ).exclude(id__in=genre_matches)[:3]
        else:
            author_matches = Book.objects.none()
        
        # Combine and serialize
        recommendations = list(genre_matches) + list(author_matches)
        serializer = BookListSerializer(recommendations[:8], many=True)
        
        # Cache for 1 hour
        cache.set(cache_key, serializer.data, 3600)
        
        return Response({
            'book_id': book.id,
            'book_title': book.title,
            'recommendations': serializer.data,
            'recommendation_reason': f"Based on genre: {book.ai_genre}"
        })


class BulkBookUploadView(APIView):
    """
    POST /api/books/bulk/
    Handles bulk book upload from scraper.
    """
    
    def post(self, request):
        books_data = request.data.get('books', [])
        created_count = 0
        errors = []
        
        for book_data in books_data:
            serializer = BookCreateSerializer(data=book_data)
            if serializer.is_valid():
                serializer.save()
                created_count += 1
            else:
                errors.append({
                    'title': book_data.get('title', 'Unknown'),
                    'errors': serializer.errors
                })
        
        return Response({
            'message': f'Successfully created {created_count} books',
            'created': created_count,
            'errors': errors
        }, status=status.HTTP_201_CREATED)


class ChatHistoryView(APIView):
    """
    GET /api/books/chat-history/
    Returns recent Q&A history.
    """
    
    def get(self, request):
        history = ChatHistory.objects.all()[:50]
        serializer = ChatHistorySerializer(history, many=True)
        return Response(serializer.data)
