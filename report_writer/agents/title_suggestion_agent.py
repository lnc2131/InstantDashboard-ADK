"""
Title Suggestion Agent for Interactive Analytics Report Writer

This agent specializes in generating compelling, contextual titles for business 
reports and sections based on available data sources and business context.
"""

import os
from datetime import date
import json
from typing import Dict, Any, List, Optional

from google.genai import types
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import ToolContext

# Import prompts and existing InstantDashboard functionality
from report_writer.prompts import return_instructions_title_suggestion_agent
from instant_dashboard.shared import get_database_settings

date_today = date.today()


def suggest_report_titles(
    business_context: str,
    data_summary: str,
    tool_context: ToolContext,
) -> str:
    """Generate title suggestions for business reports based on context and data.
    
    This tool analyzes the business context and available data to suggest
    compelling, professional titles that reflect key findings and business value.
    
    Args:
        business_context (str): Description of the business context, goals, and audience.
        data_summary (str): Summary of available data sources and key metrics.
        tool_context (ToolContext): The tool context with database access.
        
    Returns:
        str: JSON list of suggested titles with rationale and effectiveness ratings.
    """
    
    try:
        print(f"💡 Generating report title suggestions...")
        print(f"   Business context: {business_context[:100]}...")
        print(f"   Data summary: {data_summary[:100]}...")
        
        # Parse inputs to understand context
        context_keywords = business_context.lower()
        data_keywords = data_summary.lower()
        
        # Determine report type and focus
        report_type = "General Business"
        if any(word in context_keywords for word in ["financial", "revenue", "profit", "budget", "quarterly"]):
            report_type = "Financial"
        elif any(word in context_keywords for word in ["marketing", "campaign", "roi", "conversion", "customer acquisition"]):
            report_type = "Marketing"
        elif any(word in context_keywords for word in ["sales", "territory", "pipeline", "quota", "performance"]):
            report_type = "Sales"
        elif any(word in context_keywords for word in ["operational", "efficiency", "process", "productivity", "resources"]):
            report_type = "Operational"
        
        # Extract key metrics/numbers if mentioned
        key_metrics = []
        if "growth" in data_keywords:
            key_metrics.append("growth")
        if "increase" in data_keywords or "up" in data_keywords:
            key_metrics.append("increase")
        if "decrease" in data_keywords or "down" in data_keywords:
            key_metrics.append("decrease")
        if "%" in data_summary or "percent" in data_keywords:
            key_metrics.append("percentage_change")
        
        # Generate title suggestions based on type and context
        title_suggestions = []
        
        if report_type == "Financial":
            title_suggestions = [
                {
                    "title": f"Q{(date_today.month-1)//3 + 1} {date_today.year} Financial Performance: Key Metrics and Strategic Insights",
                    "style": "executive",
                    "effectiveness": 85,
                    "rationale": "Professional, time-specific, implies both data and strategic value"
                },
                {
                    "title": "Financial Analysis Report: Revenue Trends and Growth Opportunities",
                    "style": "analytical", 
                    "effectiveness": 78,
                    "rationale": "Clear focus on analysis with forward-looking component"
                },
                {
                    "title": "Financial Dashboard: Performance Metrics and Business Impact",
                    "style": "dashboard",
                    "effectiveness": 72,
                    "rationale": "Dashboard format suggests visual data presentation"
                }
            ]
            
            # Customize based on metrics
            if "growth" in key_metrics:
                title_suggestions.insert(0, {
                    "title": "Financial Growth Analysis: Driving Performance and Strategic Value",
                    "style": "growth_focused",
                    "effectiveness": 88,
                    "rationale": "Emphasizes positive growth story, appeals to executives"
                })
        
        elif report_type == "Marketing":
            title_suggestions = [
                {
                    "title": "Marketing Performance Analysis: Campaign ROI and Customer Insights",
                    "style": "performance",
                    "effectiveness": 82,
                    "rationale": "Combines performance metrics with customer insights"
                },
                {
                    "title": "Digital Marketing Report: Conversion Trends and Optimization Opportunities",
                    "style": "digital_focused",
                    "effectiveness": 79,
                    "rationale": "Specific to digital channels with actionable focus"
                },
                {
                    "title": "Marketing Analytics Dashboard: Key Metrics and Strategic Recommendations",
                    "style": "analytical",
                    "effectiveness": 76,
                    "rationale": "Balances data analysis with strategic guidance"
                }
            ]
        
        elif report_type == "Sales":
            title_suggestions = [
                {
                    "title": "Sales Performance Report: Territory Analysis and Pipeline Insights",
                    "style": "performance",
                    "effectiveness": 84,
                    "rationale": "Covers key sales metrics and forward-looking pipeline"
                },
                {
                    "title": "Sales Analytics: Team Performance and Revenue Optimization",
                    "style": "analytical",
                    "effectiveness": 80,
                    "rationale": "Focus on team metrics with optimization angle"
                },
                {
                    "title": "Sales Dashboard: Quota Tracking and Market Opportunities",
                    "style": "dashboard",
                    "effectiveness": 77,
                    "rationale": "Operational focus with strategic market component"
                }
            ]
        
        else:  # General/Operational
            title_suggestions = [
                {
                    "title": "Business Intelligence Report: Key Performance Indicators and Insights",
                    "style": "general",
                    "effectiveness": 75,
                    "rationale": "Professional, covers both metrics and insights"
                },
                {
                    "title": "Operational Analysis: Efficiency Metrics and Process Optimization",
                    "style": "operational",
                    "effectiveness": 78,
                    "rationale": "Focus on operational efficiency and improvement"
                },
                {
                    "title": "Performance Dashboard: Business Metrics and Strategic Analysis",
                    "style": "dashboard",
                    "effectiveness": 73,
                    "rationale": "Broad performance focus with strategic element"
                }
            ]
        
        # Add data-driven variations if specific metrics are available
        if "percentage_change" in key_metrics:
            data_driven_title = {
                "title": f"{report_type} Performance Report: Data-Driven Insights and Trend Analysis",
                "style": "data_driven",
                "effectiveness": 86,
                "rationale": "Emphasizes data-driven approach, suggests quantified insights"
            }
            title_suggestions.insert(0, data_driven_title)
        
        # Sort by effectiveness
        title_suggestions.sort(key=lambda x: x["effectiveness"], reverse=True)
        
        result = {
            "status": "success",
            "report_type": report_type,
            "title_suggestions": title_suggestions[:5],  # Top 5 suggestions
            "context_analysis": {
                "detected_focus": report_type,
                "key_themes": key_metrics,
                "recommendation": "Choose titles that match your audience - executive style for C-level, analytical for detailed teams"
            }
        }
        
        print(f"✅ Generated {len(title_suggestions)} title suggestions")
        print(f"   Report type: {report_type}")
        print(f"   Top suggestion: {title_suggestions[0]['title']}")
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_msg = f"❌ Error generating titles: {e}"
        print(error_msg)
        return json.dumps({
            "status": "error",
            "error": str(e),
            "title_suggestions": []
        })


