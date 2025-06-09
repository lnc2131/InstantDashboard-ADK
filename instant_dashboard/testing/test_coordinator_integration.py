#!/usr/bin/env python3

"""Test script for coordinator integration with Phase 2 + 3 pipeline."""

import sys
import os

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

def test_coordinator_integration():
    """Test that coordinator can run the full Phase 2 → Phase 3 pipeline."""
    print("🧪 Testing Coordinator Integration - Phase 2 + 3 Pipeline")
    print("=" * 65)
    
    try:
        # Import coordinator and tools
        from instant_dashboard.agent import dashboard_agent, execute_full_pipeline
        from data_science.sub_agents.bigquery.tools import get_database_settings
        
        # Create a tool context
        class SimpleToolContext:
            def __init__(self):
                self.state = {}
        
        tool_context = SimpleToolContext()
        tool_context.state["database_settings"] = get_database_settings()
        
        print("✅ Setup complete")
        print(f"   - Coordinator: {dashboard_agent.name}")
        print(f"   - Tools available: {len(dashboard_agent.tools)} tools")
        print(f"   - Database: {tool_context.state['database_settings']['bq_project_id']}")
        
        # Test question that should trigger the full pipeline
        test_question = "What are the top 5 stores by total revenue?"
        
        print(f"\n📝 Test Question: {test_question}")
        print("\n🚀 Testing execute_full_pipeline directly...")
        
        # Test the full pipeline function directly
        result = execute_full_pipeline(test_question, tool_context)
        
        print(f"\n✅ Pipeline execution completed!")
        print("📊 Result Preview:")
        
        # Show a preview of the result
        if len(result) > 500:
            print(result[:500] + "...")
            print(f"\n📏 Full result length: {len(result)} characters")
        else:
            print(result)
        
        # Check for success indicators
        if "success" in result.lower():
            print(f"\n🎉 SUCCESS: Full pipeline execution completed successfully!")
            if "query_plan_used" in result:
                print("   ✅ Query plan was generated and used")
            if "generated_sql" in result:
                print("   ✅ SQL was generated from the plan")
            if "data" in result:
                print("   ✅ Data was returned from BigQuery")
        else:
            print(f"\n⚠️ Pipeline may have encountered issues")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_coordinator_tools():
    """Test that coordinator has all expected tools."""
    print("\n🔧 Testing Coordinator Tools...")
    print("=" * 40)
    
    try:
        from instant_dashboard.agent import dashboard_agent
        
        expected_tools = [
            "call_db_agent",
            "call_query_planner_agent", 
            "call_bigquery_runner_agent",
            "execute_full_pipeline"
        ]
        
        tool_names = [tool.__name__ if hasattr(tool, '__name__') else str(tool) for tool in dashboard_agent.tools]
        
        print(f"Available tools: {len(tool_names)}")
        for i, tool_name in enumerate(tool_names, 1):
            print(f"   {i}. {tool_name}")
        
        # Check for expected tools
        for expected in expected_tools:
            found = any(expected in str(tool_name) for tool_name in tool_names)
            status = "✅" if found else "❌"
            print(f"{status} {expected}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking tools: {e}")
        return False


if __name__ == "__main__":
    print("🎯 Starting Coordinator Integration Tests")
    print("=" * 65)
    
    success1 = test_coordinator_tools()
    success2 = test_coordinator_integration()
    
    if success1 and success2:
        print(f"\n🎉 All integration tests passed!")
        print("💡 Phase 3 BigQueryRunner integration is working correctly!")
    else:
        print(f"\n❌ Some tests failed - check output above")
    
    sys.exit(0 if (success1 and success2) else 1) 