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

"""QueryPlannerAgent: Converts natural language to structured query plans.

This agent is responsible for Phase 2 of the InstantDashboard pipeline:
Natural Language → Query Plan → SQL (future phases will handle SQL execution)
"""

import os
import json

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import ToolContext
from google.genai import types, Client
from google.cloud import bigquery

# Import existing database functionality
from data_science.sub_agents.bigquery.tools import get_database_settings
from data_science.utils.utils import get_env_var

# Import prompts
from ..prompts import return_instructions_query_planner

# Initialize clients
project = os.getenv("BQ_PROJECT_ID", None)
location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
llm_client = Client(vertexai=True, project=project, location=location)


def generate_query_plan(
    question: str,
    tool_context: ToolContext,
) -> str:
    """Generates a structured query plan from a natural language question.

    This function adapts the sophisticated query planning approach from the 
    existing BigQuery infrastructure, focusing on breaking down questions
    into logical steps before SQL generation.

    Args:
        question (str): Natural language question about the data.
        tool_context (ToolContext): The tool context with database settings.

    Returns:
        str: A structured query plan in JSON format with steps and reasoning.
    """
    
    # Get schema from existing database settings
    ddl_schema = tool_context.state["database_settings"]["bq_ddl_schema"]
    
    # Use adapted query planning prompt template
    prompt_template = """
You are an expert database query planner. Your job is to analyze natural language questions 
and create structured query plans that break down complex questions into logical steps.

You will use the "Query Plan Guided Analysis" method that involves:
1. Understanding the question requirements
2. Identifying relevant tables and relationships  
3. Breaking down into logical preparation, filtering, joining, and aggregation steps
4. Planning the sequence of operations needed

**Database Schema:**
```
{SCHEMA}
```

**Natural Language Question:**
```
{QUESTION}
```

**Task:** Create a structured query plan that includes:

1. **Question Analysis:** Restate and clarify what is being asked
2. **Required Tables:** List tables needed and their relationships  
3. **Preparation Steps:** Setup and initialization steps
4. **Data Processing Steps:** Filtering, joining, aggregation steps in logical order
5. **Output Requirements:** What the final result should contain

**Output Format:** Return a JSON object with this structure:
```json
{{
    "question_analysis": "Clear restatement of what is being asked",
    "required_tables": ["table1", "table2", ...],
    "table_relationships": "Description of how tables relate",
    "preparation_steps": [
        "Step 1: Initialize process and setup environment",
        "Step 2: Open required tables for access"
    ],
    "data_processing_steps": [
        "Step 1: Filter data based on conditions",
        "Step 2: Join tables on relationships", 
        "Step 3: Apply aggregations as needed"
    ],
    "output_requirements": "Description of expected final result format",
    "complexity_assessment": "Simple|Medium|Complex",
    "estimated_performance": "Description of expected query performance"
}}
```

Think step-by-step through the question and create a comprehensive query plan.
"""

    prompt = prompt_template.format(
        SCHEMA=ddl_schema,
        QUESTION=question
    )

    try:
        response = llm_client.models.generate_content(
            model=os.getenv("ROOT_AGENT_MODEL", "gemini-1.5-pro"),
            contents=prompt,
            config={"temperature": 0.1},
        )

        query_plan = response.text
        if query_plan:
            # Clean up the response - remove any markdown formatting
            query_plan = query_plan.replace("```json", "").replace("```", "").strip()
            
            # Validate JSON format
            try:
                json.loads(query_plan)
                print("✅ Generated structured query plan")
            except json.JSONDecodeError:
                print("⚠️ Query plan generated but not in valid JSON format")
        
        # Store the query plan in context for future phases
        tool_context.state["query_plan"] = query_plan
        tool_context.state["original_question"] = question
        
        return query_plan

    except Exception as e:
        error_msg = f"❌ Error generating query plan: {e}"
        print(error_msg)
        return json.dumps({
            "error": error_msg,
            "question_analysis": question,
            "status": "failed"
        })


def validate_query_plan(
    query_plan: str,
    tool_context: ToolContext,
) -> str:
    """Validates and refines a query plan for completeness and accuracy.

    Args:
        query_plan (str): The query plan in JSON format to validate.
        tool_context (ToolContext): The tool context with database settings.

    Returns:
        str: Validation results and any recommended improvements.
    """
    
    try:
        # Parse the query plan
        plan_data = json.loads(query_plan)
        
        validation_results = {
            "is_valid": True,
            "completeness_score": 0,
            "missing_elements": [],
            "recommendations": []
        }
        
        # Check required elements
        required_elements = [
            "question_analysis", 
            "required_tables", 
            "preparation_steps",
            "data_processing_steps",
            "output_requirements"
        ]
        
        for element in required_elements:
            if element in plan_data and plan_data[element]:
                validation_results["completeness_score"] += 1
            else:
                validation_results["missing_elements"].append(element)
                validation_results["is_valid"] = False
        
        # Calculate completeness percentage
        validation_results["completeness_score"] = (
            validation_results["completeness_score"] / len(required_elements) * 100
        )
        
        # Add recommendations based on analysis
        if validation_results["completeness_score"] < 80:
            validation_results["recommendations"].append(
                "Query plan needs more detail in missing elements"
            )
        
        if "required_tables" in plan_data:
            table_count = len(plan_data["required_tables"])
            if table_count > 3:
                validation_results["recommendations"].append(
                    f"Complex query with {table_count} tables - consider optimization"
                )
        
        print(f"✅ Query plan validation complete: {validation_results['completeness_score']:.1f}% complete")
        
        tool_context.state["query_plan_validation"] = validation_results
        
        return json.dumps(validation_results, indent=2)
        
    except json.JSONDecodeError:
        error_result = {
            "is_valid": False,
            "error": "Query plan is not valid JSON format",
            "recommendations": ["Regenerate query plan in proper JSON format"]
        }
        return json.dumps(error_result, indent=2)
    
    except Exception as e:
        error_result = {
            "is_valid": False,
            "error": f"Validation error: {e}",
            "recommendations": ["Check query plan format and content"]
        }
        return json.dumps(error_result, indent=2)


def setup_before_agent_call(callback_context: CallbackContext):
    """Setup the query planner agent with database settings."""
    
    # Set up database settings (reuse existing infrastructure)
    if "database_settings" not in callback_context.state:
        callback_context.state["database_settings"] = get_database_settings()
    
    # Add schema information to the agent instruction
    schema = callback_context.state["database_settings"]["bq_ddl_schema"]
    callback_context._invocation_context.agent.instruction = (
        return_instructions_query_planner()
        + f"""

--------- Available BigQuery Schema: ---------
{schema}

"""
    )


# QueryPlannerAgent definition
query_planner_agent = Agent(
    model=os.getenv("ROOT_AGENT_MODEL", "gemini-1.5-pro"),
    name="query_planner",
    instruction=return_instructions_query_planner(),
    tools=[
        generate_query_plan,
        validate_query_plan,
    ],
    before_agent_callback=setup_before_agent_call,
    generate_content_config=types.GenerateContentConfig(temperature=0.01),
) 