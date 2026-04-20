
#AI Engine API Views.

#Endpoints:
#- POST /api/ai/ask/ - RAG question-answering
#- POST /api/ai/generate-insights/ - Generate insights for a book
#- POST /api/ai/index-book/ - Index book for RAG


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache

from books.models import Book, ChatHistory
from .rag_pipeline import rag_pipeline
from .insight_generator import insight_generator


class AskQuestionView(APIView):
    """
    POST /api/ai/ask/
    
    RAG-powered question answering about books.
    Implements caching for repeated questions.
    """
    
    def post(self, request):
        question = request.data.get('question', '').strip()
        
        if not question:
            return Response(
                {'error': 'Question is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check cache for this question
        cache_key = f"rag_answer_{hash(question)}"
        cached_response = cache.get(cache_key)
        
        if cached_response:
            return Response({
                **cached_response,
                'cached': True
            })
        
        # Get answer from RAG pipeline
        result = rag_pipeline.ask(question)
        
        # Save to chat history
        chat_entry = ChatHistory.objects.create(
            question=question,
            answer=result['answer']
        )
        
        # Link source books
        for source in result['sources']:
            try:
                book = Book.objects.get(id=source['book_id'])
                chat_entry.source_books.add(book)
            except Book.DoesNotExist:
                pass
        
        # Cache the response for 30 minutes
        cache.set(cache_key, result, 1800)
        
        return Response({
            **result,
            'cached': False,
            'chat_id': chat_entry.id
        })


class GenerateInsightsView(APIView):
    """
    POST /api/ai/generate-insights/
    
    Generate AI insights (summary, genre, sentiment) for a book.
    """
    
    def post(self, request):
        book_id = request.data.get('book_id')
        
        if not book_id:
            return Response(
                {'error': 'book_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response(
                {'error': 'Book not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Generate insights
        insights = insight_generator.generate_all_insights(book)
        
        return Response({
            'book_id': book.id,
            'book_title': book.title,
            'insights': insights,
            'message': 'Insights generated successfully'
        })


class IndexBookView(APIView):
    """
    POST /api/ai/index-book/
    
    Index a book for RAG retrieval.
    Chunks the book content and stores embeddings.
    """
    
    def post(self, request):
        book_id = request.data.get('book_id')
        
        if not book_id:
            return Response(
                {'error': 'book_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response(
                {'error': 'Book not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Index the book
        chunks_count = rag_pipeline.index_book(book)
        
        return Response({
            'book_id': book.id,
            'book_title': book.title,
            'chunks_created': chunks_count,
            'message': 'Book indexed successfully for RAG'
        })


class BatchProcessView(APIView):
    """
    POST /api/ai/batch-process/
    
    Process multiple books - generate insights and index for RAG.
    Useful after bulk scraping.
    """
    
    def post(self, request):
        # Get unprocessed books
        unprocessed_books = Book.objects.filter(is_processed=False)[:10]
        
        results = []
        for book in unprocessed_books:
            try:
                # Generate insights
                insights = insight_generator.generate_all_insights(book)
                
                # Index for RAG
                chunks = rag_pipeline.index_book(book)
                
                results.append({
                    'book_id': book.id,
                    'title': book.title,
                    'status': 'success',
                    'chunks': chunks
                })
            except Exception as e:
                results.append({
                    'book_id': book.id,
                    'title': book.title,
                    'status': 'error',
                    'error': str(e)
                })
        
        return Response({
            'processed': len(results),
            'results': results
        })

