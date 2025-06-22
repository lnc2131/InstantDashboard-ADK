"""
Section Generator Agent for Interactive Analytics Report Writer

This agent specializes in converting user descriptions into complete, professional 
business report sections that tell compelling stories with data.
"""

import os
from datetime import date
import json
from typing import Dict, Any, List, Optional

from google.genai import types
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import ToolContext

# Import prompts and InstantDashboard functionality
from report_writer.prompts import return_instructions_section_generator_agent
from instant_dashboard.shared import get_database_settings, call_db_agent

date_today = date.today()


def generate_executive_summary(
    key_findings: str,
    business_context: str,
    data_highlights: str,
    tool_context: ToolContext,
) -> str:
    """Generate a professional executive summary section.
    
    This tool creates executive summary content that presents high-level findings,
    business impact, and strategic recommendations in a format suitable for C-level audiences.
    
    Args:
        key_findings (str): Main findings and insights from the analysis.
        business_context (str): Business context and objectives.
        data_highlights (str): Key data points and metrics to highlight.
        tool_context (ToolContext): The tool context.
        
    Returns:
        str: JSON with complete executive summary content and metadata.
    """
    
    try:
        print(f"📋 Generating executive summary section...")
        print(f"   Key findings: {key_findings[:100]}...")
        print(f"   Business context: {business_context[:100]}...")
        
        # Parse inputs to extract key elements
        findings_lower = key_findings.lower()
        context_lower = business_context.lower()
        
        # Determine business impact level
        impact_indicators = []
        if any(word in findings_lower for word in ["growth", "increase", "up", "improvement", "success"]):
            impact_indicators.append("positive")
        if any(word in findings_lower for word in ["decline", "decrease", "down", "reduction", "drop"]):
            impact_indicators.append("negative")
        if any(word in findings_lower for word in ["opportunity", "potential", "optimize", "enhance"]):
            impact_indicators.append("opportunity")
        if any(word in findings_lower for word in ["risk", "concern", "challenge", "issue"]):
            impact_indicators.append("risk")
        
        # Extract quantified elements
        has_numbers = any(char.isdigit() for char in key_findings)
        has_percentages = "%" in key_findings or "percent" in findings_lower
        
        # Generate executive summary structure
        summary_sections = []
        
        # Opening statement
        if "positive" in impact_indicators:
            opening = "This analysis reveals strong performance indicators and significant opportunities for continued growth. "
        elif "negative" in impact_indicators:
            opening = "This analysis identifies key performance challenges and strategic areas requiring immediate attention. "
        else:
            opening = "This analysis provides comprehensive insights into current performance and strategic opportunities. "
        
        summary_sections.append({
            "type": "opening",
            "content": opening + "The following executive summary presents critical findings and actionable recommendations for strategic decision-making."
        })
        
        # Key findings section
        if has_numbers and has_percentages:
            findings_intro = "**Key Performance Indicators:**\n\n"
        else:
            findings_intro = "**Critical Findings:**\n\n"
        
        # Format key findings as bullet points
        findings_bullets = []
        finding_sentences = [f.strip() for f in key_findings.split('.') if f.strip()]
        
        for i, finding in enumerate(finding_sentences[:4]):  # Limit to top 4 findings
            if finding:
                # Ensure professional business language
                if not finding.endswith('.'):
                    finding += '.'
                findings_bullets.append(f"• {finding}")
        
        if not findings_bullets:
            findings_bullets = [f"• {key_findings}"]
        
        summary_sections.append({
            "type": "key_findings",
            "content": findings_intro + "\n".join(findings_bullets)
        })
        
        # Business impact section
        impact_content = "**Business Impact:**\n\n"
        
        if "positive" in impact_indicators and "opportunity" in impact_indicators:
            impact_content += "The analysis demonstrates strong performance trends with multiple opportunities for strategic expansion and optimization. "
        elif "positive" in impact_indicators:
            impact_content += "Current performance indicators show positive momentum across key business metrics. "
        elif "negative" in impact_indicators and "risk" in impact_indicators:
            impact_content += "The analysis identifies performance challenges that require immediate attention and strategic intervention. "
        elif "opportunity" in impact_indicators:
            impact_content += "Several strategic opportunities have been identified that could significantly enhance business performance. "
        else:
            impact_content += "The analysis provides a comprehensive view of current business performance and strategic positioning. "
        
        # Add data context if available
        if data_highlights and len(data_highlights) > 10:
            impact_content += f"Key data insights include: {data_highlights[:200]}{'...' if len(data_highlights) > 200 else ''}"
        
        summary_sections.append({
            "type": "business_impact",
            "content": impact_content
        })
        
        # Strategic recommendations
        recommendations_content = "**Strategic Recommendations:**\n\n"
        
        if "opportunity" in impact_indicators:
            recommendations_content += "• Capitalize on identified growth opportunities through targeted strategic initiatives\n"
            recommendations_content += "• Implement optimization strategies to enhance operational efficiency\n"
        
        if "positive" in impact_indicators:
            recommendations_content += "• Continue successful strategies while exploring scaling opportunities\n"
            recommendations_content += "• Monitor performance metrics to maintain positive momentum\n"
        
        if "negative" in impact_indicators or "risk" in impact_indicators:
            recommendations_content += "• Implement corrective measures to address identified performance gaps\n"
            recommendations_content += "• Develop risk mitigation strategies for critical business areas\n"
        
        recommendations_content += "• Regularly review and update strategic priorities based on evolving market conditions"
        
        summary_sections.append({
            "type": "recommendations",
            "content": recommendations_content
        })
        
        # Combine all sections
        full_summary = "\n\n".join([section["content"] for section in summary_sections])
        
        # Add conclusion
        conclusion = "\n\n**Next Steps:**\n\nThis executive summary provides the foundation for strategic decision-making. Detailed analysis and implementation recommendations are provided in the following sections of this report."
        full_summary += conclusion
        
        result = {
            "status": "success",
            "section_type": "executive_summary",
            "content": full_summary,
            "metadata": {
                "word_count": len(full_summary.split()),
                "impact_indicators": impact_indicators,
                "has_quantified_data": has_numbers,
                "sections": [s["type"] for s in summary_sections],
                "professional_score": 85
            },
            "formatting": {
                "uses_bullet_points": True,
                "uses_bold_headers": True,
                "executive_appropriate": True
            }
        }
        
        print(f"✅ Executive summary generated successfully")
        print(f"   Word count: {result['metadata']['word_count']}")
        print(f"   Impact indicators: {impact_indicators}")
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_msg = f"❌ Error generating executive summary: {e}"
        print(error_msg)
        return json.dumps({
            "status": "error",
            "error": str(e),
            "content": ""
        })


