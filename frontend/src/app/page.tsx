'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { FileText, BarChart3, ArrowRight } from 'lucide-react';
import Link from 'next/link';
import { apiCall } from '../config/api';

// Smart component that chooses the right chart based on data
function DataVisualization({ data }: { data: Record<string, unknown>[] }) {
  if (!data || data.length === 0) return null;

  // Get the keys from the first row to understand data structure
  const firstRow = data[0];
  const keys = Object.keys(firstRow);
  
  // Colors for charts
  const COLORS = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#06b6d4'];

  // Check if we have numeric data for charts
  const hasNumericData = keys.some(key => 
    data.some(row => typeof row[key] === 'number' || !isNaN(Number(row[key])))
  );

  // If only one column (like countries), show as a simple list
  if (keys.length === 1) {
    return (
      <div style={{
        backgroundColor: 'white',
        border: '1px solid #e0e7ff',
        borderRadius: '6px',
        padding: '16px',
        marginBottom: '16px'
      }}>
        <h4 style={{ 
          fontSize: '16px', 
          fontWeight: '600', 
          marginBottom: '12px',
          color: '#1e40af'
        }}>
          Results ({data.length} items):
        </h4>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '8px' }}>
          {data.map((item, index) => (
            <div key={index} style={{
              padding: '8px 12px',
              backgroundColor: '#f8fafc',
              borderRadius: '4px',
              border: '1px solid #e2e8f0',
              fontSize: '14px',
              fontWeight: '500'
            }}>
              {Object.values(item)[0] as string}
            </div>
          ))}
        </div>
      </div>
    );
  }

  // If we have 2 columns with numeric data, show bar chart
  if (keys.length === 2 && hasNumericData) {
    const [labelKey, valueKey] = keys;
    
    // Prepare data for chart (convert values to numbers)
    const chartData = data.map(item => ({
      [labelKey]: item[labelKey],
      [valueKey]: typeof item[valueKey] === 'number' ? item[valueKey] : Number(item[valueKey]) || 0
    }));

    return (
      <div style={{
        backgroundColor: 'white',
        border: '1px solid #e0e7ff',
        borderRadius: '6px',
        padding: '16px',
        marginBottom: '16px'
      }}>
        <h4 style={{ 
          fontSize: '16px', 
          fontWeight: '600', 
          marginBottom: '16px',
          color: '#1e40af'
        }}>
          Data Visualization:
        </h4>
        
        {/* Bar Chart */}
        <div style={{ marginBottom: '24px' }}>
          <h5 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '12px', color: '#374151' }}>
            Bar Chart:
          </h5>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey={labelKey} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey={valueKey} fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Pie Chart */}
        <div style={{ marginBottom: '16px' }}>
          <h5 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '12px', color: '#374151' }}>
            Pie Chart:
          </h5>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey={valueKey}
                nameKey={labelKey}
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    );
  }

  // For other data structures, show a nice table
  return (
    <div style={{
      backgroundColor: 'white',
      border: '1px solid #e0e7ff',
      borderRadius: '6px',
      padding: '16px',
      marginBottom: '16px'
    }}>
      <h4 style={{ 
        fontSize: '16px', 
        fontWeight: '600', 
        marginBottom: '12px',
        color: '#1e40af'
      }}>
        Data Table:
      </h4>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
          <thead>
            <tr style={{ backgroundColor: '#f8fafc' }}>
              {keys.map(key => (
                <th key={key} style={{ 
                  padding: '8px 12px', 
                  textAlign: 'left', 
                  border: '1px solid #e2e8f0',
                  fontWeight: '600',
                  color: '#374151'
                }}>
                  {key}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, index) => (
              <tr key={index} style={{ backgroundColor: index % 2 === 0 ? 'white' : '#f8fafc' }}>
                {keys.map(key => (
                  <td key={key} style={{ 
                    padding: '8px 12px', 
                    border: '1px solid #e2e8f0',
                    color: '#1f2937'
                  }}>
                    {String(row[key])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default function Home() {
  const router = useRouter();
  // React State - this "remembers" what the user types and results
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<{
    success?: boolean;
    data?: {
      row_count?: number;
      data?: Record<string, unknown>[];
      generated_sql?: string;
    };
    execution_time?: number;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Function that runs when user clicks "Ask Question"
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault(); // Prevents page refresh
    
    if (!question.trim()) return; // Don't submit empty questions
    
    setLoading(true);
    setError(null);
    setResults(null);
    
    try {
      // REAL API CALL to your FastAPI backend
      console.log('Calling FastAPI backend with question:', question);
      
      const response = await apiCall('/api/query', {
        method: 'POST',
        body: JSON.stringify({ question: question }),
      });
      
      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('API Response:', data);
      
      setResults(data);
      
    } catch (error) {
      console.error('Error calling API:', error);
      setError(error instanceof Error ? error.message : 'Unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#f9fafb',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      {/* Header Section */}
      <header style={{
        backgroundColor: 'white',
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
        padding: '24px 0'
      }}>
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '0 16px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div>
            <h1 style={{
              fontSize: '30px',
              fontWeight: 'bold',
              color: '#111827',
              margin: 0
            }}>
              InstantDashboard
            </h1>
            <p style={{
              color: '#6b7280',
              marginTop: '8px',
              margin: '8px 0 0 0'
            }}>
              Ask questions about your data in natural language
            </p>
          </div>
          
          {/* Navigation */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px'
          }}>
            {/* Navigation removed - focusing on InstantDashboard */}
          </div>
        </div>
      </header>

      {/* Navigation Cards */}
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '32px 16px 0'
      }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '20px',
          marginBottom: '32px'
        }}>
          {/* InstantDashboard Card */}
          <div style={{
            backgroundColor: 'white',
            borderRadius: '12px',
            padding: '24px',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
            border: '1px solid #e5e7eb'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              marginBottom: '12px'
            }}>
              <div style={{
                width: '40px',
                height: '40px',
                backgroundColor: '#dbeafe',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <BarChart3 size={20} color="#3b82f6" />
              </div>
              <h3 style={{
                fontSize: '18px',
                fontWeight: '600',
                color: '#111827',
                margin: 0
              }}>
                InstantDashboard
              </h3>
            </div>
            <p style={{
              fontSize: '14px',
              color: '#6b7280',
              marginBottom: '16px',
              lineHeight: '1.5'
            }}>
              Ask natural language questions about your data and get instant visualizations and insights. Perfect for quick data exploration.
            </p>
            <div style={{
              backgroundColor: '#f0f9ff',
              padding: '12px',
              borderRadius: '6px',
              fontSize: '12px',
              color: '#1e40af',
              fontWeight: '500'
            }}>
              ✓ Active below - ask any data question
            </div>
          </div>

          {/* Report Writer Card - REMOVED */}
        </div>
      </div>

      {/* Main Content */}
      <main style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '0 16px 32px'
      }}>
        <div style={{
          backgroundColor: 'white',
          borderRadius: '8px',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
          padding: '24px'
        }}>
          <h2 style={{
            fontSize: '20px',
            fontWeight: '600',
            marginBottom: '16px',
            color: '#111827'
          }}>
            InstantDashboard: Ask a Question
          </h2>
          
          {/* REAL QUERY FORM */}
          <form onSubmit={handleSubmit} style={{ marginBottom: '16px' }}>
            <div style={{ marginBottom: '16px' }}>
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="e.g., What are the top 3 countries by sticker sales?"
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  border: '1px solid #d1d5db',
                  borderRadius: '8px',
                  fontSize: '16px',
                  outline: 'none',
                  transition: 'border-color 0.2s',
                }}
                onFocus={(e) => {
                  e.target.style.borderColor = '#3b82f6';
                  e.target.style.boxShadow = '0 0 0 3px rgba(59, 130, 246, 0.1)';
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = '#d1d5db';
                  e.target.style.boxShadow = 'none';
                }}
              />
            </div>
            
            <button
              type="submit"
              disabled={loading || !question.trim()}
              style={{
                backgroundColor: loading || !question.trim() ? '#9ca3af' : '#3b82f6',
                color: 'white',
                padding: '12px 24px',
                border: 'none',
                borderRadius: '8px',
                fontSize: '16px',
                fontWeight: '600',
                cursor: loading || !question.trim() ? 'not-allowed' : 'pointer',
                transition: 'background-color 0.2s',
              }}
            >
              {loading ? 'Processing...' : 'Ask Question'}
            </button>
          </form>

          {/* Example questions */}
          <div style={{
            backgroundColor: '#f9fafb',
            borderRadius: '6px',
            padding: '16px',
            border: '1px solid #e5e7eb'
          }}>
            <p style={{ 
              fontSize: '14px', 
              fontWeight: '600', 
              color: '#374151',
              margin: '0 0 8px 0'
            }}>
              Try these examples:
            </p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              {[
                'What are the top 3 countries by sticker sales?',
                'Show me the top 5 products by sales volume',
                'What is the total sales by country?'
              ].map((example, index) => (
                <button
                  key={index}
                  onClick={() => setQuestion(example)}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: '#3b82f6',
                    fontSize: '14px',
                    cursor: 'pointer',
                    textAlign: 'left' as const,
                    padding: '4px 0',
                    textDecoration: 'underline'
                  }}
                >
                  {example}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* RESULTS SECTION - Now with charts! */}
        <div style={{
          marginTop: '32px',
          backgroundColor: 'white',
          borderRadius: '8px',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
          padding: '24px'
        }}>
          <h2 style={{
            fontSize: '20px',
            fontWeight: '600',
            marginBottom: '16px',
            color: '#111827'
          }}>
            Results
          </h2>
          
          {/* Show different content based on state */}
          {error && (
            <div style={{
              backgroundColor: '#fef2f2',
              border: '1px solid #fecaca',
              borderRadius: '8px',
              padding: '16px',
              color: '#dc2626'
            }}>
              <strong>Error:</strong> {error}
            </div>
          )}
          
          {results && !error && (
            <div style={{
              backgroundColor: '#f0f9ff',
              border: '1px solid #bae6fd',
              borderRadius: '8px',
              padding: '16px'
            }}>
              <h3 style={{ 
                fontSize: '16px', 
                fontWeight: '600', 
                marginBottom: '12px',
                color: '#0c4a6e'
              }}>
                Query Results:
              </h3>
              
              {/* Show key information in a user-friendly way */}
              {results.success && results.data && (
                <div style={{ marginBottom: '16px' }}>
                  <div style={{
                    backgroundColor: '#ecfdf5',
                    border: '1px solid #a7f3d0',
                    borderRadius: '6px',
                    padding: '12px',
                    marginBottom: '12px'
                  }}>
                    <p style={{ fontSize: '14px', color: '#065f46', margin: 0 }}>
                      ✅ <strong>Success!</strong> Found {results.data.row_count} results in {results.execution_time?.toFixed(2)}s
                    </p>
                  </div>
                  
                  {/* NEW: Smart Data Visualization */}
                  {results.data.data && results.data.data.length > 0 && (
                    <DataVisualization data={results.data.data} />
                  )}
                  
                  {/* Show the SQL that was generated */}
                  {results.data.generated_sql && (
                    <div style={{
                      backgroundColor: '#fffbeb',
                      border: '1px solid #fed7aa',
                      borderRadius: '6px',
                      padding: '12px',
                      marginBottom: '12px'
                    }}>
                      <h4 style={{ 
                        fontSize: '14px', 
                        fontWeight: '600', 
                        marginBottom: '8px',
                        color: '#92400e'
                      }}>
                        Generated SQL:
                      </h4>
                      <pre style={{
                        fontSize: '12px',
                        margin: 0,
                        whiteSpace: 'pre-wrap',
                        color: '#451a03'
                      }}>
                        {results.data.generated_sql}
                      </pre>
                    </div>
                  )}
                </div>
              )}
              
              {/* Still show the raw JSON for debugging, but collapsed */}
              <details style={{ marginTop: '12px' }}>
                <summary style={{ 
                  cursor: 'pointer', 
                  fontSize: '14px', 
                  fontWeight: '600',
                  color: '#6b7280'
                }}>
                  Show Raw Response (for debugging)
                </summary>
                <pre style={{
                  backgroundColor: 'white',
                  padding: '12px',
                  borderRadius: '4px',
                  fontSize: '12px',
                  overflow: 'auto',
                  border: '1px solid #e0e7ff',
                  marginTop: '8px'
                }}>
                  {JSON.stringify(results, null, 2)}
                </pre>
              </details>
            </div>
          )}
          
          {!results && !error && !loading && (
            <div style={{
              textAlign: 'center' as const,
              padding: '64px',
              color: '#6b7280'
            }}>
              <BarChart3 size={48} style={{ marginBottom: '16px', opacity: 0.5 }} />
              <p style={{ fontSize: '16px', margin: 0 }}>
                Ask a question above to see results and visualizations
              </p>
            </div>
          )}
          
          {loading && (
            <div style={{
              textAlign: 'center' as const,
              padding: '64px',
              color: '#6b7280'
            }}>
              <div style={{
                display: 'inline-block',
                width: '32px',
                height: '32px',
                border: '3px solid #f3f4f6',
                borderRadius: '50%',
                borderTopColor: '#3b82f6',
                animation: 'spin 1s ease-in-out infinite',
                marginBottom: '16px'
              }} />
              <p style={{ fontSize: '16px', margin: 0 }}>
                Processing your question...
              </p>
            </div>
          )}
        </div>
      </main>
      
      <style jsx>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