def suggest_section_titles(
    section_type: str,
    section_content_summary: str,
    data_insights: str,
    tool_context: ToolContext,
) -> str:
    """Generate title suggestions for specific report sections.
    
    This tool creates contextual titles for individual report sections based on
    the section type, content summary, and key data insights.
    
    Args:
        section_type (str): Type of section (executive_summary, data_analysis, insights, etc.).
        section_content_summary (str): Summary of what the section will contain.
        data_insights (str): Key data insights or findings for this section.
        tool_context (ToolContext): The tool context.
        
    Returns:
        str: JSON list of section title suggestions with effectiveness ratings.
    """
    
    try:
        print(f"📝 Generating section title suggestions...")
        print(f"   Section type: {section_type}")
        print(f"   Content: {section_content_summary[:80]}...")
        
        # Generate section-specific titles
        section_titles = []
        
        if section_type == "executive_summary":
            section_titles = [
                {
                    "title": "Executive Summary: Key Findings and Business Impact",
                    "effectiveness": 85,
                    "rationale": "Clear, professional, indicates high-level content"
                },
                {
                    "title": "Executive Overview: Performance Highlights and Strategic Insights",
                    "effectiveness": 82,
                    "rationale": "Emphasizes both performance and strategy"
                },
                {
                    "title": "Key Performance Summary: Critical Metrics and Recommendations",
                    "effectiveness": 79,
                    "rationale": "Focus on metrics with actionable component"
                }
            ]
        
        elif section_type == "data_analysis":
            # Extract specific metrics or trends if mentioned
            if "trend" in section_content_summary.lower():
                section_titles.append({
                    "title": "Trend Analysis: Performance Patterns and Key Insights",
                    "effectiveness": 88,
                    "rationale": "Specific to trends, indicates deep analysis"
                })
            
            if "comparison" in section_content_summary.lower():
                section_titles.append({
                    "title": "Comparative Analysis: Performance Benchmarks and Insights",
                    "effectiveness": 86,
                    "rationale": "Indicates benchmarking and comparison focus"
                })
            
            # Standard data analysis titles
            section_titles.extend([
                {
                    "title": "Data Analysis: Quantitative Insights and Key Metrics",
                    "effectiveness": 80,
                    "rationale": "Professional, indicates quantified analysis"
                },
                {
                    "title": "Performance Metrics: Data-Driven Analysis and Findings",
                    "effectiveness": 78,
                    "rationale": "Emphasizes data-driven approach"
                },
                {
                    "title": "Analytical Deep Dive: Key Data Points and Trends",
                    "effectiveness": 75,
                    "rationale": "Suggests thorough, detailed analysis"
                }
            ])
        
        elif section_type == "insights":
            section_titles = [
                {
                    "title": "Business Insights: What the Data Tells Us",
                    "effectiveness": 84,
                    "rationale": "Clear value proposition, business-focused"
                },
                {
                    "title": "Key Insights: Implications and Business Impact",
                    "effectiveness": 81,
                    "rationale": "Focus on implications and business value"
                },
                {
                    "title": "Data Interpretation: Patterns, Trends, and Opportunities",
                    "effectiveness": 78,
                    "rationale": "Comprehensive interpretation with forward focus"
                }
            ]
        
        elif section_type == "recommendations":
            section_titles = [
                {
                    "title": "Strategic Recommendations: Actionable Next Steps",
                    "effectiveness": 87,
                    "rationale": "Clear action focus, strategic positioning"
                },
                {
                    "title": "Action Plan: Priority Initiatives and Implementation",
                    "effectiveness": 84,
                    "rationale": "Practical focus with implementation guidance"
                },
                {
                    "title": "Recommendations: Optimizing Performance and Growth",
                    "effectiveness": 81,
                    "rationale": "Performance and growth focused outcomes"
                }
            ]
        
        elif section_type == "chart":
            section_titles = [
                {
                    "title": "Data Visualizations: Key Performance Indicators",
                    "effectiveness": 80,
                    "rationale": "Clear visualization focus with KPI emphasis"
                },
                {
                    "title": "Charts and Analysis: Visual Data Insights",
                    "effectiveness": 77,
                    "rationale": "Combines visual and analytical elements"
                },
                {
                    "title": "Performance Dashboard: Visual Metrics Overview",
                    "effectiveness": 75,
                    "rationale": "Dashboard feel with performance focus"
                }
            ]
        
        else:  # Generic section
            section_titles = [
                {
                    "title": f"{section_type.replace('_', ' ').title()}: Analysis and Insights",
                    "effectiveness": 70,
                    "rationale": "Generic professional format"
                }
            ]
        
        # Enhance titles with specific data insights if provided
        if data_insights and len(data_insights) > 10:
            insights_lower = data_insights.lower()
            
            # Look for quantified insights
            if any(char.isdigit() for char in data_insights):
                # Try to extract and incorporate numbers
                enhanced_title = {
                    "title": f"{section_type.replace('_', ' ').title()}: Performance Metrics and Quantified Results",
                    "effectiveness": 85,
                    "rationale": "Incorporates quantified results, higher business value"
                }
                section_titles.insert(0, enhanced_title)
        
        # Sort by effectiveness and limit results
        section_titles = sorted(section_titles, key=lambda x: x["effectiveness"], reverse=True)[:4]
        
        result = {
            "status": "success",
            "section_type": section_type,
            "title_suggestions": section_titles,
            "context_used": {
                "content_summary": section_content_summary[:100],
                "has_data_insights": bool(data_insights and len(data_insights) > 10)
            }
        }
        
        print(f"✅ Generated {len(section_titles)} section titles")
        print(f"   Top suggestion: {section_titles[0]['title']}")
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_msg = f"❌ Error generating section titles: {e}"
        print(error_msg)
        return json.dumps({
            "status": "error",
            "error": str(e),
            "title_suggestions": []
        })


