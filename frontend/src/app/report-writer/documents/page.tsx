'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { 
  Plus, 
  FileText, 
  Edit3, 
  Calendar, 
  MoreVertical
} from 'lucide-react';
import { apiCall } from '../../../config/api';

interface Document {
  id: number;
  title: string;
  description: string;
  template_id: number;
  content: {
    template_used: { name: string };
    sections: Array<{ title: string; completed: boolean }>;
  };
  created_at: string;
  updated_at: string;
  status: 'draft' | 'in_progress' | 'completed';
}

export default function DocumentsPage() {
  const router = useRouter();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiCall('/api/report-writer/documents');
      
      if (!response.ok) {
        throw new Error(`Failed to fetch documents: ${response.status}`);
      }
      
      const data = await response.json();
      setDocuments(data);
      
    } catch (error) {
      console.error('Error fetching documents:', error);
      setError(error instanceof Error ? error.message : 'Failed to load documents');
      
      // Mock data for development
      setDocuments([
        {
          id: 1,
          title: "Q4 Financial Performance Report",
          description: "Comprehensive quarterly financial analysis with revenue trends and forecasting",
          template_id: 1,
          content: {
            template_used: { name: "Financial Quarterly Report" },
            sections: [
              { title: "Executive Summary", completed: true },
              { title: "Revenue Analysis", completed: true },
              { title: "Financial Forecasting", completed: false }
            ]
          },
          created_at: "2024-01-15T10:30:00Z",
          updated_at: "2024-01-16T14:45:00Z",
          status: "in_progress"
        },
        {
          id: 2,
          title: "Holiday Marketing Campaign Results",
          description: "Analysis of Q4 marketing campaigns including ROI and customer acquisition metrics",
          template_id: 2,
          content: {
            template_used: { name: "Marketing Campaign Analysis" },
            sections: [
              { title: "Campaign Overview", completed: true },
              { title: "Performance Metrics", completed: true },
              { title: "ROI Analysis", completed: true },
              { title: "Customer Insights", completed: true }
            ]
          },
          created_at: "2024-01-10T09:15:00Z",
          updated_at: "2024-01-12T16:20:00Z",
          status: "completed"
        },
        {
          id: 3,
          title: "Sales Team Performance Review",
          description: "Monthly sales performance analysis and territory breakdown",
          template_id: 3,
          content: {
            template_used: { name: "Sales Performance Report" },
            sections: [
              { title: "Executive Summary", completed: false },
              { title: "Territory Analysis", completed: false },
              { title: "Team Performance", completed: false }
            ]
          },
          created_at: "2024-01-18T08:00:00Z",
          updated_at: "2024-01-18T08:00:00Z",
          status: "draft"
        }
      ]);
      
    } finally {
      setLoading(false);
    }
  };



  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'in_progress':
        return 'bg-blue-100 text-blue-800';
      case 'draft':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getCompletionPercentage = (sections: Array<{ completed: boolean }>) => {
    const completed = sections.filter(s => s.completed).length;
    return Math.round((completed / sections.length) * 100);
  };

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#f8fafc',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      {/* Header */}
      <header style={{
        backgroundColor: 'white',
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
        padding: '24px 0'
      }}>
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '0 24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div>
            <h1 style={{
              fontSize: '32px',
              fontWeight: 'bold',
              color: '#111827',
              margin: 0
            }}>
              My Reports
            </h1>
            <p style={{
              color: '#6b7280',
              marginTop: '8px',
              margin: '8px 0 0 0',
              fontSize: '16px'
            }}>
              Manage and access your business reports
            </p>
          </div>
          
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '16px'
          }}>
            <button
              onClick={() => router.push('/report-writer')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 20px',
                backgroundColor: '#3b82f6',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '14px',
                fontWeight: '500',
                cursor: 'pointer'
              }}
            >
              <Plus size={16} />
              New Report
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '40px 24px'
      }}>
        {error && (
          <div style={{
            backgroundColor: '#fef2f2',
            border: '1px solid #fecaca',
            borderRadius: '8px',
            padding: '16px',
            marginBottom: '24px',
            color: '#dc2626'
          }}>
            <strong>Error:</strong> {error}
            <br />
            <small>Showing mock data for development</small>
          </div>
        )}

        {loading ? (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
            gap: '24px'
          }}>
            {[1, 2, 3].map((i) => (
              <div key={i} style={{
                backgroundColor: 'white',
                borderRadius: '12px',
                padding: '24px',
                boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
                border: '1px solid #e5e7eb'
              }}>
                <div style={{
                  height: '20px',
                  backgroundColor: '#f3f4f6',
                  borderRadius: '4px',
                  marginBottom: '12px'
                }} />
                <div style={{
                  height: '40px',
                  backgroundColor: '#f3f4f6',
                  borderRadius: '4px'
                }} />
              </div>
            ))}
          </div>
        ) : documents.length === 0 ? (
          <div style={{
            textAlign: 'center',
            padding: '80px 20px',
            backgroundColor: 'white',
            borderRadius: '12px',
            border: '1px solid #e5e7eb'
          }}>
            <FileText size={64} color="#d1d5db" style={{ marginBottom: '24px' }} />
            <h3 style={{
              fontSize: '24px',
              fontWeight: '600',
              color: '#374151',
              marginBottom: '12px'
            }}>
              No reports yet
            </h3>
            <p style={{
              fontSize: '16px',
              color: '#6b7280',
              marginBottom: '32px'
            }}>
              Create your first business report to get started
            </p>
            <button
              onClick={() => router.push('/report-writer')}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '12px 24px',
                backgroundColor: '#3b82f6',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '16px',
                fontWeight: '500',
                cursor: 'pointer'
              }}
            >
              <Plus size={20} />
              Create Your First Report
            </button>
          </div>
        ) : (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
            gap: '24px'
          }}>
            {documents.map((doc) => {
              const completionPercentage = getCompletionPercentage(doc.content.sections);
              
              return (
                <div
                  key={doc.id}
                  style={{
                    backgroundColor: 'white',
                    borderRadius: '12px',
                    padding: '24px',
                    boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
                    border: '1px solid #e5e7eb',
                    transition: 'transform 0.2s, box-shadow 0.2s',
                    cursor: 'pointer'
                  }}
                  onClick={() => router.push(`/report-writer/editor/${doc.id}`)}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 8px 25px 0 rgba(0, 0, 0, 0.15)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = '0 1px 3px 0 rgba(0, 0, 0, 0.1)';
                  }}
                >
                  {/* Status Badge */}
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    marginBottom: '16px'
                  }}>
                    <span style={{
                      fontSize: '12px',
                      fontWeight: '600',
                      padding: '4px 12px',
                      borderRadius: '12px'
                    }} className={getStatusColor(doc.status)}>
                      {doc.status.replace('_', ' ').toUpperCase()}
                    </span>
                    
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        // Show options menu
                      }}
                      style={{
                        backgroundColor: 'transparent',
                        border: 'none',
                        cursor: 'pointer',
                        padding: '4px',
                        color: '#6b7280'
                      }}
                    >
                      <MoreVertical size={16} />
                    </button>
                  </div>

                  {/* Title and Description */}
                  <h3 style={{
                    fontSize: '18px',
                    fontWeight: '600',
                    color: '#111827',
                    marginBottom: '8px',
                    lineHeight: '1.3'
                  }}>
                    {doc.title}
                  </h3>
                  
                  <p style={{
                    fontSize: '14px',
                    color: '#6b7280',
                    marginBottom: '16px',
                    lineHeight: '1.5'
                  }}>
                    {doc.description}
                  </p>

                  {/* Template Info */}
                  <div style={{
                    fontSize: '12px',
                    color: '#374151',
                    backgroundColor: '#f3f4f6',
                    padding: '6px 12px',
                    borderRadius: '6px',
                    marginBottom: '16px',
                    fontWeight: '500'
                  }}>
                    📋 {doc.content.template_used.name}
                  </div>

                  {/* Progress Bar */}
                  <div style={{ marginBottom: '16px' }}>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      marginBottom: '6px'
                    }}>
                      <span style={{
                        fontSize: '12px',
                        fontWeight: '600',
                        color: '#374151'
                      }}>
                        Progress
                      </span>
                      <span style={{
                        fontSize: '12px',
                        color: '#6b7280'
                      }}>
                        {completionPercentage}%
                      </span>
                    </div>
                    
                    <div style={{
                      width: '100%',
                      height: '6px',
                      backgroundColor: '#f3f4f6',
                      borderRadius: '3px',
                      overflow: 'hidden'
                    }}>
                      <div style={{
                        width: `${completionPercentage}%`,
                        height: '100%',
                        backgroundColor: completionPercentage === 100 ? '#10b981' : '#3b82f6',
                        transition: 'width 0.3s ease'
                      }} />
                    </div>
                  </div>

                  {/* Sections Summary */}
                  <div style={{ marginBottom: '16px' }}>
                    <span style={{
                      fontSize: '12px',
                      color: '#6b7280',
                      fontWeight: '500'
                    }}>
                      Sections: {doc.content.sections.filter(s => s.completed).length}/{doc.content.sections.length} completed
                    </span>
                  </div>

                  {/* Footer */}
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    paddingTop: '16px',
                    borderTop: '1px solid #f3f4f6'
                  }}>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px',
                      fontSize: '12px',
                      color: '#6b7280'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <Calendar size={12} />
                        {new Date(doc.updated_at).toLocaleDateString()}
                      </div>
                    </div>
                    
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        router.push(`/report-writer/editor/${doc.id}`);
                      }}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                        padding: '6px 12px',
                        backgroundColor: '#f3f4f6',
                        border: 'none',
                        borderRadius: '6px',
                        fontSize: '12px',
                        fontWeight: '500',
                        color: '#374151',
                        cursor: 'pointer'
                      }}
                    >
                      <Edit3 size={12} />
                      Edit
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
} 