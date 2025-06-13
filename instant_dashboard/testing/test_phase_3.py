#!/usr/bin/env python3

"""Comprehensive test suite for Phase 3: BigQueryRunner Agent.

This test suite validates all Phase 3 functionality:
- BigQueryRunner agent creation and setup
- Query plan execution 
- SQL validation and execution
- Integration with Phase 2 QueryPlannerAgent
- End-to-end pipeline functionality
"""

import sys
import os
import json

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
instant_dashboard_dir = os.path.dirname(current_dir)
data_science_dir = os.path.dirname(instant_dashboard_dir)
sys.path.append(data_science_dir)
sys.path.append(instant_dashboard_dir)


def test_bigquery_runner_imports():
    """Test Phase 3: BigQueryRunner imports and agent creation."""
    print("🧪 Testing BigQueryRunner Imports...")
    print("=" * 50)
    
    try:
        # Test BigQueryRunner agent import
        from instant_dashboard.sub_agents.bigquery_runner import bigquery_runner_agent
        print("✅ BigQueryRunner agent imported successfully")
        print(f"   - Name: {bigquery_runner_agent.name}")
        print(f"   - Tools: {len(bigquery_runner_agent.tools)} tool(s)")
        
        # Test individual tool imports
        from instant_dashboard.sub_agents.bigquery_runner import execute_query_plan, validate_query_execution
        print("✅ BigQueryRunner tools imported successfully")
        print("   - execute_query_plan: Main Phase 3 function")
        print("   - validate_query_execution: SQL validation wrapper")
        
        # Test prompt import
        from instant_dashboard.prompts import return_instructions_bigquery_runner
        prompt = return_instructions_bigquery_runner()
        if "BigQueryRunnerAgent" in prompt and len(prompt) > 100:
            print("✅ BigQueryRunner prompt loaded and updated from placeholder")
        else:
            print("❌ BigQueryRunner prompt seems to be placeholder")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False


def test_validate_query_execution():
    """Test Phase 3: SQL validation and execution functionality."""
    print("\n🧪 Testing validate_query_execution Function...")
    print("=" * 50)
    
    try:
        from instant_dashboard.sub_agents.bigquery_runner import validate_query_execution
        from instant_dashboard.shared import get_database_settings
        
        # Create test context
        class SimpleToolContext:
            def __init__(self):
                self.state = {}
        
        tool_context = SimpleToolContext()
        tool_context.state["database_settings"] = get_database_settings()
        
        # Test SQL query
        test_sql = "SELECT country, COUNT(*) as count FROM `ultra-might-456821-s8.forecasting_sticker_sales.train` GROUP BY country LIMIT 3"
        
        print(f"📝 Test SQL: {test_sql[:60]}...")
        result = validate_query_execution(test_sql, tool_context)
        
        # Parse and validate result
        result_data = json.loads(result)
        
        if result_data.get("status") == "success" and result_data.get("row_count", 0) > 0:
            print(f"✅ SQL executed successfully")
            print(f"   - Status: {result_data['status']}")
            print(f"   - Rows: {result_data['row_count']}")
            print(f"   - Sample data: {result_data['data'][0] if result_data['data'] else 'None'}")
            return True
        else:
            print(f"❌ SQL execution failed: {result_data.get('error_message', 'Unknown error')}")
            return False
        
    except Exception as e:
        print(f"❌ Validation test error: {e}")
        return False


def test_execute_query_plan():
    """Test Phase 3: Query plan execution functionality."""
    print("\n🧪 Testing execute_query_plan Function...")
    print("=" * 50)
    
    try:
        from instant_dashboard.sub_agents.bigquery_runner import execute_query_plan
        from instant_dashboard.shared import get_database_settings
        
        # Create test context
        class SimpleToolContext:
            def __init__(self):
                self.state = {}
        
        tool_context = SimpleToolContext()
        tool_context.state["database_settings"] = get_database_settings()
        
        # Create realistic query plan (from Phase 2 format)
        test_query_plan = {
            "question_analysis": "Find top 3 stores by sales count",
            "required_tables": ["train"],
            "table_relationships": "Single table analysis",
            "preparation_steps": [
                "Step 1: Access train table",
                "Step 2: Prepare aggregation"
            ],
            "data_processing_steps": [
                "Step 1: Group by store",
                "Step 2: Count sales per store",
                "Step 3: Order by count descending",
                "Step 4: Limit to top 3"
            ],
            "output_requirements": "Store name and sales count",
            "complexity_assessment": "Medium",
            "estimated_performance": "Good - simple aggregation"
        }
        
        query_plan_json = json.dumps(test_query_plan, indent=2)
        
        print(f"📋 Test Query Plan: {test_query_plan['question_analysis']}")
        result = execute_query_plan(query_plan_json, tool_context)
        
        # Parse and validate result
        result_data = json.loads(result)
        
        if result_data.get("status") == "success":
            print(f"✅ Query plan executed successfully")
            print(f"   - Status: {result_data['status']}")
            print(f"   - Rows: {result_data.get('row_count', 0)}")
            print(f"   - Used query plan: {result_data.get('query_plan_used', False)}")
            print(f"   - SQL generated: {'generated_sql' in result_data}")
            
            if result_data.get('data'):
                print(f"   - Sample result: {result_data['data'][0]}")
            
            return True
        else:
            print(f"❌ Query plan execution failed: {result_data.get('error_message', 'Unknown error')}")
            return False
        
    except Exception as e:
        print(f"❌ Query plan test error: {e}")
        return False


