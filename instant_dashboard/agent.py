# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""InstantDashboard coordinator agent.

This is the main coordinator for the InstantDashboard multi-agent system.
It orchestrates the pipeline: Natural Language → SQL → Results → Charts → Insights
"""

import os
from datetime import date, datetime
import time
import json

from google.genai import types
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext

# Import existing database functionality (now from our shared module)
from .shared import (
    get_database_settings as get_bq_database_settings,
    call_db_agent,
)

# Import prompt system
from .prompts import return_instructions_coordinator
from google.adk.tools import ToolContext

from instant_dashboard.sub_agents.query_planner import query_planner_agent
from instant_dashboard.sub_agents.bigquery_runner import bigquery_runner_agent
# Temporarily commented out for Railway deployment debugging
# from instant_dashboard.sub_agents.chart_generator import chart_generator_agent

date_today = date.today()


def call_query_planner_agent(
    question: str,
    tool_context: ToolContext,
) -> str:
    """Call the QueryPlannerAgent to create a structured query plan.
    
    This tool integrates the QueryPlannerAgent into the coordinator workflow.
    It takes a natural language question and returns a structured query plan.
    
    Args:
        question (str): Natural language question about the data.
        tool_context (ToolContext): The tool context with database settings.
        
    Returns:
        str: A structured query plan in JSON format.
    """
    
    try:
        # Set up context for the query planner
        if "database_settings" not in tool_context.state:
            tool_context.state["database_settings"] = get_bq_database_settings()
        
        # Call the query planner tool directly (import locally to avoid circular imports)
        from .sub_agents.query_planner import generate_query_plan
        result = generate_query_plan(question, tool_context)
        
        print("✅ QueryPlannerAgent tool called successfully")
        
        # Store result in context for future phases
        tool_context.state["query_plan_result"] = result
        
        return result
        
    except Exception as e:
        error_msg = f"❌ Error calling QueryPlannerAgent: {e}"
        print(error_msg)
        return f"Error: Could not generate query plan - {e}"


def call_bigquery_runner_agent(
    query_plan: str,
    tool_context: ToolContext,
) -> str:
    """Call the BigQueryRunner to execute a structured query plan.
    
    This tool integrates the BigQueryRunnerAgent into the coordinator workflow.
    It takes a query plan from Phase 2 and executes it to return data results.
    
    Args:
        query_plan (str): JSON query plan from QueryPlannerAgent.
        tool_context (ToolContext): The tool context with database settings.
        
    Returns:
        str: Execution results in JSON format with data and metadata.
    """
    
    try:
        # Set up context for the BigQuery runner
        if "database_settings" not in tool_context.state:
            tool_context.state["database_settings"] = get_bq_database_settings()
        
        # Call the BigQuery runner tool directly (import locally to avoid circular imports)
        from instant_dashboard.sub_agents.bigquery_runner import execute_query_plan
        result = execute_query_plan(query_plan, tool_context)
        
        print("✅ BigQueryRunnerAgent tool called successfully")
        
        # Store result in context for future phases
        tool_context.state["execution_result"] = result
        
        return result
        
    except Exception as e:
        error_msg = f"❌ Error calling BigQueryRunnerAgent: {e}"
        print(error_msg)
        return f"Error: Could not execute query plan - {e}"


def execute_full_pipeline(question: str) -> dict:
    """
    Execute the complete InstantDashboard pipeline with all agents.
    
    Now includes:
    - Phase 1: Main coordinator 
    - Phase 2: QueryPlannerAgent
    - Phase 3: BigQueryRunnerAgent  
    - Phase 4: ChartGeneratorAgent (NEW!)
    """
    print(f"🚀 EXECUTE_FULL_PIPELINE: Starting 4-phase pipeline...")
    print(f"   Question: {question}")
    print(f"   🔍 DEBUG: This is the NEW 4-phase version with ChartGenerator!")
    
    # UNMISTAKABLE DEBUG MARKER FOR API TESTING
    print("🚨🚨🚨 EXECUTE_FULL_PIPELINE WAS CALLED! 🚨🚨🚨")
    
    start_time = time.time()
    
    try:
        # Phase 1: Main Dashboard Agent (coordinator)
        print(f"📋 Phase 1: Coordinating analysis...")
        
        # Create a simple tool context for the agents
        class SimpleToolContext:
            def __init__(self):
                self.state = {}
                self.state["database_settings"] = get_bq_database_settings()
        
        tool_context = SimpleToolContext()
        
        # Phase 2: Query Planning
        print(f"📋 Phase 2: Generating query plan...")
        from .sub_agents.query_planner import generate_query_plan
        query_plan_result = generate_query_plan(question, tool_context)
        print(f"✅ Generated structured query plan")
        print(f"✅ QueryPlannerAgent tool called successfully")
        
        # Phase 3: Query Execution  
        print(f"⚡ Phase 3: Executing query plan...")
        from .sub_agents.bigquery_runner import execute_query_plan
        execution_result = execute_query_plan(query_plan_result, tool_context)
        print(f"✅ Query plan execution complete - Status: success")
        print(f"✅ BigQueryRunnerAgent tool called successfully")
        
        # Parse execution result to get the data
        try:
            execution_data = json.loads(execution_result)
            query_data = execution_data.get("data", []) if execution_data.get("status") == "success" else []
        except (json.JSONDecodeError, KeyError):
            query_data = []
        
        # Phase 4: Chart Generation (NEW!)
        print(f"🎨 Phase 4: Generating chart specifications...")
        if query_data:
            # Call chart generator tool directly
            from .sub_agents.chart_generator import generate_chart_specifications
            
            # Create callback context for the tool
            class ChartCallbackContext:
                def __init__(self, data, user_query):
                    self.input = {"data": data, "user_query": user_query}
            
            chart_context = ChartCallbackContext(query_data, question)
            chart_result_str = generate_chart_specifications(chart_context)
            print(f"✅ Chart specifications generated")
            print(f"✅ ChartGeneratorAgent tool called successfully")
        else:
            chart_result_str = json.dumps({
                "success": False, 
                "error": "No data available for chart generation",
                "recommendations": []
            })
            print(f"⚠️ No data for chart generation")
        
        # Combine all results
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Parse chart result
        try:
            chart_data = json.loads(chart_result_str)
        except (json.JSONDecodeError, KeyError):
            chart_data = {"success": False, "error": "Chart generation parsing failed"}
        
        # Build comprehensive response
        pipeline_result = {
            "success": True,
            "data": execution_data if 'execution_data' in locals() else {},
            "chart_specifications": chart_data,
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat(),
            "pipeline_phases": {
                "query_planning": {"status": "success", "agent": "QueryPlannerAgent"},
                "query_execution": {"status": "success", "agent": "BigQueryRunnerAgent"}, 
                "chart_generation": {"status": "success" if chart_data.get("success") else "error", "agent": "ChartGeneratorAgent"}
            },
            "query_plan_used": True,
            "row_count": len(query_data),
            "error_message": None
        }
        
        print(f"✅ Full pipeline complete!")
        print(f"   Total execution time: {execution_time:.2f}s")
        print(f"   Phases completed: 4/4")
        print(f"   Charts recommended: {len(chart_data.get('chart_recommendations', []))}")
        
        return pipeline_result
        
    except Exception as e:
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"❌ Pipeline error: {e}")
        
        return {
            "success": False,
            "data": {},
            "chart_specifications": {"success": False, "error": "Pipeline failed"},
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat(),
            "error_message": str(e),
            "pipeline_phases": {
                "query_planning": {"status": "unknown"},
                "query_execution": {"status": "unknown"},
                "chart_generation": {"status": "error"}
            }
        }


def setup_before_agent_call(callback_context: CallbackContext):
    """Setup the agent with database settings."""
    
    # Set up database settings in session state (reusing existing infrastructure)
    if "database_settings" not in callback_context.state:
        db_settings = dict()
        db_settings["use_database"] = "BigQuery"
        callback_context.state["all_db_settings"] = db_settings

    # Set up BigQuery schema in instruction (reusing existing schema cache)
    if callback_context.state["all_db_settings"]["use_database"] == "BigQuery":
        callback_context.state["database_settings"] = get_bq_database_settings()
        schema = callback_context.state["database_settings"]["bq_ddl_schema"]

        # Only update agent instruction if invocation context is available (ADK framework)
        if (hasattr(callback_context, '_invocation_context') and 
            callback_context._invocation_context is not None and
            hasattr(callback_context._invocation_context, 'agent')):
            
            callback_context._invocation_context.agent.instruction = (
                return_instructions_coordinator()
                + f"""

    --------- The BigQuery schema of the relevant data with a few sample rows. ---------
    {schema}

    """
            )


# Instructions now managed through prompts.py versioning system


# Enhanced coordinator agent for Phase 2 + 3
root_agent = Agent(
    model=os.getenv("ROOT_AGENT_MODEL", "gemini-1.5-pro"),
    name="instant_dashboard",
    instruction=return_instructions_coordinator(),
    global_instruction=(
        f"""
        You are InstantDashboard, a multi-agent data analytics assistant.
        Today's date: {date_today}
        
        Phase 2 & 3: Complete Pipeline Integration
        ✅ Phase 1: Foundation complete - database integration working  
        ✅ Phase 2: QueryPlannerAgent - structured query planning
        ✅ Phase 3: BigQueryRunnerAgent - query plan execution
        
        Available workflow options:
        1. Direct SQL: Use call_db_agent for immediate SQL generation & execution
        2. Structured Planning: Use call_query_planner_agent for detailed query plans
        3. Query Execution: Use call_bigquery_runner_agent to execute existing query plans
        4. Full Pipeline: Use execute_full_pipeline for complete NL → Plans → Results
        
        Recommended: Use execute_full_pipeline for complex analytical questions to get 
        the best results with complete transparency of the planning and execution process.
        """
    ),
    tools=[
        call_db_agent,  # Phase 1: Direct database access
        call_query_planner_agent,  # Phase 2: Structured query planning
        call_bigquery_runner_agent,  # Phase 3: Query plan execution
        # execute_full_pipeline now called directly, not as a tool
    ],
    before_agent_callback=setup_before_agent_call,
    generate_content_config=types.GenerateContentConfig(temperature=0.01),
)

# Alias for backward compatibility with existing tests
dashboard_agent = root_agent