#!/usr/bin/env python3

"""Direct test of query_planner function."""

import sys
import os

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

def test_direct_query_planner():
    """Test the query_planner function directly."""
    print("🧪 Testing query_planner function directly...")
    print("=" * 50)
    
    try:
        # Import the function
        from instant_dashboard.sub_agents.query_planner import generate_query_plan
        from data_science.sub_agents.bigquery.tools import get_database_settings
        
        # Create context
        class SimpleToolContext:
            def __init__(self):
                self.state = {}
        
        tool_context = SimpleToolContext()
        tool_context.state["database_settings"] = get_database_settings()
        
        print("✅ Setup complete")
        
        # Test with simple question
        question = "What are the top 3 countries?"
        print(f"📝 Question: {question}")
        
        # Call the function
        result = generate_query_plan(question, tool_context)
        
        print("✅ Function completed successfully!")
        print("📊 Result preview:")
        print(result[:200] + "..." if len(result) > 200 else result)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_direct_query_planner() 