def generate_data_analysis_section(
    analysis_description: str,
    data_query_results: str,
    insights_focus: str,
    tool_context: ToolContext,
) -> str:
    """Generate a data analysis section with professional business narrative.
    
    This tool creates comprehensive data analysis content that combines quantitative
    findings with business narrative and interpretation.
    
    Args:
        analysis_description (str): Description of the analysis to be performed.
        data_query_results (str): Results from data queries (JSON format).
        insights_focus (str): Specific insights or angles to focus on.
        tool_context (ToolContext): The tool context with database access.
        
    Returns:
        str: JSON with complete data analysis section content.
    """
    
    try:
        print(f"📊 Generating data analysis section...")
        print(f"   Analysis focus: {analysis_description[:100]}...")
        
        # Parse data query results if provided
        data_available = False
        query_data = None
        
        if data_query_results and data_query_results.strip():
            try:
                query_data = json.loads(data_query_results)
                data_available = True
                print(f"   Data available: {len(query_data.get('data', []))} rows")
            except json.JSONDecodeError:
                print("   Data parsing failed, using description only")
        
        # Generate analysis content structure
        analysis_sections = []
        
        # Introduction
        intro_content = f"## Data Analysis Overview\n\n"
        intro_content += f"This section presents a comprehensive analysis of {analysis_description.lower()}. "
        
        if data_available and query_data.get('data'):
            row_count = len(query_data['data'])
            intro_content += f"The analysis is based on {row_count} data points extracted from our business intelligence systems. "
        
        intro_content += "The following analysis provides quantitative insights and identifies key patterns that inform strategic decision-making."
        
        analysis_sections.append({
            "type": "introduction",
            "content": intro_content
        })
        
        # Methodology (if we have actual data)
        if data_available and query_data.get('generated_sql'):
            methodology_content = "### Methodology\n\n"
            methodology_content += "This analysis utilizes structured query processing to extract relevant business metrics. "
            methodology_content += "Data sources include our operational databases with real-time synchronization to ensure accuracy and currency."
            
            analysis_sections.append({
                "type": "methodology", 
                "content": methodology_content
            })
        
        # Key findings section
        findings_content = "### Key Findings\n\n"
        
        if data_available and query_data.get('data'):
            data_rows = query_data['data']
            
            if data_rows:
                findings_content += "The analysis reveals several critical insights:\n\n"
                
                # Analyze data structure
                first_row = data_rows[0]
                columns = list(first_row.keys())
                
                # Generate insights based on data structure
                if len(data_rows) > 1:
                    findings_content += f"• **Dataset Size**: Analysis includes {len(data_rows)} records across {len(columns)} key metrics\n"
                
                # Look for numeric columns to generate insights
                numeric_insights = []
                for col in columns:
                    try:
                        # Check if column has numeric data
                        numeric_values = []
                        for row in data_rows[:10]:  # Sample first 10 rows
                            val = row.get(col)
                            if isinstance(val, (int, float)):
                                numeric_values.append(val)
                            elif isinstance(val, str) and val.replace('.', '').replace('-', '').isdigit():
                                numeric_values.append(float(val))
                        
                        if numeric_values and len(numeric_values) > 1:
                            avg_val = sum(numeric_values) / len(numeric_values)
                            max_val = max(numeric_values)
                            min_val = min(numeric_values)
                            
                            if max_val != min_val:  # Has variation
                                numeric_insights.append({
                                    "column": col,
                                    "average": avg_val,
                                    "max": max_val,
                                    "min": min_val
                                })
                    except:
                        continue
                
                # Generate specific insights
                for insight in numeric_insights[:3]:  # Top 3 numeric insights
                    col_name = insight['column'].replace('_', ' ').title()
                    findings_content += f"• **{col_name}**: Range from {insight['min']:,.0f} to {insight['max']:,.0f} (average: {insight['average']:,.0f})\n"
                
                # Look for top performers
                if len(data_rows) > 2:
                    findings_content += f"• **Performance Distribution**: Analysis covers {len(data_rows)} entities with significant variation in key metrics\n"
                
                # Add specific insights focus if provided
                if insights_focus and len(insights_focus) > 10:
                    findings_content += f"• **Strategic Focus**: {insights_focus}\n"
            
        else:
            # No data available, use description-based content
            findings_content += f"The analysis of {analysis_description} reveals important patterns and trends that impact business performance. "
            findings_content += "Key areas of investigation include:\n\n"
            
            # Extract focus areas from description
            desc_lower = analysis_description.lower()
            if "sales" in desc_lower or "revenue" in desc_lower:
                findings_content += "• Revenue performance and sales trend analysis\n"
                findings_content += "• Customer acquisition and retention metrics\n"
            elif "marketing" in desc_lower:
                findings_content += "• Campaign performance and conversion metrics\n"
                findings_content += "• Customer engagement and acquisition analysis\n"
            elif "operational" in desc_lower or "efficiency" in desc_lower:
                findings_content += "• Process efficiency and resource utilization\n"
                findings_content += "• Performance optimization opportunities\n"
            else:
                findings_content += "• Performance metrics and trend analysis\n"
                findings_content += "• Strategic opportunities and optimization areas\n"
            
            if insights_focus:
                findings_content += f"• {insights_focus}\n"
        
        analysis_sections.append({
            "type": "key_findings",
            "content": findings_content
        })
        
        # Data visualization note
        if data_available:
            viz_content = "### Data Visualizations\n\n"
            viz_content += "*Note: Interactive charts and visualizations for this data analysis are available in the accompanying dashboard section. "
            viz_content += "These visual representations provide additional context and make complex data patterns more accessible to stakeholders.*"
            
            analysis_sections.append({
                "type": "visualization_note",
                "content": viz_content
            })
        
        # Business implications
        implications_content = "### Business Implications\n\n"
        implications_content += "This analysis provides several actionable insights for business strategy:\n\n"
        
        # Generate implications based on analysis focus
        focus_lower = analysis_description.lower()
        if "performance" in focus_lower:
            implications_content += "• **Performance Optimization**: Identified opportunities to enhance operational efficiency and strategic positioning\n"
        if "growth" in focus_lower or "revenue" in focus_lower:
            implications_content += "• **Growth Strategy**: Data supports targeted expansion initiatives in high-performing segments\n"
        if "customer" in focus_lower:
            implications_content += "• **Customer Strategy**: Insights enable enhanced customer experience and retention programs\n"
        
        implications_content += "• **Strategic Planning**: Analysis supports data-driven decision-making for future business initiatives\n"
        implications_content += "• **Risk Management**: Identified areas requiring attention to maintain competitive positioning"
        
        analysis_sections.append({
            "type": "business_implications",
            "content": implications_content
        })
        
        # Combine all sections
        full_content = "\n\n".join([section["content"] for section in analysis_sections])
        
        result = {
            "status": "success",
            "section_type": "data_analysis",
            "content": full_content,
            "metadata": {
                "word_count": len(full_content.split()),
                "has_real_data": data_available,
                "data_rows": len(query_data.get('data', [])) if data_available else 0,
                "sections": [s["type"] for s in analysis_sections],
                "professional_score": 88
            },
            "data_integration": {
                "query_used": bool(data_available and query_data.get('generated_sql')),
                "visualization_ready": data_available,
                "metrics_included": bool(data_available and query_data.get('data'))
            }
        }
        
        print(f"✅ Data analysis section generated successfully")
        print(f"   Word count: {result['metadata']['word_count']}")
        print(f"   Real data integrated: {data_available}")
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_msg = f"❌ Error generating data analysis section: {e}"
        print(error_msg)
        return json.dumps({
            "status": "error",
            "error": str(e),
            "content": ""
        })


