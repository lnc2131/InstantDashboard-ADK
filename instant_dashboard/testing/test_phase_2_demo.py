#!/usr/bin/env python3

"""Demo script for Phase 2 QueryPlannerAgent functionality."""

import sys
import os

# Add parent directories to path so we can import modules from any location
current_dir = os.path.dirname(os.path.abspath(__file__))
instant_dashboard_dir = os.path.dirname(current_dir)
data_science_dir = os.path.dirname(instant_dashboard_dir)
sys.path.append(data_science_dir)
sys.path.append(instant_dashboard_dir)

def demo_query_planner():
    """Demonstrate QueryPlannerAgent functionality."""
    print("🚀 Phase 2 QueryPlannerAgent Demo")
    print("=" * 40)
    
    # Import required components
    from instant_dashboard.agent import dashboard_agent
    from instant_dashboard.sub_agents.query_planner import generate_query_plan
    from google.adk.tools import ToolContext
    from instant_dashboard.shared import get_database_settings
    
    # Test question
    question = "Show me the top 5 countries by total sessions for the last 30 days"
    
    print(f"📝 Question: {question}")
    print("\n🔧 Setting up database context...")
    
    try:
        # Create a tool context with database settings
        class SimpleToolContext:
            def __init__(self):
                self.state = {}
        
        tool_context = SimpleToolContext()
        tool_context.state["database_settings"] = get_database_settings()
        
        print("✅ Database settings loaded")
        print(f"   - Project: {tool_context.state['database_settings']['bq_project_id']}")
        print(f"   - Dataset: {tool_context.state['database_settings']['bq_dataset_id']}")
        
        print("\n🤖 Calling QueryPlannerAgent...")
        
        # Call the query planner directly
        query_plan = generate_query_plan(question, tool_context)
        
        print("\n✅ Query Plan Generated:")
        print("=" * 60)
        print(query_plan)
        print("=" * 60)
        
        # Show that the plan was stored in context
        if "query_plan" in tool_context.state:
            print("\n📊 Additional Context:")
            print(f"   - Original question stored: {'original_question' in tool_context.state}")
            print(f"   - Query plan stored: {'query_plan' in tool_context.state}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = demo_query_planner()
    sys.exit(0 if success else 1) 