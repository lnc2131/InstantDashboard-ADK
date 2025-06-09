#!/usr/bin/env python3

"""Test script for Step 5: validate_query_execution function."""

import sys
import os

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

def test_validate_query_execution():
    """Test the validate_query_execution function with a simple SQL query."""
    print("🧪 Testing validate_query_execution function...")
    print("=" * 50)
    
    try:
        # Import our function
        from instant_dashboard.sub_agents.bigquery_runner import validate_query_execution
        from data_science.sub_agents.bigquery.tools import get_database_settings
        
        # Create a simple tool context
        class SimpleToolContext:
            def __init__(self):
                self.state = {}
        
        tool_context = SimpleToolContext()
        tool_context.state["database_settings"] = get_database_settings()
        
        print("✅ Setup complete")
        print(f"   - Project: {tool_context.state['database_settings']['bq_project_id']}")
        print(f"   - Dataset: {tool_context.state['database_settings']['bq_dataset_id']}")
        
        # Test with a simple query
        test_sql = "SELECT * FROM `ultra-might-456821-s8.forecasting_sticker_sales.train` LIMIT 3"
        
        print(f"\n🔍 Testing SQL: {test_sql}")
        print("\n📝 Calling validate_query_execution...")
        
        # Call our function
        result = validate_query_execution(test_sql, tool_context)
        
        print("\n✅ Function returned successfully!")
        print("📊 Result:")
        print(result)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_validate_query_execution()
    sys.exit(0 if success else 1) 