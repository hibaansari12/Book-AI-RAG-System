"""
AI Insight Generation Module.

Generates:
1. Book summaries
2. Genre classification
3. Sentiment analysis of descriptions/reviews
4. Recommendation reasoning

Uses LM Studio (local) or OpenAI API.
"""

from openai import OpenAI
from django.conf import settings
from django.core.cache import cache
import hashlib
import json


class InsightGenerator:
    """
    Generates AI-powered insights for books.
    Implements caching to avoid repeated API calls (bonus requirement).
    """
    
    def __init__(self, use_lm_studio: bool = True):
        self.use_lm_studio = use_lm_studio
        
        if use_lm_studio:
            self.client = OpenAI(
                base_url=settings.LM_STUDIO_URL,
                api_key="not-needed"
            )
            self.model = "local-model"
        else:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = "gpt-3.5-turbo"
    
    def _get_cache_key(self, prefix: str, text: str) -> str:
        """Generate cache key for insight."""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return f"ai_insight_{prefix}_{text_hash}"
    
    def _call_llm(self, prompt: str, max_tokens: int = 500) -> str:
        """Make LLM API call."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error: {str(e)}"
    
    def generate_summary(self, title: str, author: str, description: str) -> str:
        """
        Generate a concise summary of the book.
        
        Returns a 2-3 sentence summary highlighting key themes.
        """
        cache_key = self._get_cache_key("summary", f"{title}{description}")
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        prompt = f"""Generate a concise 2-3 sentence summary for this book:

Title: {title}
Author: {author or 'Unknown'}
Description: {description or 'No description available'}

Summary:"""
        
        result = self._call_llm(prompt, max_tokens=200)
        cache.set(cache_key, result, 86400)  # Cache for 24 hours
        return result
    
    def classify_genre(self, title: str, description: str) -> str:
        """
        Predict genre(s) based on title and description.
        
        Returns comma-separated genres (e.g., "Fiction, Mystery, Thriller").
        """
        cache_key = self._get_cache_key("genre", f"{title}{description}")
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        prompt = f"""Classify this book into 1-3 genres from this list:
Fiction, Non-Fiction, Mystery, Thriller, Romance, Science Fiction, Fantasy, 
Horror, Biography, History, Self-Help, Business, Science, Philosophy, Poetry,
Young Adult, Children's, Classics, Contemporary

Title: {title}
Description: {description or 'No description'}

Respond with only the genre names, comma-separated:"""
        
        result = self._call_llm(prompt, max_tokens=50)
        cache.set(cache_key, result, 86400)
        return result
    
    def analyze_sentiment(self, description: str) -> str:
        """
        Analyze the tone/sentiment of book description or reviews.
        
        Returns: Positive, Negative, Neutral, or Mixed
        """
        if not description:
            return "Unknown"
        
        cache_key = self._get_cache_key("sentiment", description)
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        prompt = f"""Analyze the overall tone of this book description:

"{description[:500]}"

Classify as one of: Positive, Negative, Neutral, or Mixed
Respond with only the classification:"""
        
        result = self._call_llm(prompt, max_tokens=20)
        
        # Normalize result
        result = result.strip().lower()
        if 'positive' in result:
            result = 'Positive'
        elif 'negative' in result:
            result = 'Negative'
        elif 'mixed' in result:
            result = 'Mixed'
        else:
            result = 'Neutral'
        
        cache.set(cache_key, result, 86400)
        return result
    
    def generate_all_insights(self, book) -> dict:
        """
        Generate all insights for a book.
        Updates the book model with results.
        
        Args:
            book: Book model instance
            
        Returns:
            Dict with all generated insights
        """
        insights = {}
        
        # Summary
        insights['summary'] = self.generate_summary(
            book.title, 
            book.author, 
            book.description
        )
        book.ai_summary = insights['summary']
        
        # Genre
        insights['genre'] = self.classify_genre(
            book.title, 
            book.description
        )
        book.ai_genre = insights['genre']
        
        # Sentiment
        insights['sentiment'] = self.analyze_sentiment(book.description)
        book.ai_sentiment = insights['sentiment']
        
        book.save()
        
        return insights


# Singleton instance
insight_generator = InsightGenerator()