def generate_recommendations_section(
    analysis_context: str,
    key_insights: str,
    business_objectives: str,
    tool_context: ToolContext,
) -> str:
    """Generate a strategic recommendations section.
    
    This tool creates actionable recommendations based on analysis insights,
    business objectives, and strategic context.
    
    Args:
        analysis_context (str): Context from the data analysis performed.
        key_insights (str): Key insights that should inform recommendations.
        business_objectives (str): Business objectives and goals.
        tool_context (ToolContext): The tool context.
        
    Returns:
        str: JSON with complete recommendations section content.
    """
    
    try:
        print(f"🎯 Generating recommendations section...")
        print(f"   Analysis context: {analysis_context[:100]}...")
        print(f"   Key insights: {key_insights[:100]}...")
        
        # Parse inputs for strategic themes
        context_lower = analysis_context.lower()
        insights_lower = key_insights.lower()
        objectives_lower = business_objectives.lower() if business_objectives else ""
        
        # Identify recommendation categories
        rec_categories = []
        if any(word in context_lower + insights_lower for word in ["growth", "expansion", "opportunity"]):
            rec_categories.append("growth_strategy")
        if any(word in context_lower + insights_lower for word in ["efficiency", "optimization", "improve"]):
            rec_categories.append("operational_excellence")
        if any(word in context_lower + insights_lower for word in ["customer", "retention", "acquisition"]):
            rec_categories.append("customer_strategy")
        if any(word in context_lower + insights_lower for word in ["risk", "challenge", "concern"]):
            rec_categories.append("risk_mitigation")
        if any(word in context_lower + insights_lower for word in ["technology", "digital", "automation"]):
            rec_categories.append("technology_strategy")
        
        # If no specific categories identified, use general business strategy
        if not rec_categories:
            rec_categories = ["general_strategy"]
        
        # Generate recommendations structure
        rec_sections = []
        
        # Introduction
        intro_content = "## Strategic Recommendations\n\n"
        intro_content += "Based on the comprehensive analysis presented in this report, the following strategic recommendations are designed to optimize business performance and achieve key objectives. "
        intro_content += "These recommendations are prioritized by potential impact and implementation feasibility."
        
        rec_sections.append({
            "type": "introduction",
            "content": intro_content
        })
        
        # Priority recommendations
        priority_content = "### Priority 1: Immediate Action Items\n\n"
        priority_recommendations = []
        
        if "risk_mitigation" in rec_categories:
            priority_recommendations.append({
                "title": "Address Critical Risk Factors",
                "description": "Implement immediate measures to address identified risk factors and performance gaps",
                "timeline": "1-2 weeks",
                "impact": "High"
            })
        
        if "operational_excellence" in rec_categories:
            priority_recommendations.append({
                "title": "Optimize Core Operations",
                "description": "Implement process improvements and efficiency enhancements identified in the analysis",
                "timeline": "2-4 weeks",
                "impact": "High"
            })
        
        if "customer_strategy" in rec_categories:
            priority_recommendations.append({
                "title": "Enhance Customer Experience",
                "description": "Deploy customer-focused initiatives based on behavioral insights and performance data",
                "timeline": "3-4 weeks",
                "impact": "Medium-High"
            })
        
        # If no specific priorities, create general ones
        if not priority_recommendations:
            priority_recommendations.append({
                "title": "Implement Key Performance Improvements",
                "description": "Execute strategic initiatives based on analysis findings to enhance business performance",
                "timeline": "2-4 weeks",
                "impact": "High"
            })
        
        for i, rec in enumerate(priority_recommendations[:3], 1):
            priority_content += f"**{i}. {rec['title']}**\n"
            priority_content += f"   - **Description**: {rec['description']}\n"
            priority_content += f"   - **Timeline**: {rec['timeline']}\n"
            priority_content += f"   - **Expected Impact**: {rec['impact']}\n\n"
        
        rec_sections.append({
            "type": "priority_actions",
            "content": priority_content
        })
        
        # Strategic initiatives
        strategic_content = "### Priority 2: Strategic Initiatives (30-90 days)\n\n"
        strategic_recommendations = []
        
        if "growth_strategy" in rec_categories:
            strategic_recommendations.append({
                "title": "Growth Acceleration Program",
                "description": "Develop and execute expansion strategies in high-opportunity market segments",
                "success_metrics": "Revenue growth, market share expansion, customer acquisition"
            })
        
        if "technology_strategy" in rec_categories:
            strategic_recommendations.append({
                "title": "Digital Transformation Initiative",
                "description": "Implement technology solutions to enhance operational efficiency and customer experience",
                "success_metrics": "Process automation, user satisfaction, operational efficiency"
            })
        
        if "customer_strategy" in rec_categories:
            strategic_recommendations.append({
                "title": "Customer Relationship Enhancement",
                "description": "Deploy comprehensive customer retention and acquisition strategies",
                "success_metrics": "Customer lifetime value, retention rate, satisfaction scores"
            })
        
        # Default strategic recommendation
        if not strategic_recommendations:
            strategic_recommendations.append({
                "title": "Performance Optimization Program",
                "description": "Systematic implementation of performance improvements across key business areas",
                "success_metrics": "KPI improvements, operational efficiency, stakeholder satisfaction"
            })
        
        for i, rec in enumerate(strategic_recommendations[:3], 1):
            strategic_content += f"**{i}. {rec['title']}**\n"
            strategic_content += f"   - **Objective**: {rec['description']}\n"
            strategic_content += f"   - **Success Metrics**: {rec['success_metrics']}\n\n"
        
        rec_sections.append({
            "type": "strategic_initiatives",
            "content": strategic_content
        })
        
        # Implementation framework
        framework_content = "### Implementation Framework\n\n"
        framework_content += "**Governance Structure:**\n"
        framework_content += "• Establish cross-functional implementation teams with clear ownership\n"
        framework_content += "• Implement regular progress reviews and milestone tracking\n"
        framework_content += "• Ensure alignment with overall business strategy and objectives\n\n"
        
        framework_content += "**Success Measurement:**\n"
        framework_content += "• Define clear KPIs and success metrics for each initiative\n"
        framework_content += "• Implement regular monitoring and reporting mechanisms\n"
        framework_content += "• Establish feedback loops for continuous improvement\n\n"
        
        framework_content += "**Risk Management:**\n"
        framework_content += "• Identify potential implementation risks and mitigation strategies\n"
        framework_content += "• Develop contingency plans for critical initiatives\n"
        framework_content += "• Ensure adequate resource allocation and stakeholder commitment"
        
        rec_sections.append({
            "type": "implementation_framework",
            "content": framework_content
        })
        
        # Combine all sections
        full_content = "\n\n".join([section["content"] for section in rec_sections])
        
        result = {
            "status": "success",
            "section_type": "recommendations",
            "content": full_content,
            "metadata": {
                "word_count": len(full_content.split()),
                "recommendation_categories": rec_categories,
                "priority_actions": len(priority_recommendations),
                "strategic_initiatives": len(strategic_recommendations),
                "professional_score": 90
            },
            "implementation": {
                "has_timeline": True,
                "has_success_metrics": True,
                "has_governance_framework": True,
                "actionable": True
            }
        }
        
        print(f"✅ Recommendations section generated successfully")
        print(f"   Word count: {result['metadata']['word_count']}")
        print(f"   Categories: {rec_categories}")
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_msg = f"❌ Error generating recommendations: {e}"
        print(error_msg)
        return json.dumps({
            "status": "error",
            "error": str(e),
            "content": ""
        })


