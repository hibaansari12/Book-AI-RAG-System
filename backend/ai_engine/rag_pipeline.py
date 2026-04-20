"""
RAG (Retrieval-Augmented Generation) Pipeline Implementation.

This module handles:
1. Text chunking with overlap (smart chunking)
2. Embedding generation using Sentence Transformers
3. Vector storage in ChromaDB
4. Similarity search for question answering
5. Context construction and LLM response generation
"""

import os
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from django.conf import settings
import hashlib

# Initialize embedding model (runs locally - no API needed)
# all-MiniLM-L6-v2 is fast and effective for semantic search
EMBEDDING_MODEL = SentenceTransformer('all-MiniLM-L6-v2')

# ChromaDB client for vector storage
CHROMA_CLIENT = chromadb.PersistentClient(
    path=str(settings.CHROMA_PERSIST_DIR),
    settings=Settings(anonymized_telemetry=False)
)

# Get or create the books collection
BOOKS_COLLECTION = CHROMA_CLIENT.get_or_create_collection(
    name="book_chunks",
    metadata={"description": "Book text chunks for RAG"}
)


class TextChunker:
    """
    Smart text chunking with configurable size and overlap.
    Overlap ensures context isn't lost at chunk boundaries.
    """
    
    def __init__(self, chunk_size: int = 500, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Strategy: Semantic chunking - tries to break at sentence boundaries
        when possible, maintaining overlap for context continuity.
        """
        if not text:
            return []
        
        # Clean text
        text = ' '.join(text.split())
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to find sentence boundary near the end
            if end < len(text):
                # Look for period, exclamation, or question mark
                boundary = text.rfind('. ', start + self.chunk_size - 100, end)
                if boundary == -1:
                    boundary = text.rfind('! ', start + self.chunk_size - 100, end)
                if boundary == -1:
                    boundary = text.rfind('? ', start + self.chunk_size - 100, end)
                if boundary != -1:
                    end = boundary + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start with overlap
            start = end - self.overlap if end < len(text) else len(text)
        
        return chunks


class RAGPipeline:
    """
    Complete RAG pipeline for book question-answering.
    
    Flow:
    1. User asks question
    2. Generate embedding for question
    3. Search ChromaDB for similar chunks
    4. Construct context from top chunks
    5. Send to LLM with context
    6. Return answer with citations
    """
    
    def __init__(self):
        self.chunker = TextChunker()
        self.collection = BOOKS_COLLECTION
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text."""
        return EMBEDDING_MODEL.encode(text).tolist()
    
    def index_book(self, book) -> int:
        """
        Process and index a book for RAG.
        
        Args:
            book: Book model instance
            
        Returns:
            Number of chunks created
        """
        from books.models import BookChunk
        
        # Combine all book text for chunking
        full_text = f"""
        Title: {book.title}
        Author: {book.author or 'Unknown'}
        Description: {book.description or ''}
        Rating: {book.rating or 'N/A'}
        Genre: {book.ai_genre or 'Unknown'}
        Summary: {book.ai_summary or ''}
        """
        
        # Generate chunks
        chunks = self.chunker.chunk_text(full_text)
        
        # Store in ChromaDB and database
        for idx, chunk_text in enumerate(chunks):
            # Generate unique ID
            chunk_id = hashlib.md5(
                f"{book.id}_{idx}_{chunk_text[:50]}".encode()
            ).hexdigest()
            
            # Generate embedding
            embedding = self.generate_embedding(chunk_text)
            
            # Add to ChromaDB
            self.collection.add(
                ids=[chunk_id],
                embeddings=[embedding],
                documents=[chunk_text],
                metadatas=[{
                    'book_id': str(book.id),
                    'book_title': book.title,
                    'chunk_index': idx
                }]
            )
            
            # Save chunk reference in MySQL
            BookChunk.objects.update_or_create(
                book=book,
                chunk_index=idx,
                defaults={
                    'chunk_text': chunk_text,
                    'embedding_id': chunk_id
                }
            )
        
        # Mark book as processed
        book.is_processed = True
        book.save()
        
        return len(chunks)
    
    def search_similar(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search for chunks similar to the query.
        
        Args:
            query: User's question
            top_k: Number of results to return
            
        Returns:
            List of relevant chunks with metadata
        """
        # Generate query embedding
        query_embedding = self.generate_embedding(query)
        
        # Search ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=['documents', 'metadatas', 'distances']
        )
        
        # Format results
        chunks = []
        if results and results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                chunks.append({
                    'text': doc,
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i]
                })
        
        return chunks
    
    def construct_context(self, chunks: List[Dict]) -> str:
        """Build context string from retrieved chunks."""
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            book_title = chunk['metadata'].get('book_title', 'Unknown')
            context_parts.append(
                f"[Source {i}: {book_title}]\n{chunk['text']}"
            )
        return "\n\n".join(context_parts)
    
    def generate_answer(self, question: str, context: str, use_lm_studio: bool = True) -> str:
        """
        Generate answer using LLM with retrieved context.
        
        Supports both LM Studio (local) and OpenAI API.
        """
        from openai import OpenAI
        
        system_prompt = """You are a helpful book assistant. Answer questions based on the provided context about books.
        
        Rules:
        1. Only use information from the provided context
        2. If the context doesn't contain the answer, say so
        3. Cite sources using [Source X] notation
        4. Be concise but informative
        """
        
        user_prompt = f"""Context:
{context}

Question: {question}

Please provide a helpful answer based on the context above."""
        
        if use_lm_studio:
            # LM Studio - runs locally
            client = OpenAI(
                base_url=settings.LM_STUDIO_URL,
                api_key="not-needed"  # LM Studio doesn't require key
            )
        else:
            # OpenAI API
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        try:
            response = client.chat.completions.create(
                model="local-model" if use_lm_studio else "gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def ask(self, question: str) -> Dict:
        """
        Main entry point for RAG Q&A.
        
        Args:
            question: User's question about books
            
        Returns:
            Dict with answer, sources, and metadata
        """
        # Step 1: Search for relevant chunks
        chunks = self.search_similar(question, top_k=5)
        
        if not chunks:
            return {
                'answer': "I don't have enough information to answer that question. Please try asking something else about the books in our database.",
                'sources': [],
                'chunks_used': 0
            }
        
        # Step 2: Construct context
        context = self.construct_context(chunks)
        
        # Step 3: Generate answer
        answer = self.generate_answer(question, context)
        
        # Step 4: Extract unique sources
        sources = []
        seen_books = set()
        for chunk in chunks:
            book_id = chunk['metadata'].get('book_id')
            if book_id and book_id not in seen_books:
                seen_books.add(book_id)
                sources.append({
                    'book_id': book_id,
                    'book_title': chunk['metadata'].get('book_title')
                })
        
        return {
            'answer': answer,
            'sources': sources,
            'chunks_used': len(chunks)
        }


# Singleton instance
rag_pipeline = RAGPipeline()
