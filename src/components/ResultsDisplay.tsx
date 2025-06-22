import React from 'react';
import { CheckCircle, XCircle, Clock, BarChart3, Table, Eye } from 'lucide-react';
import DataChart from './DataChart';
import DataTable from './DataTable';

interface ResultsDisplayProps {
  results: any;
  query: string;
  isLoading: boolean;
}

const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ results, query, isLoading }) => {
  if (isLoading) {
    return (
      <div className="bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 p-8">
        <div className="flex items-center justify-center space-x-3">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-400"></div>
          <span className="text-white text-lg">Analyzing your question...</span>
        </div>
        <div className="mt-4 text-center text-gray-400">
          <p>🤖 AI agents are working on your query</p>
        </div>
      </div>
    );
  }

  if (!results) {
    return (
      <div className="bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 p-8 text-center">
        <Eye className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-white mb-2">Ready for your questions</h3>
        <p className="text-gray-400">Ask a question above or try one of the examples to get started.</p>
      </div>
    );
  }

  const { success, data, execution_time, row_count, query_plan_used, error_message } = results;

  return (
    <div className="space-y-6">
      {/* Query Info */}
      <div className="bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-2">
            {success ? (
              <CheckCircle className="w-5 h-5 text-green-400" />
            ) : (
              <XCircle className="w-5 h-5 text-red-400" />
            )}
            <h3 className="text-lg font-semibold text-white">Query Results</h3>
          </div>
          
          <div className="flex items-center space-x-4 text-sm text-gray-400">
            <div className="flex items-center space-x-1">
              <Clock className="w-4 h-4" />
              <span>{execution_time?.toFixed(2)}s</span>
            </div>
            {query_plan_used && (
              <span className="bg-purple-500/20 text-purple-300 px-2 py-1 rounded text-xs">
                AI Pipeline
              </span>
            )}
          </div>
        </div>

        <div className="bg-white/5 rounded-lg p-3 mb-4">
          <p className="text-gray-300 text-sm font-medium">Question:</p>
          <p className="text-white">{query}</p>
        </div>

        {success ? (
          <div className="grid grid-cols-3 gap-4 text-center">
            <div className="bg-green-500/10 rounded-lg p-3">
              <div className="text-2xl font-bold text-green-400">{row_count}</div>
              <div className="text-sm text-gray-400">Rows Returned</div>
            </div>
            <div className="bg-blue-500/10 rounded-lg p-3">
              <div className="text-2xl font-bold text-blue-400">
                {data?.status === 'success' ? 'Success' : 'Completed'}
              </div>
              <div className="text-sm text-gray-400">Status</div>
            </div>
            <div className="bg-purple-500/10 rounded-lg p-3">
              <div className="text-2xl font-bold text-purple-400">
                {query_plan_used ? 'Yes' : 'No'}
              </div>
              <div className="text-sm text-gray-400">AI Enhanced</div>
            </div>
          </div>
        ) : (
          <div className="bg-red-500/10 rounded-lg p-4">
            <p className="text-red-400 font-medium">Error:</p>
            <p className="text-red-300">{error_message || 'Unknown error occurred'}</p>
          </div>
        )}
      </div>

      {/* Data Visualization */}
      {success && data?.data && Array.isArray(data.data) && data.data.length > 0 && (
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Chart */}
          <div className="bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 p-6">
            <div className="flex items-center space-x-2 mb-4">
              <BarChart3 className="w-5 h-5 text-blue-400" />
              <h3 className="text-lg font-semibold text-white">Visualization</h3>
            </div>
            <DataChart data={data.data} />
          </div>

          {/* Table */}
          <div className="bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 p-6">
            <div className="flex items-center space-x-2 mb-4">
              <Table className="w-5 h-5 text-green-400" />
              <h3 className="text-lg font-semibold text-white">Data Table</h3>
            </div>
            <DataTable data={data.data} />
          </div>
        </div>
      )}

      {/* SQL Query */}
      {success && data?.generated_sql && (
        <div className="bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Generated SQL</h3>
          <div className="bg-black/30 rounded-lg p-4 overflow-x-auto">
            <pre className="text-sm text-gray-300 whitespace-pre-wrap">
              {data.generated_sql}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResultsDisplay; 