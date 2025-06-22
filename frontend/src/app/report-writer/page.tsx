'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ChevronRight, FileText, BarChart3, TrendingUp, Users, Building2 } from 'lucide-react';
import { apiCall } from '../../config/api';

// Template categories with icons
const TEMPLATE_CATEGORIES = [
  {
    id: 'financial',
    name: 'Financial Reports',
    icon: TrendingUp,
    description: 'Quarterly reports, budget analysis, financial forecasting',
    color: 'bg-green-100 text-green-600'
  },
  {
    id: 'marketing',
    name: 'Marketing Analytics',
    icon: BarChart3,
    description: 'Campaign performance, ROI analysis, customer insights',
    color: 'bg-blue-100 text-blue-600'
  },
  {
    id: 'sales',
    name: 'Sales Performance',
    icon: Users,
    description: 'Territory analysis, pipeline forecasting, team performance',
    color: 'bg-purple-100 text-purple-600'
  },
  {
    id: 'operational',
    name: 'Operational Reports',
    icon: Building2,
    description: 'Efficiency metrics, process analysis, resource utilization',
    color: 'bg-orange-100 text-orange-600'
  }
];

interface Template {
  id: number;
  name: string;
  description: string;
  category: string;
  sections: Array<{name: string; type: string; ai_generated: boolean}>;
  usage_count: number;
  is_featured: boolean;
}

