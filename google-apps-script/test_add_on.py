#!/usr/bin/env python3
"""
Comprehensive Google Apps Script Add-on Testing Script

This script tests all endpoints that the Google Apps Script add-on uses
to ensure everything is working correctly before deploying.
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_QUERIES = [
    "show me sales data",
    "what are the top 5 products by sales?",
    "analyze sales trends by country",
    "create a chart of monthly sales",
    "show me recent sales data"
]

def test_health_check():
    """Test the basic health check endpoint."""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{API_BASE_URL}/")
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ Health check passed")
        print(f"   Status: {data.get('status')}")
        print(f"   Service: {data.get('service')}")
        print(f"   InstantDashboard Available: {data.get('instant_dashboard_available')}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_auth_endpoint():
    """Test the authentication endpoint."""
    print("\n🔐 Testing authentication...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/apps-script/auth",
            json={"email": "test@example.com"}
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get("success"):
            print("✅ Authentication test passed")
            print(f"   User ID: {data.get('user_id')}")
            print(f"   Email: {data.get('email')}")
            return True
        else:
            print(f"❌ Authentication failed: {data.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return False

def test_schema_endpoint():
    """Test the schema information endpoint."""
    print("\n🗃️  Testing schema endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/schema")
        response.raise_for_status()
        data = response.json()
        
        print("✅ Schema test passed")
        print(f"   Project ID: {data.get('project_id')}")
        print(f"   Dataset ID: {data.get('dataset_id')}")
        print(f"   Tables Available: {data.get('tables_available')}")
        print(f"   Schema Length: {len(data.get('schema', ''))}")
        return True
    except Exception as e:
        print(f"❌ Schema test failed: {e}")
        return False

def test_quick_query(query: str) -> bool:
    """Test a single quick query."""
    print(f"\n📊 Testing query: '{query}'")
    try:
        start_time = time.time()
        response = requests.post(
            f"{API_BASE_URL}/api/apps-script/quick-query",
            json={"question": query}
        )
        response.raise_for_status()
        data = response.json()
        execution_time = time.time() - start_time
        
        if data.get("success"):
            print(f"✅ Query successful ({execution_time:.1f}s)")
            print(f"   Summary: {data.get('summary')}")
            print(f"   Data rows: {len(data.get('data', []))}")
            print(f"   Charts recommended: {len(data.get('charts', {}).get('chart_recommendations', []))}")
            
            # Show sample data
            if data.get('data') and len(data['data']) > 0:
                sample_row = data['data'][0]
                print(f"   Sample row: {dict(list(sample_row.items())[:3])}...")
            
            return True
        else:
            print(f"❌ Query failed: {data.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Query test failed: {e}")
        return False

def test_demo_endpoint():
    """Test the demo endpoint."""
    print("\n🧪 Testing demo endpoint...")
    try:
        response = requests.post(f"{API_BASE_URL}/api/demo")
        response.raise_for_status()
        data = response.json()
        
        if data.get("success"):
            print("✅ Demo test passed")
            print(f"   Data rows: {len(data.get('data', []))}")
            print(f"   Summary: {data.get('summary')}")
            return True
        else:
            print(f"❌ Demo test failed")
            return False
    except Exception as e:
        print(f"❌ Demo test failed: {e}")
        return False

def test_pdf_analysis_endpoint():
    """Test the PDF analysis endpoint (placeholder)."""
    print("\n📄 Testing PDF analysis endpoint...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/apps-script/analyze-pdf",
            json={"content": "test pdf content"}
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get("success"):
            print("✅ PDF analysis test passed (placeholder)")
            print(f"   Analysis: {data.get('analysis', {}).get('summary')}")
            return True
        else:
            print(f"❌ PDF analysis test failed")
            return False
    except Exception as e:
        print(f"❌ PDF analysis test failed: {e}")
        return False

def run_comprehensive_tests():
    """Run all tests and provide a summary."""
    print("🚀 Starting Google Apps Script Add-on Comprehensive Testing")
    print("=" * 60)
    
    results = []
    
    # Basic connectivity tests
    results.append(("Health Check", test_health_check()))
    results.append(("Authentication", test_auth_endpoint()))
    results.append(("Schema Info", test_schema_endpoint()))
    results.append(("Demo Endpoint", test_demo_endpoint()))
    results.append(("PDF Analysis", test_pdf_analysis_endpoint()))
    
    # Query tests
    for i, query in enumerate(TEST_QUERIES):
        test_name = f"Query Test {i+1}"
        results.append((test_name, test_quick_query(query)))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/len(results)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 All tests passed! Your Google Apps Script add-on is ready!")
        print("📝 Next steps:")
        print("   1. Update Code.gs with correct API_BASE_URL")
        print("   2. Deploy to Google Apps Script")
        print("   3. Test in Google Docs")
    else:
        print(f"\n⚠️  {failed} tests failed. Please check your setup.")
        print("💡 Common issues:")
        print("   - Make sure simple_api_server.py is running")
        print("   - Check that InstantDashboard is properly configured")
        print("   - Verify BigQuery credentials are set")

if __name__ == "__main__":
    run_comprehensive_tests() 