def test_phase_2_3_integration():
    """Test Phase 2 + 3: QueryPlanner → BigQueryRunner integration."""
    print("\n🧪 Testing Phase 2 + 3 Integration...")
    print("=" * 50)
    
    try:
        from instant_dashboard.sub_agents.query_planner import generate_query_plan
        from instant_dashboard.sub_agents.bigquery_runner import execute_query_plan
        from instant_dashboard.shared import get_database_settings
        
        # Create test context
        class SimpleToolContext:
            def __init__(self):
                self.state = {}
        
        tool_context = SimpleToolContext()
        tool_context.state["database_settings"] = get_database_settings()
        
        # Test question
        question = "What are the top 3 products by total sales?"
        
        print(f"📝 Question: {question}")
        
        # Phase 2: Generate query plan
        print("📋 Phase 2: Generating query plan...")
        query_plan = generate_query_plan(question, tool_context)
        
        # Validate query plan format
        try:
            plan_data = json.loads(query_plan)
            print(f"✅ Phase 2 complete - valid JSON plan generated")
            print(f"   - Tables: {plan_data.get('required_tables', [])}")
            print(f"   - Steps: {len(plan_data.get('data_processing_steps', []))}")
        except json.JSONDecodeError:
            print("❌ Phase 2 failed - invalid JSON plan")
            return False
        
        # Phase 3: Execute query plan
        print("⚡ Phase 3: Executing query plan...")
        execution_result = execute_query_plan(query_plan, tool_context)
        
        # Validate execution result
        result_data = json.loads(execution_result)
        
        if result_data.get("status") == "success":
            print(f"✅ Phase 3 complete - plan executed successfully")
            print(f"   - Status: {result_data['status']}")
            print(f"   - Rows: {result_data.get('row_count', 0)}")
            print(f"   - Original question preserved: {'original_question' in result_data}")
            
            print(f"\n🎉 END-TO-END SUCCESS: Question → Plan → SQL → Data")
            print(f"   Pipeline: Natural Language → Structured Plan → Generated SQL → BigQuery Results")
            
            return True
        else:
            print(f"❌ Phase 3 failed: {result_data.get('error_message', 'Unknown error')}")
            return False
        
    except Exception as e:
        print(f"❌ Integration test error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_coordinator_tools():
    """Test Phase 3: Coordinator integration functionality."""
    print("\n🧪 Testing Coordinator Integration...")
    print("=" * 50)
    
    try:
        from instant_dashboard.agent import dashboard_agent
        from instant_dashboard.agent import (
            call_query_planner_agent, 
            call_bigquery_runner_agent, 
            execute_full_pipeline
        )
        
        print(f"✅ Coordinator agent imported successfully")
        print(f"   - Name: {dashboard_agent.name}")
        print(f"   - Total tools: {len(dashboard_agent.tools)}")
        
        # Check for expected Phase 3 tools
        expected_tools = [
            "call_db_agent",                # Phase 1
            "call_query_planner_agent",     # Phase 2  
            "call_bigquery_runner_agent",   # Phase 3
            "execute_full_pipeline"         # Phase 2+3
        ]
        
        tool_names = [tool.__name__ for tool in dashboard_agent.tools]
        
        for expected in expected_tools:
            if expected in tool_names:
                print(f"✅ {expected}")
            else:
                print(f"❌ {expected} - missing")
                return False
        
        print(f"✅ All Phase 3 integration tools available")
        print(f"✅ Coordinator ready for Phase 3 workflows")
        
        return True
        
    except Exception as e:
        print(f"❌ Coordinator test error: {e}")
        return False


def main():
    """Run all Phase 3 tests."""
    print("🎯 Phase 3 BigQueryRunner Test Suite")
    print("=" * 60)
    
    tests = [
        ("BigQueryRunner Imports", test_bigquery_runner_imports),
        ("SQL Validation & Execution", test_validate_query_execution),
        ("Query Plan Execution", test_execute_query_plan),
        ("Phase 2+3 Integration", test_phase_2_3_integration),
        ("Coordinator Integration", test_coordinator_tools),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print(f"{'='*60}")
        results.append(test_func())
    
    # Summary
    print(f"\n📊 Phase 3 Test Results:")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    for i, (test_name, _) in enumerate(tests):
        status = "✅ PASSED" if results[i] else "❌ FAILED"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"\n🎉 ALL PHASE 3 TESTS PASSED!")
        print(f"✅ BigQueryRunner Agent is fully functional")
        print(f"✅ Phase 2 + 3 integration working")
        print(f"✅ End-to-end pipeline: NL → Plans → SQL → Data")
        print(f"💡 Ready for Phase 4: ChartGenerator")
    else:
        print(f"\n⚠️ {total-passed} test(s) need attention")
        print(f"🔧 Review failed tests above")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 