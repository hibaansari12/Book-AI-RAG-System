/**
 * Dashboard / Book Listing Page
 * 
 * Displays all books with search and filter capabilities.
 * Requirements: title, author, rating/reviews, description, book URL
 */

'use client';

import { useState, useEffect } from 'react';
import { MagnifyingGlassIcon, FunnelIcon } from '@heroicons/react/24/outline';
import BookCard from '@/components/BookCard';
import LoadingSpinner from '@/components/LoadingSpinner';
import { bookApi, BookListItem } from '@/lib/api';

export default function DashboardPage() {
  const [books, setBooks] = useState<BookListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedGenre, setSelectedGenre] = useState('');
  const [totalCount, setTotalCount] = useState(0);

  // Fetch books on mount and when filters change
  useEffect(() => {
    fetchBooks();
  }, [searchQuery, selectedGenre]);

  const fetchBooks = async () => {
    setLoading(true);
    try {
      const response = await bookApi.getAll({
        search: searchQuery || undefined,
        genre: selectedGenre || undefined,
      });
      setBooks(response.results);
      setTotalCount(response.count);
    } catch (error) {
      console.error('Failed to fetch books:', error);
    } finally {
      setLoading(false);
    }
  };

  // Debounced search
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };

  return (
    <div>
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-neutral-900 mb-2">
          Book Library
        </h1>
        <p className="text-neutral-600">
          Explore our collection of {totalCount} books with AI-powered insights
        </p>
      </div>

      {/* Search and Filters */}
      <div className="card p-4 mb-8">
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Search Input */}
          <div className="flex-1 relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-neutral-400" />
            <input
              type="text"
              placeholder="Search by title or author..."
              value={searchQuery}
              onChange={handleSearchChange}
              className="input-field pl-10"
            />
          </div>

          {/* Genre Filter */}
          <div className="flex items-center gap-2">
            <FunnelIcon className="h-5 w-5 text-neutral-400" />
            <select
              value={selectedGenre}
              onChange={(e) => setSelectedGenre(e.target.value)}
              className="input-field w-auto"
            >
              <option value="">All Genres</option>
              <option value="Fiction">Fiction</option>
              <option value="Non-Fiction">Non-Fiction</option>
              <option value="Mystery">Mystery</option>
              <option value="Science Fiction">Science Fiction</option>
              <option value="Fantasy">Fantasy</option>
              <option value="Romance">Romance</option>
              <option value="Self-Help">Self-Help</option>
              <option value="Biography">Biography</option>
            </select>
          </div>
        </div>
      </div>

      {/* Book Grid */}
      {loading ? (
        <div className="flex justify-center py-12">
          <LoadingSpinner size="lg" />
        </div>
      ) : books.length === 0 ? (
        <div className="card p-12 text-center">
          <p className="text-neutral-500 text-lg">
            No books found. Try adjusting your search.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
          {books.map((book) => (
            <BookCard key={book.id} book={book} />
          ))}
        </div>
      )}
    </div>
  );
}
