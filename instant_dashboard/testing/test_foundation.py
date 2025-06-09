#!/usr/bin/env python3

"""Test script for InstantDashboard foundation setup.

This script tests basic integration with existing infrastructure:
- Can import our agent
- Can access database settings
- Can verify environment setup
"""

import sys
import os

# Add parent directories to path so we can import modules from any location
current_dir = os.path.dirname(os.path.abspath(__file__))
instant_dashboard_dir = os.path.dirname(current_dir)
data_science_dir = os.path.dirname(instant_dashboard_dir)
sys.path.append(data_science_dir)
sys.path.append(instant_dashboard_dir)

def test_imports():
    """Test that we can import our agent and dependencies."""
    print("🧪 Testing imports...")
    
    try:
        from instant_dashboard.agent import dashboard_agent
        print("✅ Successfully imported dashboard_agent")
    except ImportError as e:
        print(f"❌ Failed to import dashboard_agent: {e}")
        return False
    
    try:
        from data_science.sub_agents.bigquery.tools import get_database_settings
        print("✅ Successfully imported existing BigQuery tools")
    except ImportError as e:
        print(f"❌ Failed to import BigQuery tools: {e}")
        return False
    
    # Test InstantDashboard-specific dependencies
    required_packages = ['pandas', 'jsonschema', 'requests', 'sqlglot', 'pydantic']
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is available")
        except ImportError:
            print(f"❌ {package} is missing")
            return False
    
    return True


