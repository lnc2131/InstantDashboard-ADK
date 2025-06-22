"use client";

import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Search, BarChart3, TrendingUp, Database, Sparkles } from 'lucide-react';
import QueryForm from '../components/QueryForm';
import ResultsDisplay from '../components/ResultsDisplay';
import StatsCards from '../components/StatsCards';

// Create a query client
const queryClient = new QueryClient();

export default function Home() {
  const [currentQuery, setCurrentQuery] = useState<string>('');
  const [results, setResults] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        {/* Header */}
        <header className="border-b border-white/10 bg-black/20 backdrop-blur-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center space-x-3">
                <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg">
                  <Sparkles className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-white">InstantDashboard</h1>
                  <p className="text-sm text-gray-400">AI-Powered Data Analytics</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-2 text-sm text-gray-400">
                <Database className="w-4 h-4" />
                <span>Connected to BigQuery</span>
              </div>
            </div>
          </div>
        </header>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Welcome Section */}
          <div className="text-center mb-8">
            <h2 className="text-4xl font-bold text-white mb-4">
              Ask questions about your data in{' '}
              <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                plain English
              </span>
            </h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              Our AI agents convert your natural language questions into SQL queries, 
              execute them safely, and present beautiful visualizations.
            </p>
          </div>

          {/* Stats Cards */}
          <StatsCards />

          {/* Query Section */}
          <div className="grid lg:grid-cols-2 gap-8 mb-8">
            {/* Query Form */}
            <div className="bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 p-6">
              <div className="flex items-center space-x-2 mb-4">
                <Search className="w-5 h-5 text-purple-400" />
                <h3 className="text-lg font-semibold text-white">Ask Your Question</h3>
              </div>
              
              <QueryForm 
                onSubmit={setCurrentQuery}
                isLoading={isLoading}
                onLoadingChange={setIsLoading}
                onResults={setResults}
              />
            </div>

            {/* Quick Examples */}
            <div className="bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 p-6">
              <div className="flex items-center space-x-2 mb-4">
                <TrendingUp className="w-5 h-5 text-green-400" />
                <h3 className="text-lg font-semibold text-white">Try These Examples</h3>
              </div>
              
              <div className="space-y-3">
                {[
                  "What are the top 3 countries by total sticker sales?",
                  "Show me the top 5 products by sales volume",
                  "Which stores have the highest revenue?",
                  "What is the sales trend over time?"
                ].map((example, index) => (
                  <button
                    key={index}
                    onClick={() => setCurrentQuery(example)}
                    className="w-full text-left p-3 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 hover:border-purple-400/50 transition-all duration-200 text-gray-300 hover:text-white"
                  >
                    <div className="flex items-center space-x-2">
                      <BarChart3 className="w-4 h-4 text-purple-400" />
                      <span className="text-sm">{example}</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Results Section */}
          <ResultsDisplay 
            results={results}
            query={currentQuery}
            isLoading={isLoading}
          />
        </div>

        {/* Footer */}
        <footer className="border-t border-white/10 bg-black/20 backdrop-blur-sm mt-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="text-center text-gray-400 text-sm">
              <p>Powered by Google ADK • Built with Next.js & FastAPI</p>
              <p className="mt-1">Natural Language → SQL → Insights</p>
            </div>
          </div>
        </footer>
      </div>
    </QueryClientProvider>
  );
} 