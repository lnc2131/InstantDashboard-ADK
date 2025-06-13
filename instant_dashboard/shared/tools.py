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

"""Tools for InstantDashboard agents.

This module contains agent tools migrated from data_science to make 
instant_dashboard self-contained.
"""

import os
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool
from google.genai import types

from .bigquery import (
    get_database_settings,
    initial_bq_nl2sql,
    run_bigquery_validation,
)

# Environment variable for NL2SQL method
NL2SQL_METHOD = os.getenv("NL2SQL_METHOD", "BASELINE")


def setup_database_agent_before_call(callback_context: CallbackContext) -> None:
    """Setup the database agent before each call."""
    if "database_settings" not in callback_context.state:
        callback_context.state["database_settings"] = get_database_settings()


# Create the database agent (migrated from data_science)
database_agent = Agent(
    model=os.getenv("BIGQUERY_AGENT_MODEL", "gemini-1.5-pro"),
    name="database_agent",
    instruction="""You are a BigQuery database agent specialized in converting natural language questions to SQL queries and executing them safely.

Your primary capabilities:
- Convert natural language questions to BigQuery SQL using initial_bq_nl2sql
- Validate and execute SQL queries using run_bigquery_validation
- Return structured results in a clear format

Process:
1. Use initial_bq_nl2sql to convert the user's question to SQL
2. Use run_bigquery_validation to execute the SQL and get results
3. Return the results in a clear, structured format

Always prioritize data accuracy and query safety.""",
    tools=[
        initial_bq_nl2sql,
        run_bigquery_validation,
    ],
    before_agent_callback=setup_database_agent_before_call,
    generate_content_config=types.GenerateContentConfig(temperature=0.01),
)


async def call_db_agent(
    question: str,
    tool_context: ToolContext,
):
    """Tool to call database (nl2sql) agent.
    
    This is migrated from data_science/tools.py to make instant_dashboard self-contained.
    
    Args:
        question (str): Natural language question to convert to SQL and execute.
        tool_context (ToolContext): The tool context with database settings.
        
    Returns:
        str: The result from the database agent.
    """
    print(
        "\n call_db_agent.use_database:"
        f' {tool_context.state["all_db_settings"]["use_database"]}'
    )

    agent_tool = AgentTool(agent=database_agent)

    db_agent_output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )
    tool_context.state["db_agent_output"] = db_agent_output
    return db_agent_output 