export default function ReportWriterPage() {
  const router = useRouter();
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch templates when category changes
  useEffect(() => {
    fetchTemplates(selectedCategory === 'all' ? null : selectedCategory);
  }, [selectedCategory]);

  const fetchTemplates = async (category: string | null) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiCall(
        `/api/report-writer/templates${category ? `?category=${category}` : ''}`,
        {
          method: 'GET',
        }
      );
      
      if (!response.ok) {
        throw new Error(`Failed to fetch templates: ${response.status}`);
      }
      
      const data = await response.json();
      setTemplates(data);
      
    } catch (error) {
      console.error('Error fetching templates:', error);
      setError(error instanceof Error ? error.message : 'Failed to load templates');
      // Set mock data for development
      setTemplates([
        {
          id: 1,
          name: "Financial Quarterly Report",
          description: "Comprehensive quarterly financial analysis with P&L, cash flow, and forecasting sections",
          category: "financial",
          sections: [
            {name: "Executive Summary", type: "executive_summary", ai_generated: true},
            {name: "Revenue Analysis", type: "data_analysis", ai_generated: true},
            {name: "Financial Forecasting", type: "insights", ai_generated: true},
            {name: "Recommendations", type: "recommendations", ai_generated: true}
          ],
          usage_count: 45,
          is_featured: true
        },
        {
          id: 2,
          name: "Marketing Campaign Analysis",
          description: "Marketing performance analysis with ROI, conversion metrics, and customer acquisition data",
          category: "marketing",
          sections: [
            {name: "Campaign Overview", type: "executive_summary", ai_generated: true},
            {name: "Performance Metrics", type: "data_analysis", ai_generated: true},
            {name: "ROI Analysis", type: "data_analysis", ai_generated: true},
            {name: "Customer Insights", type: "insights", ai_generated: true}
          ],
          usage_count: 32,
          is_featured: true
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const createReport = async (template: Template) => {
    try {
      const response = await apiCall('/api/report-writer/documents', {
        method: 'POST',
        body: JSON.stringify({
          title: `New ${template.name}`,
          description: `Report created from ${template.name} template`,
          template_id: template.id,
          content: {
            template_used: template,
            sections: template.sections.map((section, index) => ({
              id: `section_${index + 1}`,
              title: section.name,
              type: section.type,
              content: "",
              ai_generated: section.ai_generated,
              completed: false
            }))
          }
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to create report: ${response.status}`);
      }

      const newReport = await response.json();
      console.log('Report created:', newReport);
      
      // Navigate to editor page
      router.push(`/report-writer/editor/${newReport.id}`);
      
    } catch (error) {
      console.error('Error creating report:', error);
      alert('Failed to create report. Please try again.');
    }
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
              Interactive Analytics Report Writer
            </h1>
            <p style={{
              color: '#6b7280',
              marginTop: '8px',
              margin: '8px 0 0 0',
              fontSize: '16px'
            }}>
              Create professional business reports with AI-powered insights
            </p>
          </div>
          
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '16px'
          }}>
            <button 
              onClick={() => router.push('/report-writer/documents')}
              style={{
                padding: '8px 16px',
                backgroundColor: 'white',
                border: '1px solid #d1d5db',
                borderRadius: '8px',
                fontSize: '14px',
                color: '#374151',
                cursor: 'pointer'
              }}
            >
              My Reports
            </button>
            <button style={{
              padding: '8px 16px',
              backgroundColor: '#3b82f6',
              border: 'none',
              borderRadius: '8px',
              fontSize: '14px',
              color: 'white',
              cursor: 'pointer',
              fontWeight: '500'
            }}>
              Settings
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
        {/* Category Selection */}
        <div style={{ marginBottom: '40px' }}>
          <h2 style={{
            fontSize: '24px',
            fontWeight: '600',
            color: '#111827',
            marginBottom: '16px'
          }}>
            Choose Your Report Type
          </h2>
          
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '16px',
            marginBottom: '32px'
          }}>
            <button
              onClick={() => setSelectedCategory('all')}
              style={{
                padding: '20px',
                backgroundColor: selectedCategory === 'all' ? '#eff6ff' : 'white',
                border: selectedCategory === 'all' ? '2px solid #3b82f6' : '1px solid #e5e7eb',
                borderRadius: '12px',
                textAlign: 'left' as const,
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            >
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                marginBottom: '8px'
              }}>
                <div style={{
                  width: '40px',
                  height: '40px',
                  backgroundColor: '#f3f4f6',
                  borderRadius: '8px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  <FileText size={20} color="#6b7280" />
                </div>
                <h3 style={{
                  fontSize: '16px',
                  fontWeight: '600',
                  color: '#111827',
                  margin: 0
                }}>
                  All Templates
                </h3>
              </div>
              <p style={{
                fontSize: '14px',
                color: '#6b7280',
                margin: 0
              }}>
                Browse all available report templates
              </p>
            </button>

            {TEMPLATE_CATEGORIES.map((category) => {
              const Icon = category.icon;
              return (
                <button
                  key={category.id}
                  onClick={() => setSelectedCategory(category.id)}
                  style={{
                    padding: '20px',
                    backgroundColor: selectedCategory === category.id ? '#eff6ff' : 'white',
                    border: selectedCategory === category.id ? '2px solid #3b82f6' : '1px solid #e5e7eb',
                    borderRadius: '12px',
                    textAlign: 'left' as const,
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                >
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    marginBottom: '8px'
                  }}>
                    <div style={{
                      width: '40px',
                      height: '40px',
                      borderRadius: '8px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }} className={category.color}>
                      <Icon size={20} />
                    </div>
                    <h3 style={{
                      fontSize: '16px',
                      fontWeight: '600',
                      color: '#111827',
                      margin: 0
                    }}>
                      {category.name}
                    </h3>
                  </div>
                  <p style={{
                    fontSize: '14px',
                    color: '#6b7280',
                    margin: 0
                  }}>
                    {category.description}
                  </p>
                </button>
              );
            })}
          </div>
        </div>

        {/* Templates Grid */}
        <div>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '24px'
          }}>
            <h2 style={{
              fontSize: '20px',
              fontWeight: '600',
              color: '#111827',
              margin: 0
            }}>
              Available Templates
            </h2>
            <span style={{
              fontSize: '14px',
              color: '#6b7280'
            }}>
              {loading ? 'Loading...' : `${templates.length} templates`}
            </span>
          </div>

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
              gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
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
          ) : (
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
              gap: '24px'
            }}>
              {templates.map((template) => (
                <div
                  key={template.id}
                  style={{
                    backgroundColor: 'white',
                    borderRadius: '12px',
                    padding: '24px',
                    boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
                    border: '1px solid #e5e7eb',
                    position: 'relative',
                    transition: 'transform 0.2s, box-shadow 0.2s'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 8px 25px 0 rgba(0, 0, 0, 0.15)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = '0 1px 3px 0 rgba(0, 0, 0, 0.1)';
                  }}
                >
                  {template.is_featured && (
                    <div style={{
                      position: 'absolute',
                      top: '16px',
                      right: '16px',
                      backgroundColor: '#fbbf24',
                      color: 'white',
                      fontSize: '12px',
                      fontWeight: '600',
                      padding: '4px 8px',
                      borderRadius: '12px'
                    }}>
                      Featured
                    </div>
                  )}

                  <h3 style={{
                    fontSize: '18px',
                    fontWeight: '600',
                    color: '#111827',
                    marginBottom: '8px',
                    marginTop: 0
                  }}>
                    {template.name}
                  </h3>

                  <p style={{
                    fontSize: '14px',
                    color: '#6b7280',
                    marginBottom: '16px',
                    lineHeight: '1.5'
                  }}>
                    {template.description}
                  </p>

                  <div style={{ marginBottom: '16px' }}>
                    <h4 style={{
                      fontSize: '14px',
                      fontWeight: '600',
                      color: '#374151',
                      marginBottom: '8px',
                      marginTop: 0
                    }}>
                      Sections ({template.sections.length}):
                    </h4>
                    <div style={{
                      display: 'flex',
                      flexWrap: 'wrap',
                      gap: '6px'
                    }}>
                      {template.sections.slice(0, 4).map((section, index) => (
                        <span
                          key={index}
                          style={{
                            fontSize: '12px',
                            backgroundColor: section.ai_generated ? '#dbeafe' : '#f3f4f6',
                            color: section.ai_generated ? '#1e40af' : '#374151',
                            padding: '4px 8px',
                            borderRadius: '12px',
                            fontWeight: '500'
                          }}
                        >
                          {section.name}
                        </span>
                      ))}
                      {template.sections.length > 4 && (
                        <span style={{
                          fontSize: '12px',
                          color: '#6b7280',
                          padding: '4px 8px'
                        }}>
                          +{template.sections.length - 4} more
                        </span>
                      )}
                    </div>
                  </div>

                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between'
                  }}>
                    <span style={{
                      fontSize: '12px',
                      color: '#6b7280'
                    }}>
                      Used {template.usage_count} times
                    </span>

                    <button
                      onClick={() => createReport(template)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        padding: '8px 16px',
                        backgroundColor: '#3b82f6',
                        color: 'white',
                        border: 'none',
                        borderRadius: '8px',
                        fontSize: '14px',
                        fontWeight: '500',
                        cursor: 'pointer',
                        transition: 'background-color 0.2s'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.backgroundColor = '#2563eb';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.backgroundColor = '#3b82f6';
                      }}
                    >
                      Create Report
                      <ChevronRight size={16} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {!loading && templates.length === 0 && (
            <div style={{
              textAlign: 'center' as const,
              padding: '64px',
              backgroundColor: 'white',
              borderRadius: '12px',
              border: '1px solid #e5e7eb'
            }}>
              <FileText size={48} color="#d1d5db" style={{ marginBottom: '16px' }} />
              <h3 style={{
                fontSize: '18px',
                fontWeight: '600',
                color: '#374151',
                marginBottom: '8px'
              }}>
                No templates found
              </h3>
              <p style={{
                fontSize: '14px',
                color: '#6b7280'
              }}>
                Try selecting a different category or check back later.
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
} 