def analyze_data_for_titles(
    data_query_description: str,
    tool_context: ToolContext,
) -> str:
    """Analyze available data sources to understand context for title generation.
    
    This tool examines data sources and schema to provide context for generating
    data-driven titles that accurately reflect what insights will be available.
    
    Args:
        data_query_description (str): Description of the data analysis being performed.
        tool_context (ToolContext): The tool context with database access.
        
    Returns:
        str: JSON with data context analysis for title generation.
    """
    
    try:
        print(f"🔍 Analyzing data context for title generation...")
        print(f"   Query description: {data_query_description[:100]}...")
        
        # Get database schema information
        try:
            db_settings = get_database_settings()
            schema_info = db_settings.get("bq_ddl_schema", "")
        except:
            schema_info = ""
        
        # Analyze query description for key elements
        query_lower = data_query_description.lower()
        
        # Identify data themes
        data_themes = []
        if any(word in query_lower for word in ["sales", "revenue", "orders"]):
            data_themes.append("sales_performance")
        if any(word in query_lower for word in ["customer", "users", "accounts"]):
            data_themes.append("customer_analysis")
        if any(word in query_lower for word in ["time", "trend", "over", "monthly", "quarterly"]):
            data_themes.append("temporal_analysis")
        if any(word in query_lower for word in ["region", "country", "location", "territory"]):
            data_themes.append("geographic_analysis")
        if any(word in query_lower for word in ["product", "category", "item"]):
            data_themes.append("product_analysis")
        
        # Identify analytical approaches
        analysis_types = []
        if any(word in query_lower for word in ["top", "best", "highest", "ranking"]):
            analysis_types.append("ranking_analysis")
        if any(word in query_lower for word in ["compare", "comparison", "vs", "versus"]):
            analysis_types.append("comparative_analysis")
        if any(word in query_lower for word in ["growth", "increase", "decrease", "change"]):
            analysis_types.append("growth_analysis")
        if any(word in query_lower for word in ["forecast", "predict", "future", "projection"]):
            analysis_types.append("predictive_analysis")
        
        # Generate title context suggestions
        title_context = {
            "data_themes": data_themes,
            "analysis_types": analysis_types,
            "has_schema_access": bool(schema_info),
            "suggested_title_elements": []
        }
        
        # Generate specific title elements based on analysis
        if "sales_performance" in data_themes:
            title_context["suggested_title_elements"].append({
                "element": "Revenue Performance",
                "usage": "Strong business focus, executive appeal"
            })
        
        if "temporal_analysis" in data_themes:
            title_context["suggested_title_elements"].append({
                "element": "Trend Analysis",
                "usage": "Indicates time-series insights"
            })
        
        if "ranking_analysis" in analysis_types:
            title_context["suggested_title_elements"].append({
                "element": "Top Performers",
                "usage": "Highlights best-performing entities"
            })
        
        if "comparative_analysis" in analysis_types:
            title_context["suggested_title_elements"].append({
                "element": "Benchmark Analysis",
                "usage": "Professional comparison focus"
            })
        
        # Provide title templates based on detected patterns
        title_templates = []
        
        if data_themes and analysis_types:
            if "sales_performance" in data_themes and "ranking_analysis" in analysis_types:
                title_templates.append("Sales Performance: Top Revenue Drivers and Growth Opportunities")
            if "customer_analysis" in data_themes and "temporal_analysis" in data_themes:
                title_templates.append("Customer Analytics: Engagement Trends and Behavioral Insights")
            if "geographic_analysis" in data_themes:
                title_templates.append("Regional Performance: Market Analysis and Territory Insights")
        
        title_context["template_suggestions"] = title_templates
        
        result = {
            "status": "success",
            "data_context": title_context,
            "recommendations": {
                "focus_area": data_themes[0] if data_themes else "general_analysis",
                "analytical_approach": analysis_types[0] if analysis_types else "descriptive_analysis",
                "title_style": "data_driven" if analysis_types else "descriptive"
            }
        }
        
        print(f"✅ Data context analysis complete")
        print(f"   Data themes: {data_themes}")
        print(f"   Analysis types: {analysis_types}")
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_msg = f"❌ Error analyzing data context: {e}"
        print(error_msg)
        return json.dumps({
            "status": "error",
            "error": str(e),
            "data_context": {}
        })


