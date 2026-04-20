/**
 * API client for communicating with Django backend.
 * Handles all HTTP requests and error handling.
 */

import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '[localhost](http://localhost:8000/api)';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface Book {
  id: number;
  title: string;
  author: string | null;
  description: string | null;
  rating: number | null;
  review_count: number;
  book_url: string;
  cover_image_url: string | null;
  ai_summary: string | null;
  ai_genre: string | null;
  ai_sentiment: string | null;
  source_website: string;
  created_at: string;
  is_processed: boolean;
}

export interface BookListItem {
  id: number;
  title: string;
  author: string | null;
  rating: number | null;
  review_count: number;
  cover_image_url: string | null;
  ai_genre: string | null;
}

export interface AskResponse {
  answer: string;
  sources: Array<{ book_id: string; book_title: string }>;
  chunks_used: number;
  cached: boolean;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// Book APIs
export const bookApi = {
  // GET /api/books/ - List all books
  getAll: async (params?: {
    search?: string;
    genre?: string;
    min_rating?: number;
    page?: number;
  }): Promise<PaginatedResponse<BookListItem>> => {
    const response = await api.get('/books/', { params });
    return response.data;
  },

  // GET /api/books/{id}/ - Get book details
  getById: async (id: number): Promise<Book> => {
    const response = await api.get(`/books/${id}/`);
    return response.data;
  },

  // GET /api/books/{id}/recommendations/ - Get related books
  getRecommendations: async (id: number): Promise<{
    book_id: number;
    book_title: string;
    recommendations: BookListItem[];
    recommendation_reason: string;
  }> => {
    const response = await api.get(`/books/${id}/recommendations/`);
    return response.data;
  },

  // POST /api/books/ - Create new book
  create: async (bookData: Partial<Book>): Promise<Book> => {
    const response = await api.post('/books/', bookData);
    return response.data;
  },
};

// AI APIs
export const aiApi = {
  // POST /api/ai/ask/ - RAG question answering
  ask: async (question: string): Promise<AskResponse> => {
    const response = await api.post('/ai/ask/', { question });
    return response.data;
  },

  // POST /api/ai/generate-insights/ - Generate AI insights for a book
  generateInsights: async (bookId: number): Promise<{
    book_id: number;
    book_title: string;
    insights: {
      summary: string;
      genre: string;
      sentiment: string;
    };
  }> => {
    const response = await api.post('/ai/generate-insights/', { book_id: bookId });
    return response.data;
  },
};

// Scraper APIs
export const scraperApi = {
  // POST /api/scraper/scrape/ - Trigger scraping
  scrape: async (query: string, maxBooks: number = 10): Promise<{
    query: string;
    books_found: number;
    books_created: number;
    message: string;
  }> => {
    const response = await api.post('/scraper/scrape/', {
      query,
      max_books: maxBooks,
      generate_insights: true,
    });
    return response.data;
  },
};

export default api;
