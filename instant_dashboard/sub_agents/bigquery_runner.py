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

"""BigQueryRunner Agent: Executes SQL queries safely on BigQuery.

This agent is responsible for Phase 3 of the InstantDashboard pipeline:
Query Plan → SQL Generation → SQL Execution → Formatted Results
"""

import os
import json

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import ToolContext
from google.genai import types, Client

# Import existing BigQuery functionality
from data_science.sub_agents.bigquery.tools import (
    get_database_settings,
    run_bigquery_validation,
)
from data_science.utils.utils import get_env_var

# Import prompts (will add this function next)
from ..prompts import return_instructions_bigquery_runner

# Initialize clients (reusing existing pattern)
project = os.getenv("BQ_PROJECT_ID", None)
location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
llm_client = Client(vertexai=True, project=project, location=location)


def execute_query_plan(
    query_plan: str,
    tool_context: ToolContext,
) -> str:
    """Execute a structured query plan by converting it to SQL and running it.

    This is the main function that takes a query plan from Phase 2 and:
    1. Converts the plan to actual SQL
    2. Executes the SQL safely on BigQuery
    3. Returns formatted results

    Args:
        query_plan (str): JSON query plan from QueryPlannerAgent
        tool_context (ToolContext): The tool context with database settings.

    Returns:
        str: Execution results in JSON format with data and metadata.
    """
    
    try:
        print(f"🚀 BigQueryRunner: Executing query plan...")
        print(f"   Plan Preview: {query_plan[:150]}{'...' if len(query_plan) > 150 else ''}")
        
        # Step 1: Parse the JSON query plan
        try:
            plan_data = json.loads(query_plan)
            print("✅ Query plan parsed successfully")
        except json.JSONDecodeError as e:
            error_result = {
                "status": "error",
                "execution_successful": False,
                "data": None,
                "row_count": 0,
                "error_message": f"Invalid JSON query plan: {e}"
            }
            print(f"❌ Failed to parse query plan: {e}")
            return json.dumps(error_result, indent=2)
        
        # Step 2: Extract key information from the plan
        question_analysis = plan_data.get("question_analysis", "")
        required_tables = plan_data.get("required_tables", [])
        data_processing_steps = plan_data.get("data_processing_steps", [])
        output_requirements = plan_data.get("output_requirements", "")
        
        print(f"📊 Plan Analysis:")
        print(f"   - Question: {question_analysis[:100]}{'...' if len(question_analysis) > 100 else ''}")
        print(f"   - Tables needed: {required_tables}")
        print(f"   - Processing steps: {len(data_processing_steps)} steps")
        
        # Step 3: Generate SQL from the structured plan
        sql_query = _convert_plan_to_sql(plan_data, tool_context)
        print(f"🔧 Generated SQL: {sql_query[:100]}{'...' if len(sql_query) > 100 else ''}")
        
        # Step 4: Execute the SQL using our proven validation function
        print("🎯 Executing SQL via validate_query_execution...")
        execution_result = validate_query_execution(sql_query, tool_context)
        
        # Step 5: Parse and enhance the execution result
        exec_data = json.loads(execution_result)
        
        # Enhance with query plan metadata
        enhanced_result = {
            **exec_data,  # Include all execution results
            "query_plan_used": True,
            "original_question": question_analysis,
            "tables_accessed": required_tables,
            "generated_sql": sql_query
        }
        
        print(f"✅ Query plan execution complete - Status: {enhanced_result['status']}")
        
        # Store enhanced result in context
        tool_context.state["last_execution_result"] = enhanced_result
        
        return json.dumps(enhanced_result, indent=2)
        
    except Exception as e:
        error_result = {
            "status": "error",
            "execution_successful": False,
            "data": None,
            "row_count": 0,
            "error_message": f"BigQueryRunner execute_query_plan error: {e}",
            "query_plan_used": True
        }
        print(f"❌ BigQueryRunner execute_query_plan error: {e}")
        return json.dumps(error_result, indent=2)


