'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft, Save, Sparkles, FileText } from 'lucide-react';

interface DocumentSection {
  id: string;
  title: string;
  type: string;
  content: string;
  ai_generated: boolean;
  completed: boolean;
}

interface Document {
  id: number;
  title: string;
  description: string;
  template_id: number;
  content: {
    template_used: any;
    sections: DocumentSection[];
  };
  created_at: string;
  updated_at: string;
}

export default function DocumentEditorPage() {
  const params = useParams();
  const router = useRouter();
  const documentId = params.id as string;
  
  const [document, setDocument] = useState<Document | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeSection, setActiveSection] = useState<string>('');

  useEffect(() => {
    // Mock data for development
    const mockDocument: Document = {
      id: parseInt(documentId),
      title: "Q4 Financial Performance Report",
      description: "Comprehensive quarterly financial analysis",
      template_id: 1,
      content: {
        template_used: { name: "Financial Quarterly Report" },
        sections: [
          {
            id: "section_1",
            title: "Executive Summary",
            type: "executive_summary",
            content: "",
            ai_generated: true,
            completed: false
          },
          {
            id: "section_2", 
            title: "Revenue Analysis",
            type: "data_analysis",
            content: "",
            ai_generated: true,
            completed: false
          }
        ]
      },
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    
    setDocument(mockDocument);
    setActiveSection("section_1");
    setLoading(false);
  }, [documentId]);

  const currentSection = document?.content.sections.find(s => s.id === activeSection);

  if (loading) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#f8fafc'
      }}>
        <p>Loading document...</p>
      </div>
    );
  }

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#f8fafc',
      display: 'flex',
      flexDirection: 'column'
    }}>
      {/* Header */}
      <header style={{
        backgroundColor: 'white',
        borderBottom: '1px solid #e5e7eb',
        padding: '12px 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <button
            onClick={() => router.push('/report-writer')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '8px 12px',
              backgroundColor: 'transparent',
              border: '1px solid #d1d5db',
              borderRadius: '6px',
              cursor: 'pointer'
            }}
          >
            <ArrowLeft size={16} />
            Back
          </button>
          
          <h1 style={{
            fontSize: '18px',
            fontWeight: '600',
            color: '#111827',
            margin: 0
          }}>
            {document?.title}
          </h1>
        </div>

        <button style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          padding: '8px 16px',
          backgroundColor: '#10b981',
          color: 'white',
          border: 'none',
          borderRadius: '6px',
          cursor: 'pointer'
        }}>
          <Save size={16} />
          Save
        </button>
      </header>

      {/* Main Layout */}
      <div style={{ display: 'flex', flex: 1 }}>
        {/* Sidebar */}
        <aside style={{
          width: '300px',
          backgroundColor: 'white',
          borderRight: '1px solid #e5e7eb',
          padding: '16px'
        }}>
          <h3 style={{ marginBottom: '16px' }}>Document Outline</h3>
          {document?.content.sections.map((section, index) => (
            <div
              key={section.id}
              onClick={() => setActiveSection(section.id)}
              style={{
                padding: '12px',
                borderRadius: '8px',
                backgroundColor: activeSection === section.id ? '#eff6ff' : 'transparent',
                cursor: 'pointer',
                marginBottom: '8px'
              }}
            >
              {index + 1}. {section.title}
            </div>
          ))}
        </aside>

        {/* Editor */}
        <main style={{ flex: 1, padding: '24px' }}>
          {currentSection ? (
            <div>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                marginBottom: '24px'
              }}>
                <h2 style={{ fontSize: '24px', margin: 0 }}>
                  {currentSection.title}
                </h2>
                
                {currentSection.ai_generated && (
                  <button style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '8px 16px',
                    backgroundColor: '#8b5cf6',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer'
                  }}>
                    <Sparkles size={16} />
                    Generate with AI
                  </button>
                )}
              </div>

              <div style={{
                backgroundColor: 'white',
                borderRadius: '8px',
                padding: '24px',
                minHeight: '500px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
              }}>
                <textarea
                  value={currentSection.content}
                  onChange={(e) => {
                    // Update section content
                    const updatedSections = document!.content.sections.map(s => 
                      s.id === currentSection.id 
                        ? { ...s, content: e.target.value }
                        : s
                    );
                    setDocument({
                      ...document!,
                      content: {
                        ...document!.content,
                        sections: updatedSections
                      }
                    });
                  }}
                  placeholder={`Start writing your ${currentSection.title.toLowerCase()}...`}
                  style={{
                    width: '100%',
                    height: '400px',
                    border: 'none',
                    outline: 'none',
                    resize: 'none',
                    fontSize: '16px',
                    lineHeight: '1.6',
                    fontFamily: 'system-ui, -apple-system, sans-serif'
                  }}
                />
              </div>
            </div>
          ) : (
            <div style={{
              textAlign: 'center',
              padding: '64px',
              color: '#6b7280'
            }}>
              <FileText size={48} style={{ marginBottom: '16px' }} />
              <h3>Select a Section</h3>
              <p>Choose a section from the outline to start editing</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
} 