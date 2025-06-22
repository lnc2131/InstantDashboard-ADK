import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer } from 'recharts';

interface DataChartProps {
  data: any[];
}

const DataChart: React.FC<DataChartProps> = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-400">
        <p>No data to display</p>
      </div>
    );
  }

  // Get the first two keys from the data to use as x and y axis
  const keys = Object.keys(data[0]);
  const xKey = keys[0];
  const yKey = keys[1];

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis 
            dataKey={xKey} 
            stroke="#9CA3AF"
            tick={{ fontSize: 12 }}
          />
          <YAxis 
            stroke="#9CA3AF"
            tick={{ fontSize: 12 }}
          />
          <Bar 
            dataKey={yKey} 
            fill="#8B5CF6"
            radius={[4, 4, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default DataChart; 