def setup_title_suggestion_before_call(callback_context: CallbackContext):
    """Setup the Title Suggestion Agent with necessary context."""
    
    # Add title generation context
    if "title_context" not in callback_context.state:
        callback_context.state["title_context"] = {
            "business_domains": ["financial", "marketing", "sales", "operational", "strategic"],
            "title_styles": ["executive", "analytical", "dashboard", "performance", "data_driven"],
            "effectiveness_factors": ["specificity", "business_value", "clarity", "professional_tone"]
        }
    
    # Add database settings for data-driven titles
    if "database_settings" not in callback_context.state:
        try:
            callback_context.state["database_settings"] = get_database_settings()
        except:
            callback_context.state["database_settings"] = {}


# Create the Title Suggestion Agent
title_suggestion_agent = Agent(
    model=os.getenv("ROOT_AGENT_MODEL", "gemini-1.5-pro"),
    name="title_suggestion_agent",
    instruction=return_instructions_title_suggestion_agent(),
    global_instruction=(
        f"""
        You are the Title Suggestion Agent for the Interactive Analytics Report Writer.
        Today's date: {date_today}
        
        Your specialization: Generating compelling, contextual titles for business reports and sections
        
        Title generation principles:
        - Data-driven: Incorporate key metrics and findings when available
        - Business-focused: Appeal to professional audiences and executives
        - Specific: Use quantified language when possible
        - Professional: Match corporate communication standards
        - Hierarchical: Create clear information architecture
        
        Your role in the report generation pipeline:
        1. Generate report-level titles that reflect key findings and business value
        2. Create section titles that guide readers through the narrative
        3. Analyze data context to suggest quantified, specific titles
        4. Provide multiple options with effectiveness ratings and rationale
        
        Work with data analysis results to create titles that accurately reflect insights.
        """
    ),
    tools=[
        suggest_report_titles,
        suggest_section_titles,
        analyze_data_for_titles,
    ],
    before_agent_callback=setup_title_suggestion_before_call,
    generate_content_config=types.GenerateContentConfig(temperature=0.2),
) 