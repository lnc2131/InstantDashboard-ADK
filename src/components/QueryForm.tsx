import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Send, Loader2 } from 'lucide-react';

interface QueryFormProps {
  onSubmit: (query: string) => void;
  isLoading: boolean;
  onLoadingChange: (loading: boolean) => void;
  onResults: (results: any) => void;
}

interface QueryResponse {
  success: boolean;
  data: any;
  execution_time: number;
  timestamp: string;
  query_plan_used: boolean;
  row_count: number;
  error_message?: string;
}

const QueryForm: React.FC<QueryFormProps> = ({ 
  onSubmit, 
  isLoading, 
  onLoadingChange, 
  onResults 
}) => {
  const [query, setQuery] = useState('');

  const queryMutation = useMutation({
    mutationFn: async (question: string): Promise<QueryResponse> => {
      const response = await fetch('http://127.0.0.1:8001/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question,
          use_full_pipeline: true,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to execute query');
      }

      return response.json();
    },
    onMutate: () => {
      onLoadingChange(true);
    },
    onSuccess: (data) => {
      onResults(data);
      onLoadingChange(false);
    },
    onError: (error) => {
      console.error('Query error:', error);
      onResults({ 
        success: false, 
        error_message: error instanceof Error ? error.message : 'Unknown error' 
      });
      onLoadingChange(false);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !isLoading) {
      onSubmit(query);
      queryMutation.mutate(query);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="relative">
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask a question about your data... e.g., 'What are the top 3 countries by sales?'"
          className="w-full p-4 pr-12 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
          rows={3}
          disabled={isLoading}
        />
        
        <button
          type="submit"
          disabled={!query.trim() || isLoading}
          className="absolute bottom-3 right-3 p-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg hover:from-purple-600 hover:to-pink-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
        >
          {isLoading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <Send className="w-5 h-5" />
          )}
        </button>
      </div>

      {isLoading && (
        <div className="flex items-center space-x-2 text-purple-400">
          <Loader2 className="w-4 h-4 animate-spin" />
          <span className="text-sm">Processing your question...</span>
        </div>
      )}

      <div className="text-xs text-gray-400">
        <p>💡 <strong>Tip:</strong> Ask questions about countries, products, stores, or sales trends</p>
      </div>
    </form>
  );
};

export default QueryForm; 