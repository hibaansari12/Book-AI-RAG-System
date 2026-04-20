"""
DRF Serializers for converting model instances to JSON.
Handles validation and nested representations.
"""

from rest_framework import serializers
from .models import Book, BookChunk, ChatHistory


class BookListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for book listing.
    Returns only essential fields for dashboard display.
    """
    
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'rating', 
            'review_count', 'cover_image_url', 'ai_genre'
        ]


class BookDetailSerializer(serializers.ModelSerializer):
    """
    Full serializer with all book details including AI insights.
    Used for individual book pages.
    """
    
    chunks_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = '__all__'
    
    def get_chunks_count(self, obj):
        """Returns number of RAG chunks for this book."""
        return obj.chunks.count()


class BookCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/uploading books.
    Validates required fields.
    """
    
    class Meta:
        model = Book
        fields = [
            'title', 'author', 'description', 'rating',
            'review_count', 'book_url', 'cover_image_url', 'source_website'
        ]
    
    def validate_book_url(self, value):
        """Ensure URL is unique."""
        if Book.objects.filter(book_url=value).exists():
            raise serializers.ValidationError("Book with this URL already exists.")
        return value


class ChatHistorySerializer(serializers.ModelSerializer):
    """Serializer for chat history display."""
    
    source_books = BookListSerializer(many=True, read_only=True)
    
    class Meta:
        model = ChatHistory
        fields = ['id', 'question', 'answer', 'source_books', 'created_at']
