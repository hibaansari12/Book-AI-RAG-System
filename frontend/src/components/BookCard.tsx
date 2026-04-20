/**
 * Book card component for dashboard listing.
 * Displays title, author, rating, and genre badge.
 */

import Link from 'next/link';
import { StarIcon } from '@heroicons/react/24/solid';
import { BookListItem } from '@/lib/api';

interface BookCardProps {
  book: BookListItem;
}

export default function BookCard({ book }: BookCardProps) {
  return (
    <Link href={`/books/${book.id}`}>
      <article className="card p-4 hover:shadow-md transition-shadow cursor-pointer h-full flex flex-col">
        {/* Cover Image */}
        <div className="aspect-[2/3] bg-neutral-100 rounded-lg mb-4 overflow-hidden">
          {book.cover_image_url ? (
            <img
              src={book.cover_image_url}
              alt={book.title}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-neutral-400">
              <span className="text-4xl">📚</span>
            </div>
          )}
        </div>

        {/* Content */}
        <div className="flex-1 flex flex-col">
          {/* Genre Badge */}
          {book.ai_genre && (
            <span className="inline-block px-2 py-1 text-xs font-medium bg-primary-50 text-primary-700 rounded-full mb-2 w-fit">
              {book.ai_genre.split(',')[0].trim()}
            </span>
          )}

          {/* Title */}
          <h3 className="font-semibold text-neutral-900 line-clamp-2 mb-1">
            {book.title}
          </h3>

          {/* Author */}
          {book.author && (
            <p className="text-sm text-neutral-500 mb-2">
              by {book.author}
            </p>
          )}

          {/* Rating */}
          <div className="mt-auto flex items-center gap-1">
            {book.rating ? (
              <>
                <StarIcon className="h-4 w-4 text-yellow-400" />
                <span className="text-sm font-medium text-neutral-700">
                  {Number(book.rating).toFixed(1)}
                </span>
                {book.review_count > 0 && (
                  <span className="text-sm text-neutral-400">
                    ({book.review_count} reviews)
                  </span>
                )}
              </>
            ) : (
              <span className="text-sm text-neutral-400">No rating</span>
            )}
          </div>
        </div>
      </article>
    </Link>
  );
}
