/**
 * Book Detail Page
 * 
 * Displays full book information including AI insights.
 * Shows recommendations at the bottom.
 */

'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeftIcon, StarIcon, ArrowTopRightOnSquareIcon } from '@heroicons/react/24/outline';
import LoadingSpinner from '@/components/LoadingSpinner';
import BookCard from '@/components/BookCard';
import { bookApi, Book, BookListItem } from '@/lib/api';

export default function BookDetailPage() {
  const params = useParams();
  const router = useRouter();
  const bookId = Number(params.id);

  const [book, setBook] = useState<Book | null>(null);
  const [recommendations, setRecommendations] = useState<BookListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (bookId) {
      fetchBookDetails();
    }
  }, [bookId]);

  const fetchBookDetails = async () => {
    setLoading(true);
    try {
      const [bookData, recsData] = await Promise.all([
        bookApi.getById(bookId),
        bookApi.getRecommendations(bookId),
      ]);
      setBook(bookData);
      setRecommendations(recsData.recommendations);
    } catch (error) {
      console.error('Failed to fetch book:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!book) {
    return (
      <div className="card p-12 text-center">
        <p className="text-neutral-500">Book not found</p>
      </div>
    );
  }

  return (
    <div>
      {/* Back Button */}
      <button
        onClick={() => router.back()}
        className="flex items-center gap-2 text-neutral-600 hover:text-neutral-900 mb-6"
      >
        <ArrowLeftIcon className="h-5 w-5" />
        <span>Back to Library</span>
      </button>

      {/* Book Details Card */}
      <div className="card p-6 md:p-8 mb-8">
        <div className="flex flex-col md:flex-row gap-8">
          {/* Cover Image */}
          <div className="flex-shrink-0">
            <div className="w-48 aspect-[2/3] bg-neutral-100 rounded-lg overflow-hidden">
              {book.cover_image_url ? (
                <img
                  src={book.cover_image_url}
                  alt={book.title}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-neutral-400 text-6xl">
                  📚
                </div>
              )}
            </div>
          </div>

          {/* Book Info */}
          <div className="flex-1">
            {/* Genre Badge */}
            {book.ai_genre && (
              <div className="flex flex-wrap gap-2 mb-3">
                {book.ai_genre.split(',').map((genre, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1 text-sm font-medium bg-primary-50 text-primary-700 rounded-full"
                  >
                    {genre.trim()}
                  </span>
                ))}
              </div>
            )}

            {/* Title */}
            <h1 className="text-3xl font-bold text-neutral-900 mb-2">
              {book.title}
            </h1>

            {/* Author */}
            {book.author && (
              <p className="text-lg text-neutral-600 mb-4">
                by {book.author}
              </p>
            )}

            {/* Rating & Sentiment */}
            <div className="flex items-center gap-6 mb-6">
              {book.rating && (
                <div className="flex items-center gap-1">
                  <StarIcon className="h-5 w-5 text-yellow-400 fill-current" />
                  <span className="font-semibold text-neutral-800">
                    {Number(book.rating).toFixed(1)}
                  </span>
                  <span className="text-neutral-500">
                    ({book.review_count} reviews)
                  </span>
                </div>
              )}
              {book.ai_sentiment && (
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  book.ai_sentiment === 'Positive' 
                    ? 'bg-green-50 text-green-700'
                    : book.ai_sentiment === 'Negative'
                    ? 'bg-red-50 text-red-700'
                    : 'bg-neutral-100 text-neutral-600'
                }`}>
                  {book.ai_sentiment} tone
                </span>
              )}
            </div>

            {/* External Link */}
            <a
              href={book.book_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 text-primary-600 hover:text-primary-700"
            >
              <span>View on {book.source_website}</span>
              <ArrowTopRightOnSquareIcon className="h-4 w-4" />
            </a>
          </div>
        </div>

        {/* Divider */}
        <hr className="my-8 border-neutral-200" />

        {/* AI Summary */}
        {book.ai_summary && (
          <div className="mb-8">
            <h2 className="text-lg font-semibold text-neutral-900 mb-3">
              AI Summary
            </h2>
            <p className="text-neutral-700 leading-relaxed">
              {book.ai_summary}
            </p>
          </div>
        )}

        {/* Description */}
        {book.description && (
          <div>
            <h2 className="text-lg font-semibold text-neutral-900 mb-3">
              Description
            </h2>
            <p className="text-neutral-700 leading-relaxed">
              {book.description}
            </p>
          </div>
        )}
      </div>

      {/* Recommendations Section */}
      {recommendations.length > 0 && (
        <div>
          <h2 className="text-2xl font-bold text-neutral-900 mb-6">
            If you like this book, you'll also enjoy
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-6">
            {recommendations.slice(0, 4).map((rec) => (
              <BookCard key={rec.id} book={rec} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
