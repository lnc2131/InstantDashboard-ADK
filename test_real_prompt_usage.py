#!/usr/bin/env python3

"""Test real prompt usage with InstantDashboard coordinator.

This test investigates why Phase 3 integration doesn't work properly 
when using the coordinator agent with actual natural language prompts.
"""

import sys
import os

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

def test_coordinator_with_real_prompt():
    """Test the coordinator agent with a real natural language prompt."""
    print("🧪 Testing Coordinator Agent with Real Prompt...")
    print("=" * 60)
    
    try:
        # Import the coordinator agent
        from instant_dashboard.agent import dashboard_agent
        
        print(f"✅ Coordinator agent imported successfully")
        print(f"   - Name: {dashboard_agent.name}")
        print(f"   - Tools: {len(dashboard_agent.tools)} available")
        
        # Test with a real business question
        test_question = "What are the top 5 countries by total sticker sales?"
        
        print(f"\n📝 Testing with question: '{test_question}'")
        print("🚀 Calling dashboard_agent.generate_content()...")
        
        # This is where the integration likely fails
        response = dashboard_agent.generate_content(test_question)
        
        print(f"✅ Response received:")
        print(f"   Response type: {type(response)}")
        print(f"   Response content preview: {str(response)[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error with coordinator prompt: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_direct_tool_calls():
    """Test calling the integration tools directly to isolate issues."""
    print("\n🧪 Testing Direct Tool Calls...")
    print("=" * 60)
    
    try:
        from instant_dashboard.agent import execute_full_pipeline
        from data_science.sub_agents.bigquery.tools import get_database_settings
        
        # Create simple tool context
        class SimpleToolContext:
            def __init__(self):
                self.state = {}
        
        tool_context = SimpleToolContext()
        tool_context.state["database_settings"] = get_database_settings()
        
        test_question = "What are the top 3 stores by sales volume?"
        
        print(f"📝 Question: {test_question}")
        print("🚀 Calling execute_full_pipeline directly...")
        
        result = execute_full_pipeline(test_question, tool_context)
        
        print(f"✅ Direct tool call successful:")
        print(f"   Result type: {type(result)}")
        print(f"   Result preview: {str(result)[:300]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error with direct tool call: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_context_setup():
    """Test if the agent context setup is working properly."""
    print("\n🧪 Testing Agent Context Setup...")
    print("=" * 60)
    
    try:
        from instant_dashboard.agent import setup_before_agent_call
        from google.adk.agents.callback_context import CallbackContext
        
        # Create a mock callback context
        class MockCallbackContext:
            def __init__(self):
                self.state = {}
                self._invocation_context = None
        
        callback_context = MockCallbackContext()
        
        print("🔧 Testing setup_before_agent_call...")
        setup_before_agent_call(callback_context)
        
        print(f"✅ Context setup completed:")
        print(f"   State keys: {list(callback_context.state.keys())}")
        
        if "database_settings" in callback_context.state:
            db_settings = callback_context.state["database_settings"]
            print(f"   Database settings: {type(db_settings)}")
            print(f"   Schema available: {'bq_ddl_schema' in db_settings}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error with context setup: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run integration debugging tests."""
    print("🔍 Phase 3 Integration Debugging")
    print("=" * 60)
    print("Purpose: Find why coordinator agent doesn't work with real prompts")
    
    tests = [
        ("Agent Context Setup", test_agent_context_setup),
        ("Direct Tool Calls", test_direct_tool_calls),
        ("Coordinator with Real Prompt", test_coordinator_with_real_prompt),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print(f"{'='*60}")
        results.append(test_func())
    
    # Summary
    print(f"\n📊 Integration Debugging Results:")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    for i, (test_name, _) in enumerate(tests):
        status = "✅ WORKING" if results[i] else "❌ BROKEN"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} components working")
    
    if passed < total:
        print(f"\n🔧 INTEGRATION ISSUES IDENTIFIED:")
        print(f"   - {total-passed} component(s) have problems")
        print(f"   - This explains why Phase 3 doesn't work with real prompts")
        print(f"   - Need to fix these specific integration issues")
    else:
        print(f"\n🤔 All components work individually...")
        print(f"   - Issue may be in the agent framework integration")
        print(f"   - Need to investigate ADK agent behavior")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 