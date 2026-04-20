"""
Database models for book storage.
Books table stores all metadata scraped from websites.
BookChunk stores text chunks for RAG pipeline.
"""

from django.db import models
from django.utils import timezone


class Book(models.Model):
    """
    Primary book model storing all metadata.
    Fields align with assignment requirements:
    title, author, rating, reviews, description, URL.
    """
    
    title = models.CharField(max_length=500)
    author = models.CharField(max_length=300, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    review_count = models.IntegerField(default=0)
    book_url = models.URLField(max_length=1000, unique=True)
    cover_image_url = models.URLField(max_length=1000, blank=True, null=True)
    
    # AI-generated insights (stored to avoid repeated API calls - caching)
    ai_summary = models.TextField(blank=True, null=True)
    ai_genre = models.CharField(max_length=200, blank=True, null=True)
    ai_sentiment = models.CharField(max_length=50, blank=True, null=True)
    
    # Metadata
    source_website = models.CharField(max_length=200, default='goodreads')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_processed = models.BooleanField(default=False)  # RAG processing status
    
    class Meta:
        db_table = 'books'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['author']),
            models.Index(fields=['ai_genre']),
        ]
    
    def __str__(self):
        return f"{self.title} by {self.author}"


class BookChunk(models.Model):
    """
    Stores text chunks for RAG pipeline.
    Each book is split into smaller chunks for embedding and retrieval.
    Uses smart chunking with overlap for better context preservation.
    """
    
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='chunks')
    chunk_text = models.TextField()
    chunk_index = models.IntegerField()  # Order of chunk in document
    embedding_id = models.CharField(max_length=100, blank=True, null=True)  # ChromaDB reference
    
    class Meta:
        db_table = 'book_chunks'
        ordering = ['book', 'chunk_index']
        unique_together = ['book', 'chunk_index']
    
    def __str__(self):
        return f"Chunk {self.chunk_index} of {self.book.title}"


class ChatHistory(models.Model):
    """
    Stores Q&A history for bonus points.
    Enables conversation continuity and analytics.
    """
    
    question = models.TextField()
    answer = models.TextField()
    source_books = models.ManyToManyField(Book, related_name='chat_references')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_history'
        ordering = ['-created_at']
