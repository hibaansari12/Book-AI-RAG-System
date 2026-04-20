/**
 * Q&A Interface Page
 * 
 * RAG-powered question answering about books.
 * Displays answers with source citations.
 */

'use client';

import { useState } from 'react';
import { PaperAirplaneIcon, BookOpenIcon, SparklesIcon } from '@heroicons/react/24/outline';
import LoadingSpinner from '@/components/LoadingSpinner';
import { aiApi, AskResponse } from '@/lib/api';
import Link from 'next/link';

interface ChatMessage {
  type: 'user' | 'assistant';
  content: string;
  sources?: Array<{ book_id: string; book_title: string }>;
  cached?: boolean;
}

export default function AskPage() {
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim() || loading) return;

    const userMessage = question.trim();
    setQuestion('');
    
    // Add user message
    setMessages((prev) => [...prev, { type: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response = await aiApi.ask(userMessage);
      
      // Add assistant response
      setMessages((prev) => [
        ...prev,
        {
          type: 'assistant',
          content: response.answer,
          sources: response.sources,
          cached: response.cached,
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          type: 'assistant',
          content: 'Sorry, I encountered an error processing your question. Please try again.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Sample questions for users to try
  const sampleQuestions = [
    "What fiction books do you recommend?",
    "Tell me about books on self-improvement",
    "What are some highly rated mystery novels?",
    "Summarize the themes in science fiction books",
  ];

  return (
    <div className="max-w-4xl mx-auto">
      {/* Page Header */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 rounded-full mb-4">
          <SparklesIcon className="h-8 w-8 text-primary-600" />
        </div>
        <h1 className="text-3xl font-bold text-neutral-900 mb-2">
          Ask About Books
        </h1>
        <p className="text-neutral-600 max-w-xl mx-auto">
          Ask questions about the books in our library. Our AI will search through 
          the collection and provide answers with source citations.
        </p>
      </div>

      {/* Chat Container */}
      <div className="card mb-6">
        {/* Messages Area */}
        <div className="min-h-[400px] max-h-[500px] overflow-y-auto p-6">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <BookOpenIcon className="h-12 w-12 text-neutral-300 mx-auto mb-4" />
              <p className="text-neutral-500 mb-6">
                Start by asking a question about books
              </p>
              
              {/* Sample Questions */}
              <div className="space-y-2">
                <p className="text-sm text-neutral-400 mb-3">Try asking:</p>
                {sampleQuestions.map((q, idx) => (
                  <button
                    key={idx}
                    onClick={() => setQuestion(q)}
                    className="block w-full text-left px-4 py-2 text-sm text-neutral-600 
                             bg-neutral-50 hover:bg-neutral-100 rounded-lg transition-colors"
                  >
                    "{q}"
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {messages.map((message, idx) => (
                <div
                  key={idx}
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                      message.type === 'user'
                        ? 'bg-primary-600 text-white'
                        : 'bg-neutral-100 text-neutral-800'
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{message.content}</p>
                    
                    {/* Sources */}
                    {message.sources && message.sources.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-neutral-200">
                        <p className="text-xs text-neutral-500 mb-2">Sources:</p>
                        <div className="flex flex-wrap gap-2">
                          {message.sources.map((source, sIdx) => (
                            <Link
                              key={sIdx}
                              href={`/books/${source.book_id}`}
                              className="text-xs px-2 py-1 bg-white rounded-full 
                                       text-primary-600 hover:bg-primary-50 transition-colors"
                            >
                              {source.book_title}
                            </Link>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {/* Cached indicator */}
                    {message.cached && (
                      <p className="text-xs text-neutral-400 mt-2">
                        ⚡ Retrieved from cache
                      </p>
                    )}
                  </div>
                </div>
              ))}
              
              {/* Loading indicator */}
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-neutral-100 rounded-2xl px-4 py-3">
                    <LoadingSpinner size="sm" />
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="border-t border-neutral-200 p-4">
          <form onSubmit={handleSubmit} className="flex gap-3">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask a question about books..."
              className="input-field flex-1"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={!question.trim() || loading}
              className="btn-primary flex items-center gap-2"
            >
              <PaperAirplaneIcon className="h-5 w-5" />
              <span className="hidden sm:inline">Ask</span>
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
