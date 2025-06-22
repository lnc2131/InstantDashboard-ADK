"""
Report Template Agent for Interactive Analytics Report Writer

This agent specializes in business report structure and template management.
It helps users select, customize, and manage templates that match their specific
business needs and industry requirements.
"""

import os
from datetime import date
import json
from typing import Dict, Any, List, Optional

from google.genai import types
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import ToolContext

# Import prompts and database functionality
from report_writer.prompts import return_instructions_report_template_agent

date_today = date.today()


def get_available_templates(
    category: Optional[str],
    tool_context: ToolContext,
) -> str:
    """Get available report templates, optionally filtered by category.
    
    This tool retrieves business report templates from the database,
    allowing users to see what templates are available for their use case.
    
    Args:
        category (Optional[str]): Template category to filter by (financial, marketing, sales, etc.).
        tool_context (ToolContext): The tool context with database access.
        
    Returns:
        str: JSON list of available templates with their metadata.
    """
    
    try:
        print(f"🔍 Getting available templates for category: {category or 'all'}")
        
        # Mock data for now - in production this would query the database
        available_templates = [
            {
                "id": 1,
                "name": "Financial Quarterly Report",
                "description": "Comprehensive quarterly financial analysis with P&L, cash flow, and forecasting sections",
                "category": "financial",
                "sections": [
                    {"name": "Executive Summary", "type": "executive_summary", "ai_generated": True},
                    {"name": "Revenue Analysis", "type": "data_analysis", "ai_generated": True},
                    {"name": "Cost Breakdown", "type": "data_analysis", "ai_generated": True},
                    {"name": "Financial Forecasting", "type": "insights", "ai_generated": True},
                    {"name": "Recommendations", "type": "recommendations", "ai_generated": True}
                ],
                "usage_count": 45,
                "is_featured": True
            },
            {
                "id": 2,
                "name": "Marketing Campaign Analysis",
                "description": "Marketing performance analysis with ROI, conversion metrics, and customer acquisition data",
                "category": "marketing", 
                "sections": [
                    {"name": "Campaign Overview", "type": "executive_summary", "ai_generated": True},
                    {"name": "Performance Metrics", "type": "data_analysis", "ai_generated": True},
                    {"name": "ROI Analysis", "type": "data_analysis", "ai_generated": True},
                    {"name": "Customer Insights", "type": "insights", "ai_generated": True},
                    {"name": "Optimization Recommendations", "type": "recommendations", "ai_generated": True}
                ],
                "usage_count": 32,
                "is_featured": True
            },
            {
                "id": 3,
                "name": "Sales Performance Dashboard",
                "description": "Sales team and territory analysis with pipeline forecasting and performance benchmarks",
                "category": "sales",
                "sections": [
                    {"name": "Sales Summary", "type": "executive_summary", "ai_generated": True},
                    {"name": "Territory Analysis", "type": "data_analysis", "ai_generated": True},
                    {"name": "Pipeline Forecasting", "type": "data_analysis", "ai_generated": True},
                    {"name": "Performance Insights", "type": "insights", "ai_generated": True},
                    {"name": "Action Items", "type": "recommendations", "ai_generated": True}
                ],
                "usage_count": 28,
                "is_featured": False
            }
        ]
        
        # Filter by category if specified
        if category:
            available_templates = [t for t in available_templates if t["category"] == category.lower()]
        
        # Sort by usage count and featured status
        available_templates.sort(key=lambda x: (x["is_featured"], x["usage_count"]), reverse=True)
        
        result = {
            "status": "success",
            "templates": available_templates,
            "total_count": len(available_templates),
            "filtered_by": category
        }
        
        print(f"✅ Found {len(available_templates)} templates")
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_msg = f"❌ Error getting templates: {e}"
        print(error_msg)
        return json.dumps({
            "status": "error", 
            "error": str(e),
            "templates": []
        })


def setup_report_template_before_call(callback_context: CallbackContext):
    """Setup the Report Template Agent with necessary context."""
    
    # Add template management context
    if "template_context" not in callback_context.state:
        callback_context.state["template_context"] = {
            "available_categories": ["financial", "marketing", "sales", "operational", "strategic"],
            "default_sections": ["executive_summary", "data_analysis", "insights", "recommendations"],
            "user_preferences": {}
        }


# Create the Report Template Agent
report_template_agent = Agent(
    model=os.getenv("ROOT_AGENT_MODEL", "gemini-1.5-pro"),
    name="report_template_agent",
    instruction=return_instructions_report_template_agent(),
    global_instruction=(
        f"""
        You are the Report Template Agent for the Interactive Analytics Report Writer.
        Today's date: {date_today}
        
        Your specialization: Business report structure and template management
        
        Available template categories: Financial, Marketing, Sales, Operational, Strategic
        
        Your role in the report generation pipeline:
        1. Help users select appropriate templates for their business needs
        2. Customize templates based on specific requirements
        3. Validate template structures for AI content generation compatibility
        4. Ensure templates follow professional business report standards
        
        Work collaboratively with other agents to create comprehensive business reports.
        """
    ),
    tools=[
        get_available_templates,
    ],
    before_agent_callback=setup_report_template_before_call,
    generate_content_config=types.GenerateContentConfig(temperature=0.1),
) 