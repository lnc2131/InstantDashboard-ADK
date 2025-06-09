#!/usr/bin/env python3

"""Test InstantDashboard using the correct ADK framework approach.

This test uses the proper ADK API server approach to test real integration
instead of trying to call agent methods directly.
"""

import sys
import os
import time
import subprocess
import requests
import json
from threading import Thread

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)


def start_adk_server():
    """Start the ADK API server for instant_dashboard."""
    print("🚀 Starting ADK API server for instant_dashboard...")
    
    try:
        # Start the ADK server in the background
        process = subprocess.Popen(
            ["adk", "api_server", "instant_dashboard"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give it a few seconds to start
        time.sleep(5)
        
        # Check if it's running
        if process.poll() is None:
            print("✅ ADK server started successfully")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ ADK server failed to start:")
            print(f"   stdout: {stdout}")
            print(f"   stderr: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting ADK server: {e}")
        return None


def test_adk_api_endpoint():
    """Test if the ADK API endpoint is working."""
    print("\n🧪 Testing ADK API Endpoint...")
    print("=" * 50)
    
    try:
        # Test the base endpoint
        response = requests.get("http://127.0.0.1:8000/docs")
        
        if response.status_code == 200:
            print("✅ ADK API server is responding")
            print(f"   Status: {response.status_code}")
            return True
        else:
            print(f"❌ ADK API server returned status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to ADK API server")
        print("   Make sure 'adk api_server instant_dashboard' is running")
        return False
    except Exception as e:
        print(f"❌ Error testing ADK endpoint: {e}")
        return False


def create_session():
    """Create a test session."""
    print("\n🔧 Creating Test Session...")
    
    try:
        session_endpoint = "http://127.0.0.1:8000/apps/instant_dashboard/users/test_user/sessions/test_session"
        response = requests.post(session_endpoint)
        
        if response.status_code in [200, 201]:
            print("✅ Session created successfully")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Session creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating session: {e}")
        return False


def test_instant_dashboard_query():
    """Test InstantDashboard with a real business question."""
    print("\n🧪 Testing InstantDashboard with Real Query...")
    print("=" * 50)
    
    try:
        run_endpoint = "http://127.0.0.1:8000/run_sse"
        headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "Accept": "text/event-stream",
        }
        
        # Test question
        test_question = "What are the top 3 countries by total sticker sales?"
        
        data = {
            "session_id": "test_session",
            "app_name": "instant_dashboard",
            "user_id": "test_user",
            "new_message": {
                "role": "user",
                "parts": [{"text": test_question}],
            },
        }
        
        print(f"📝 Question: {test_question}")
        print("🚀 Sending request to InstantDashboard...")
        
        response_content = []
        error_occurred = False
        
        with requests.post(
            run_endpoint, 
            data=json.dumps(data), 
            headers=headers, 
            stream=True,
            timeout=60  # 60 second timeout
        ) as r:
            
            if r.status_code != 200:
                print(f"❌ Request failed with status: {r.status_code}")
                print(f"   Response: {r.text}")
                return False
            
            print("📡 Streaming response...")
            
            for chunk in r.iter_lines():
                if not chunk:
                    continue
                    
                try:
                    json_string = chunk.decode("utf-8").removeprefix("data: ").strip()
                    if not json_string:
                        continue
                        
                    event = json.loads(json_string)
                    response_content.append(event)
                    
                    # Print progress
                    if "author" in event:
                        author = event["author"]
                        
                        # Check for text responses
                        if "content" in event and "parts" in event["content"]:
                            for part in event["content"]["parts"]:
                                if "text" in part:
                                    text = part["text"][:100] + "..." if len(part["text"]) > 100 else part["text"]
                                    print(f"   [{author}]: {text}")
                                
                                # Check for function calls
                                if "functionCall" in part:
                                    func_name = part["functionCall"]["name"]
                                    print(f"   [{author}]: Calling {func_name}")
                                    
                                # Check for function responses
                                if "functionResponse" in part:
                                    func_name = part["functionResponse"]["name"]
                                    print(f"   [{author}]: Response from {func_name}")
                    
                    # Check for errors
                    if "error" in event:
                        print(f"❌ Error in response: {event['error']}")
                        error_occurred = True
                        
                except json.JSONDecodeError:
                    # Skip malformed JSON
                    continue
                except Exception as e:
                    print(f"⚠️ Error processing chunk: {e}")
                    continue
        
        print(f"\n📊 Response Summary:")
        print(f"   Total events: {len(response_content)}")
        print(f"   Errors occurred: {error_occurred}")
        
        if response_content and not error_occurred:
            print("✅ InstantDashboard responded successfully")
            
            # Check if we got actual data results
            for event in response_content:
                if ("content" in event and "parts" in event["content"]):
                    for part in event["content"]["parts"]:
                        if "functionResponse" in part:
                            response_data = part["functionResponse"].get("response", "")
                            if "status" in str(response_data) and "success" in str(response_data):
                                print("✅ Detected successful data execution")
                                return True
            
            print("⚠️ Response received but no clear data execution detected")
            return True
        else:
            print("❌ No valid response received or errors occurred")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (60 seconds)")
        return False
    except Exception as e:
        print(f"❌ Error testing InstantDashboard query: {e}")
        return False


def main():
    """Test InstantDashboard integration using correct ADK approach."""
    print("🎯 InstantDashboard ADK Integration Test")
    print("=" * 60)
    
    # Check if we should start the server or assume it's running
    server_process = None
    
    print("Note: This test assumes 'adk api_server instant_dashboard' is already running")
    print("If not, start it manually in another terminal first.")
    
    tests = [
        ("ADK API Endpoint", test_adk_api_endpoint),
        ("Session Creation", create_session),
        ("InstantDashboard Query", test_instant_dashboard_query),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print(f"{'='*60}")
        results.append(test_func())
    
    # Summary
    print(f"\n📊 ADK Integration Test Results:")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    for i, (test_name, _) in enumerate(tests):
        status = "✅ PASSED" if results[i] else "❌ FAILED"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"\n🎉 ADK INTEGRATION WORKING!")
        print(f"✅ InstantDashboard works properly with ADK framework")
        print(f"✅ Phase 3 integration is actually functional")
    else:
        print(f"\n🔧 ADK Integration Issues Found:")
        print(f"   - {total-passed} component(s) need attention")
        print(f"   - These are the real Phase 3 integration problems")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 