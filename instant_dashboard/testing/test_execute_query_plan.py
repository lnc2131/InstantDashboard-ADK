#!/usr/bin/env python3

"""Test script for execute_query_plan function using a real Phase 2 query plan."""

import sys
import os
import json

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

def test_execute_query_plan():
    """Test execute_query_plan with a real query plan from Phase 2."""
    print("🧪 Testing execute_query_plan with Phase 2 Query Plan...")
    print("=" * 60)
    
    try:
        # Import our functions
        from instant_dashboard.sub_agents.bigquery_runner import execute_query_plan
        from instant_dashboard.shared import get_database_settings
        
        # Create a tool context
        class SimpleToolContext:
            def __init__(self):
                self.state = {}
        
        tool_context = SimpleToolContext()
        tool_context.state["database_settings"] = get_database_settings()
        
        print("✅ Setup complete")
        print(f"   - Project: {tool_context.state['database_settings']['bq_project_id']}")
        print(f"   - Dataset: {tool_context.state['database_settings']['bq_dataset_id']}")
        
        # Create a realistic query plan (similar to what Phase 2 would generate)
        sample_query_plan = {
            "question_analysis": "Find the top 3 countries by total stickers sold",
            "required_tables": ["train"],
            "table_relationships": "Single table analysis - no joins needed",
            "preparation_steps": [
                "Step 1: Initialize query processing environment",
                "Step 2: Access the train table"
            ],
            "data_processing_steps": [
                "Step 1: Group the data by country",
                "Step 2: Calculate the sum of num_sold for each country", 
                "Step 3: Order results by total sales in descending order",
                "Step 4: Limit results to top 3 countries"
            ],
            "output_requirements": "Return country name and total sales, ordered by sales descending",
            "complexity_assessment": "Medium",
            "estimated_performance": "Good - simple aggregation with GROUP BY"
        }
        
        # Convert to JSON string (as it would come from Phase 2)
        query_plan_json = json.dumps(sample_query_plan, indent=2)
        
        print(f"\n📋 Test Query Plan:")
        print(f"   - Question: {sample_query_plan['question_analysis']}")
        print(f"   - Tables: {sample_query_plan['required_tables']}")
        print(f"   - Steps: {len(sample_query_plan['data_processing_steps'])} processing steps")
        
        print(f"\n🚀 Calling execute_query_plan...")
        
        # Call our main function
        result = execute_query_plan(query_plan_json, tool_context)
        
        print(f"\n✅ Function completed!")
        print("📊 Result:")
        print(result)
        
        # Parse result to check success
        result_data = json.loads(result)
        if result_data.get("status") == "success":
            print(f"\n🎉 SUCCESS! Query plan executed successfully")
            print(f"   - Rows returned: {result_data.get('row_count', 0)}")
            print(f"   - Used query plan: {result_data.get('query_plan_used', False)}")
            print(f"   - Generated SQL available: {'generated_sql' in result_data}")
        else:
            print(f"\n⚠️ Execution failed: {result_data.get('error_message', 'Unknown error')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_execute_query_plan()
    sys.exit(0 if success else 1) 