def _convert_plan_to_sql(plan_data: dict, tool_context: ToolContext) -> str:
    """Convert a structured query plan to executable SQL.
    
    This is a helper function that uses an LLM to translate the logical steps
    in a query plan into actual BigQuery SQL.
    
    Args:
        plan_data (dict): Parsed JSON query plan
        tool_context (ToolContext): Tool context with database settings
        
    Returns:
        str: Generated SQL query
    """
    
    # Get database schema for SQL generation
    ddl_schema = tool_context.state["database_settings"]["bq_ddl_schema"]
    
    # Create a prompt template for plan-to-SQL conversion
    prompt_template = """
You are a BigQuery SQL expert. Convert this structured query plan into executable BigQuery SQL.

**Database Schema:**
```
{SCHEMA}
```

**Query Plan:**
```json
{QUERY_PLAN}
```

**Instructions:**
1. Use the query plan's data_processing_steps to guide SQL structure
2. Reference the required_tables and table_relationships
3. Follow the output_requirements for SELECT clause
4. Use proper BigQuery syntax with fully qualified table names
5. Include appropriate filters, joins, aggregations, and ordering
6. Add LIMIT clause if not specified (max 80 rows for performance)

**Return only the SQL query, no explanations:**
"""

    prompt = prompt_template.format(
        SCHEMA=ddl_schema,
        QUERY_PLAN=json.dumps(plan_data, indent=2)
    )
    
    try:
        response = llm_client.models.generate_content(
            model=os.getenv("ROOT_AGENT_MODEL", "gemini-1.5-pro"),
            contents=prompt,
            config={"temperature": 0.1},
        )
        
        sql = response.text
        if sql:
            # Clean up the SQL response
            sql = sql.replace("```sql", "").replace("```", "").strip()
        
        return sql
        
    except Exception as e:
        print(f"❌ Error generating SQL from plan: {e}")
        # Fallback: Create a basic SQL query from available information
        tables = plan_data.get("required_tables", [])
        if tables:
            table_name = tables[0]  # Use first table as fallback
            return f"SELECT * FROM `{tool_context.state['database_settings']['bq_project_id']}.{tool_context.state['database_settings']['bq_dataset_id']}.{table_name}` LIMIT 10"
        else:
            raise Exception(f"Unable to generate SQL and no tables specified in plan: {e}")


def validate_query_execution(
    sql_query: str,
    tool_context: ToolContext,
) -> str:
    """Validate SQL before execution using existing validation tools.

    This function wraps the existing run_bigquery_validation function
    to provide consistent validation for our BigQueryRunner agent.

    Args:
        sql_query (str): The SQL query to validate and execute
        tool_context (ToolContext): The tool context with database settings.

    Returns:
        str: Validation and execution results in JSON format.
    """
    
    try:
        print(f"🔍 BigQueryRunner: Validating SQL query...")
        print(f"   SQL Preview: {sql_query[:100]}{'...' if len(sql_query) > 100 else ''}")
        
        # Ensure we have database settings
        if "database_settings" not in tool_context.state:
            tool_context.state["database_settings"] = get_database_settings()
        
        # Call the existing validation function from data_science
        # This function returns a dict with 'query_result' and 'error_message'
        validation_result = run_bigquery_validation(sql_query, tool_context)
        
        # Format the result consistently for our BigQueryRunner
        if validation_result.get("query_result") is not None:
            # Success case - query executed and returned data
            result = {
                "status": "success",
                "execution_successful": True,
                "data": validation_result["query_result"],
                "row_count": len(validation_result["query_result"]),
                "error_message": None
            }
            print(f"✅ SQL executed successfully - {result['row_count']} rows returned")
            
        elif validation_result.get("error_message"):
            # Error case - validation or execution failed
            result = {
                "status": "error", 
                "execution_successful": False,
                "data": None,
                "row_count": 0,
                "error_message": validation_result["error_message"]
            }
            print(f"❌ SQL execution failed: {result['error_message']}")
            
        else:
            # Edge case - no data and no error (shouldn't happen but handle it)
            result = {
                "status": "success",
                "execution_successful": True, 
                "data": [],
                "row_count": 0,
                "error_message": None
            }
            print("✅ SQL executed successfully - no data returned")
        
        # Store the result in context for future use
        tool_context.state["last_query_result"] = result
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        # Handle any unexpected errors
        error_result = {
            "status": "error",
            "execution_successful": False,
            "data": None,
            "row_count": 0,
            "error_message": f"BigQueryRunner error: {e}"
        }
        print(f"❌ BigQueryRunner error: {e}")
        return json.dumps(error_result, indent=2)


def setup_before_agent_call(callback_context: CallbackContext):
    """Setup the BigQuery runner agent with database settings."""
    
    # Set up database settings (reuse existing infrastructure)
    if "database_settings" not in callback_context.state:
        callback_context.state["database_settings"] = get_database_settings()
    
    # Add schema information to the agent instruction  
    schema = callback_context.state["database_settings"]["bq_ddl_schema"]
    callback_context._invocation_context.agent.instruction = (
        return_instructions_bigquery_runner()
        + f"""

--------- Available BigQuery Schema: ---------
{schema}

"""
    )


# BigQueryRunner Agent definition (basic structure)
bigquery_runner_agent = Agent(
    model=os.getenv("ROOT_AGENT_MODEL", "gemini-1.5-pro"),
    name="bigquery_runner",
    instruction=return_instructions_bigquery_runner(),
    tools=[
        execute_query_plan,
        validate_query_execution,
    ],
    before_agent_callback=setup_before_agent_call,
    generate_content_config=types.GenerateContentConfig(temperature=0.01),
) 