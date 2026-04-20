import type { Metadata } from 'next';
import Layout from '@/components/Layout';
import './globals.css';

export const metadata: Metadata = {
  title: 'Book Insight Platform',
  description: 'AI-powered book intelligence and Q&A system',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Layout>{children}</Layout>
      </body>
    </html>
  );
}