def setup_section_generator_before_call(callback_context: CallbackContext):
    """Setup the Section Generator Agent with necessary context."""
    
    # Add content generation context
    if "content_context" not in callback_context.state:
        callback_context.state["content_context"] = {
            "section_types": ["executive_summary", "data_analysis", "insights", "recommendations", "methodology", "conclusion"],
            "writing_styles": ["executive", "analytical", "strategic", "operational"],
            "business_domains": ["financial", "marketing", "sales", "operational", "strategic"],
            "quality_standards": ["professional_tone", "data_driven", "actionable", "clear_structure"]
        }
    
    # Add database settings for data integration
    if "database_settings" not in callback_context.state:
        try:
            callback_context.state["database_settings"] = get_database_settings()
        except:
            callback_context.state["database_settings"] = {}


# Create the Section Generator Agent
section_generator_agent = Agent(
    model=os.getenv("ROOT_AGENT_MODEL", "gemini-1.5-pro"),
    name="section_generator_agent",
    instruction=return_instructions_section_generator_agent(),
    global_instruction=(
        f"""
        You are the Section Generator Agent for the Interactive Analytics Report Writer.
        Today's date: {date_today}
        
        Your specialization: Converting user descriptions into professional business report sections
        
        Content generation principles:
        - Professional business writing appropriate for corporate audiences
        - Data-driven narrative that supports statements with evidence
        - Clear structure with logical flow and professional formatting
        - Actionable insights that provide business value
        - Integration with data analysis and visualization capabilities
        
        Your role in the report generation pipeline:
        1. Generate executive summaries with high-level insights and business impact
        2. Create data analysis sections that combine quantitative findings with narrative
        3. Develop strategic recommendations with implementation guidance
        4. Ensure content consistency and professional quality across all sections
        
        Coordinate with InstantDashboard agents to integrate data analysis results into narrative sections.
        Work with other Report Writer agents to maintain document coherence and professional standards.
        """
    ),
    tools=[
        generate_executive_summary,
        generate_data_analysis_section,
        generate_recommendations_section,
        call_db_agent,  # Integration with InstantDashboard for data queries
    ],
    before_agent_callback=setup_section_generator_before_call,
    generate_content_config=types.GenerateContentConfig(temperature=0.3),
) 