def test_environment():
    """Test that required environment variables are set."""
    print("\n🧪 Testing environment...")
    
    required_vars = [
        'BQ_PROJECT_ID',
        'BQ_DATASET_ID', 
        'ROOT_AGENT_MODEL'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        print("💡 Make sure your .env file is set up correctly")
        return False
    else:
        print("✅ All required environment variables are set")
        return True


def test_database_settings():
    """Test that we can access database settings."""
    print("\n🧪 Testing database settings...")
    
    try:
        from data_science.sub_agents.bigquery.tools import get_database_settings
        settings = get_database_settings()
        
        print(f"✅ Database settings loaded:")
        print(f"   - Project ID: {settings.get('bq_project_id', 'Not set')}")
        print(f"   - Dataset ID: {settings.get('bq_dataset_id', 'Not set')}")
        print(f"   - Schema loaded: {'Yes' if settings.get('bq_ddl_schema') else 'No'}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to get database settings: {e}")
        return False


def test_prompt_system():
    """Test that the prompt system works."""
    print("\n🧪 Testing prompt system...")
    
    try:
        from instant_dashboard.prompts import return_instructions_coordinator
        
        # Test getting coordinator prompt
        prompt = return_instructions_coordinator()
        if not prompt:
            print("❌ Coordinator prompt is empty")
            return False
        print("✅ Coordinator prompt loaded successfully")
        
        # Test prompt content
        if "InstantDashboard" not in prompt:
            print("❌ Prompt doesn't contain InstantDashboard")
            return False
        print("✅ Prompt content looks correct")
        
        print(f"✅ Prompt length: {len(prompt)} characters")
        
        return True
    except Exception as e:
        print(f"❌ Failed to test prompt system: {e}")
        return False


def test_agent_creation():
    """Test that we can create our agent instance."""
    print("\n🧪 Testing agent creation...")
    
    try:
        from instant_dashboard.agent import dashboard_agent
        
        print(f"✅ Agent created successfully:")
        print(f"   - Name: {dashboard_agent.name}")
        print(f"   - Model: {dashboard_agent.model}")
        print(f"   - Tools: {len(dashboard_agent.tools)} tool(s)")
        
        # Test that agent uses versioned prompts
        instruction = dashboard_agent.instruction
        if "InstantDashboard" not in instruction:
            print("❌ Agent instruction doesn't seem to use InstantDashboard prompt")
            return False
        print("✅ Agent is using InstantDashboard prompt system")
        
        return True
    except Exception as e:
        print(f"❌ Failed to create agent: {e}")
        return False


# Phase 2: QueryPlannerAgent Tests

def test_query_planner_imports():
    """Test that QueryPlannerAgent can be imported."""
    print("\n🧪 Testing QueryPlannerAgent imports...")
    
    try:
        from instant_dashboard.sub_agents.query_planner import query_planner_agent
        print("✅ Successfully imported query_planner_agent")
    except ImportError as e:
        print(f"❌ Failed to import query_planner_agent: {e}")
        return False
    
    try:
        from instant_dashboard.sub_agents.query_planner import generate_query_plan, validate_query_plan
        print("✅ Successfully imported query planner tools")
    except ImportError as e:
        print(f"❌ Failed to import query planner tools: {e}")
        return False
    
    return True


def test_query_planner_prompts():
    """Test query planner prompt system."""
    print("\n🧪 Testing QueryPlannerAgent prompts...")
    
    try:
        from instant_dashboard.prompts import return_instructions_query_planner
        
        prompt = return_instructions_query_planner()
        if not prompt:
            print("❌ Query planner prompt is empty")
            return False
        print("✅ Query planner prompt loaded successfully")
        
        # Test prompt content
        if "QueryPlannerAgent" not in prompt:
            print("❌ Prompt doesn't contain QueryPlannerAgent")
            return False
        print("✅ Query planner prompt content looks correct")
        
        # Test that it's not the placeholder
        if "placeholder" in prompt.lower():
            print("❌ Prompt still contains placeholder text")
            return False
        print("✅ Prompt has been properly updated from placeholder")
        
        return True
    except Exception as e:
        print(f"❌ Failed to test query planner prompts: {e}")
        return False


def test_query_planner_agent_creation():
    """Test that QueryPlannerAgent can be created."""
    print("\n🧪 Testing QueryPlannerAgent creation...")
    
    try:
        from instant_dashboard.sub_agents.query_planner import query_planner_agent
        
        print(f"✅ QueryPlannerAgent created successfully:")
        print(f"   - Name: {query_planner_agent.name}")
        print(f"   - Model: {query_planner_agent.model}")
        print(f"   - Tools: {len(query_planner_agent.tools)} tool(s)")
        
        # Test that it has the right tools
        expected_tools = ['generate_query_plan', 'validate_query_plan']
        tool_names = [tool.__name__ if hasattr(tool, '__name__') else str(tool) for tool in query_planner_agent.tools]
        
        for expected_tool in expected_tools:
            found = any(expected_tool in str(tool_name) for tool_name in tool_names)
            if found:
                print(f"✅ Has {expected_tool} tool")
            else:
                print(f"❌ Missing {expected_tool} tool")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Failed to create QueryPlannerAgent: {e}")
        return False


def test_coordinator_integration():
    """Test that coordinator integrates QueryPlannerAgent."""
    print("\n🧪 Testing coordinator integration with QueryPlannerAgent...")
    
    try:
        from instant_dashboard.agent import dashboard_agent, call_query_planner_agent
        
        # Check that coordinator has the new tool
        tool_names = [tool.__name__ if hasattr(tool, '__name__') else str(tool) for tool in dashboard_agent.tools]
        
        has_query_planner_tool = any('query_planner' in str(tool_name) for tool_name in tool_names)
        if not has_query_planner_tool:
            print("❌ Coordinator doesn't have query planner tool")
            return False
        print("✅ Coordinator has query planner tool")
        
        # Check that global instruction mentions Phase 2
        global_instruction = dashboard_agent.global_instruction
        if "Phase 2" not in global_instruction:
            print("❌ Global instruction doesn't mention Phase 2")
            return False
        print("✅ Global instruction updated for Phase 2")
        
        # Check that it has both Phase 1 and Phase 2 tools
        if len(dashboard_agent.tools) < 2:
            print("❌ Coordinator doesn't have enough tools")
            return False
        print(f"✅ Coordinator has {len(dashboard_agent.tools)} tools (Phase 1 + Phase 2)")
        
        return True
    except Exception as e:
        print(f"❌ Failed to test coordinator integration: {e}")
        return False


def test_phase_2_workflow():
    """Test basic Phase 2 workflow without calling LLM."""
    print("\n🧪 Testing Phase 2 workflow structure...")
    
    try:
        # Test that we can access all Phase 2 components
        from instant_dashboard.sub_agents.query_planner import generate_query_plan, validate_query_plan
        from instant_dashboard.agent import call_query_planner_agent
        
        print("✅ All Phase 2 workflow components accessible")
        
        # Test that functions have proper signatures
        import inspect
        
        # Check generate_query_plan signature
        sig = inspect.signature(generate_query_plan)
        params = list(sig.parameters.keys())
        if 'question' not in params or 'tool_context' not in params:
            print("❌ generate_query_plan has incorrect signature")
            return False
        print("✅ generate_query_plan has correct signature")
        
        # Check validate_query_plan signature  
        sig = inspect.signature(validate_query_plan)
        params = list(sig.parameters.keys())
        if 'query_plan' not in params or 'tool_context' not in params:
            print("❌ validate_query_plan has incorrect signature")
            return False
        print("✅ validate_query_plan has correct signature")
        
        # Check call_query_planner_agent signature
        sig = inspect.signature(call_query_planner_agent)
        params = list(sig.parameters.keys())
        if 'question' not in params or 'tool_context' not in params:
            print("❌ call_query_planner_agent has incorrect signature")
            return False
        print("✅ call_query_planner_agent has correct signature")
        
        return True
    except Exception as e:
        print(f"❌ Failed to test Phase 2 workflow: {e}")
        return False


def main():
    """Run all foundation and Phase 2 tests."""
    print("🚀 InstantDashboard Foundation & Phase 2 Tests")
    print("=" * 50)
    
    foundation_tests = [
        test_imports,
        test_environment,
        test_database_settings,
        test_prompt_system,
        test_agent_creation,
    ]
    
    phase_2_tests = [
        test_query_planner_imports,
        test_query_planner_prompts,
        test_query_planner_agent_creation,
        test_coordinator_integration,
        test_phase_2_workflow,
    ]
    
    print("📋 Running Foundation Tests...")
    foundation_results = []
    for test in foundation_tests:
        foundation_results.append(test())
    
    print("\n📋 Running Phase 2 Tests...")
    phase_2_results = []
    for test in phase_2_tests:
        phase_2_results.append(test())
    
    print("\n📊 Test Results:")
    print("=" * 50)
    
    foundation_passed = sum(foundation_results)
    foundation_total = len(foundation_results)
    
    phase_2_passed = sum(phase_2_results)
    phase_2_total = len(phase_2_results)
    
    total_passed = foundation_passed + phase_2_passed
    total_tests = foundation_total + phase_2_total
    
    print(f"🏗️  Foundation: {foundation_passed}/{foundation_total} passed")
    print(f"🚀 Phase 2:    {phase_2_passed}/{phase_2_total} passed")
    print(f"📊 Overall:    {total_passed}/{total_tests} passed")
    
    if total_passed == total_tests:
        print(f"\n🎉 All tests passed! ({total_passed}/{total_tests})")
        print("\n✅ Phase 2 QueryPlannerAgent is working correctly!")
        print("💡 Ready to proceed to Phase 3: BigQueryRunner")
    else:
        failed = total_tests - total_passed
        print(f"\n❌ {failed} test(s) failed")
        
        if foundation_passed < foundation_total:
            print("🔧 Fix foundation issues first")
        if phase_2_passed < phase_2_total:
            print("🔧 Fix Phase 2 issues before proceeding")
    
    return total_passed == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 