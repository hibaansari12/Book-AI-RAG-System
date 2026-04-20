/**
 * Main layout component with navigation.
 * Clean, minimal design following assignment requirements.
 */

'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { BookOpenIcon, ChatBubbleLeftRightIcon, HomeIcon } from '@heroicons/react/24/outline';
import clsx from 'clsx';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const pathname = usePathname();

  const navItems = [
    { href: '/', label: 'Dashboard', icon: HomeIcon },
    { href: '/ask', label: 'Q&A', icon: ChatBubbleLeftRightIcon },
  ];

  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Header */}
      <header className="bg-white border-b border-neutral-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link href="/" className="flex items-center gap-2">
              <BookOpenIcon className="h-8 w-8 text-primary-600" />
              <span className="text-xl font-semibold text-neutral-900">
                Book Insights
              </span>
            </Link>

            {/* Navigation */}
            <nav className="flex items-center gap-1">
              {navItems.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={clsx(
                      'flex items-center gap-2 px-4 py-2 rounded-lg transition-colors',
                      isActive
                        ? 'bg-primary-50 text-primary-700'
                        : 'text-neutral-600 hover:bg-neutral-100'
                    )}
                  >
                    <item.icon className="h-5 w-5" />
                    <span className="font-medium">{item.label}</span>
                  </Link>
                );
              })}
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-neutral-200 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-neutral-500 text-sm">
            Book Insight Platform — AI-Powered Document Intelligence
          </p>
        </div>
      </footer>
    </div>
  );
}
