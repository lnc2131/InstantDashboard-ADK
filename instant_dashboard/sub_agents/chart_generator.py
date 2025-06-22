"""
ChartGeneratorAgent - Phase 3 of InstantDashboard

This agent analyzes data and generates intelligent chart specifications.
It determines the best visualization types based on data structure and user intent.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.genai import types

from instant_dashboard.shared.utils import get_env_var

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_chart_specifications(callback_context: CallbackContext) -> str:
    """
    Tool that analyzes data and generates chart specifications.
    
    Args:
        data (list): The raw data to visualize
        user_query (str): The original user question for context
        
    Returns:
        str: JSON string containing chart specifications and recommendations
    """
    
    # Get the inputs from the callback context
    data = callback_context.input.get("data", [])
    user_query = callback_context.input.get("user_query", "")
    
    logger.info(f"🎨 ChartGenerator: Analyzing data for visualization...")
    logger.info(f"   Data Preview: {data[:2] if data else 'No data'}")
    logger.info(f"   User Query: {user_query}")
    
    try:
        if not data or len(data) == 0:
            return json.dumps({
                "success": False,
                "error": "No data provided for visualization",
                "recommendations": []
            })
        
        # Analyze data structure
        first_row = data[0]
        if not isinstance(first_row, dict):
            return json.dumps({
                "success": False,
                "error": "Data format not supported for visualization",
                "recommendations": []
            })
        
        keys = list(first_row.keys())
        num_columns = len(keys)
        
        # Analyze data types
        data_types = {}
        numeric_columns = []
        categorical_columns = []
        
        for key in keys:
            # Check if column contains numeric data
            numeric_values = 0
            total_values = 0
            
            for row in data:
                if key in row and row[key] is not None:
                    total_values += 1
                    try:
                        float(row[key])
                        numeric_values += 1
                    except (ValueError, TypeError):
                        pass
            
            if total_values > 0 and numeric_values / total_values > 0.8:  # 80% numeric
                data_types[key] = "numeric"
                numeric_columns.append(key)
            else:
                data_types[key] = "categorical"
                categorical_columns.append(key)
        
        # Generate chart recommendations based on data structure
        recommendations = []
        
        # Single column (list of categories)
        if num_columns == 1:
            recommendations.append({
                "type": "list",
                "priority": 1,
                "reason": "Single column data best displayed as organized list",
                "config": {
                    "display_type": "grid",
                    "title": f"{keys[0].title()} Results",
                    "count": len(data)
                }
            })
        
        # Two columns with one categorical and one numeric
        elif num_columns == 2 and len(categorical_columns) == 1 and len(numeric_columns) == 1:
            cat_col = categorical_columns[0]
            num_col = numeric_columns[0]
            
            recommendations.extend([
                {
                    "type": "bar",
                    "priority": 1,
                    "reason": "Perfect for comparing values across categories",
                    "config": {
                        "x_axis": cat_col,
                        "y_axis": num_col,
                        "title": f"{num_col.title()} by {cat_col.title()}",
                        "color": "#3b82f6"
                    }
                },
                {
                    "type": "pie",
                    "priority": 2,
                    "reason": "Shows proportional relationships and market share",
                    "config": {
                        "label_field": cat_col,
                        "value_field": num_col,
                        "title": f"{num_col.title()} Distribution",
                        "show_percentages": True
                    }
                }
            ])
        
        # Multiple columns - table view
        else:
            recommendations.append({
                "type": "table",
                "priority": 1,
                "reason": "Complex data best displayed in tabular format",
                "config": {
                    "columns": keys,
                    "sortable": True,
                    "title": "Data Results"
                }
            })
        
        # Add trend analysis if data suggests time series
        if any("date" in key.lower() or "time" in key.lower() or "month" in key.lower() 
               for key in keys):
            recommendations.append({
                "type": "line",
                "priority": 1,
                "reason": "Time-based data perfect for trend analysis",
                "config": {
                    "x_axis": next((k for k in keys if any(t in k.lower() 
                                                        for t in ["date", "time", "month"])), keys[0]),
                    "y_axis": numeric_columns[0] if numeric_columns else keys[-1],
                    "title": "Trend Analysis Over Time"
                }
            })
        
        # Generate insights based on user query intent
        query_insights = []
        query_lower = user_query.lower()
        
        if "top" in query_lower or "best" in query_lower or "highest" in query_lower:
            query_insights.append("Data shows ranking/comparison - bar charts recommended")
        
        if "trend" in query_lower or "over time" in query_lower:
            query_insights.append("Time-series analysis detected - line charts recommended")
        
        if "share" in query_lower or "percentage" in query_lower or "proportion" in query_lower:
            query_insights.append("Proportional analysis requested - pie charts recommended")
        
        result = {
            "success": True,
            "data_analysis": {
                "row_count": len(data),
                "column_count": num_columns,
                "columns": keys,
                "data_types": data_types,
                "numeric_columns": numeric_columns,
                "categorical_columns": categorical_columns
            },
            "chart_recommendations": recommendations,
            "query_insights": query_insights,
            "suggested_charts": len(recommendations)
        }
        
        logger.info(f"✅ ChartGenerator: Generated {len(recommendations)} chart recommendations")
        return json.dumps(result)
        
    except Exception as e:
        logger.error(f"❌ ChartGenerator error: {e}")
        return json.dumps({
            "success": False,
            "error": f"Chart generation failed: {str(e)}",
            "recommendations": []
        })

def setup_before_agent_call(callback_context: CallbackContext):
    """Setup function called before the agent processes the request."""
    logger.info("🎨 ChartGeneratorAgent: Setting up for chart analysis...")

# Create the ChartGeneratorAgent
chart_generator_agent = Agent(
    model=os.getenv("ROOT_AGENT_MODEL", "gemini-1.5-flash"),
    name="chart_generator_agent", 
    instruction="""You are a data visualization expert specializing in creating intelligent chart recommendations.

Your role is to:
1. Analyze data structure and types
2. Understand user intent from their questions  
3. Recommend the most effective visualization types
4. Generate chart specifications for frontend rendering

Key principles:
- Choose chart types based on data characteristics
- Consider user intent and question context
- Provide multiple visualization options when appropriate
- Explain why each chart type would be effective
- Generate actionable chart configurations

Available chart types:
- Bar charts: For comparing categories
- Pie charts: For showing proportions
- Line charts: For trends over time
- Tables: For detailed data view
- Lists: For simple categorical data

Always consider:
- Data structure (categorical vs numeric)
- Number of data points
- User's analytical intent
- Best practices for data visualization""",
    tools=[generate_chart_specifications],
    before_agent_callback=setup_before_agent_call
) 