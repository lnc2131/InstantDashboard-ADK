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
from datetime import date

from google.genai import types
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext

# Import existing database functionality for testing integration
from data_science.sub_agents.bigquery.tools import (
    get_database_settings as get_bq_database_settings,
)
from data_science.tools import call_db_agent

# Import prompt system
from .prompts import return_instructions_coordinator
from google.adk.tools import ToolContext

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


def execute_full_pipeline(
    question: str,
    tool_context: ToolContext,
) -> str:
    """Execute the full Phase 2 → Phase 3 pipeline.
    
    This convenience tool runs the complete process:
    Natural Language → Query Plan → SQL Execution → Results
    
    Args:
        question (str): Natural language question about the data.
        tool_context (ToolContext): The tool context with database settings.
        
    Returns:
        str: Final execution results with complete pipeline metadata.
    """
    
    try:
        print("🚀 Starting full InstantDashboard pipeline...")
        print(f"   Question: {question}")
        
        # Phase 2: Generate query plan
        print("\n📋 Phase 2: Generating query plan...")
        query_plan = call_query_planner_agent(question, tool_context)
        
        # Phase 3: Execute query plan  
        print("\n⚡ Phase 3: Executing query plan...")
        execution_result = call_bigquery_runner_agent(query_plan, tool_context)
        
        print("\n✅ Full pipeline complete!")
        
        # Return the execution result (which includes query plan metadata)
        return execution_result
        
    except Exception as e:
        error_msg = f"❌ Error in full pipeline: {e}"
        print(error_msg)
        return f"Error: Pipeline failed - {e}"


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
        
        Phase 3: BigQueryRunner Integration Complete
        ✅ Foundation complete - database integration working  
        ✅ QueryPlannerAgent - structured query planning
        🚀 NEW: BigQueryRunnerAgent - query plan execution
        
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
        execute_full_pipeline,  # Phase 2 + 3: Complete pipeline
    ],
    before_agent_callback=setup_before_agent_call,
    generate_content_config=types.GenerateContentConfig(temperature=0.01),
)

# Alias for backward compatibility with existing tests
dashboard_agent = root_agent