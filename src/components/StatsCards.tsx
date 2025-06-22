import React from 'react';
import { Database, Zap, BarChart3, Brain } from 'lucide-react';

const StatsCards: React.FC = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div className="bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 p-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-blue-500/20 rounded-lg">
            <Database className="w-6 h-6 text-blue-400" />
          </div>
          <div>
            <p className="text-sm text-gray-400">Data Source</p>
            <p className="text-lg font-semibold text-white">BigQuery</p>
          </div>
        </div>
      </div>

      <div className="bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 p-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-green-500/20 rounded-lg">
            <Zap className="w-6 h-6 text-green-400" />
          </div>
          <div>
            <p className="text-sm text-gray-400">Query Speed</p>
            <p className="text-lg font-semibold text-white">~6s avg</p>
          </div>
        </div>
      </div>

      <div className="bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 p-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-purple-500/20 rounded-lg">
            <Brain className="w-6 h-6 text-purple-400" />
          </div>
          <div>
            <p className="text-sm text-gray-400">AI Model</p>
            <p className="text-lg font-semibold text-white">Gemini 2.0</p>
          </div>
        </div>
      </div>

      <div className="bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 p-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-orange-500/20 rounded-lg">
            <BarChart3 className="w-6 h-6 text-orange-400" />
          </div>
          <div>
            <p className="text-sm text-gray-400">Pipeline</p>
            <p className="text-lg font-semibold text-white">3 Phases</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StatsCards; 