#!/usr/bin/env python3

"""Debug script to test imports."""

import sys
import os

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

print("🔍 Debugging Import Issues...")
print("=" * 40)

# Test 1: Basic instant_dashboard import
try:
    import instant_dashboard
    print("✅ instant_dashboard import successful")
except Exception as e:
    print(f"❌ instant_dashboard import failed: {e}")

# Test 2: sub_agents package import
try:
    from instant_dashboard import sub_agents
    print("✅ instant_dashboard.sub_agents import successful")
except Exception as e:
    print(f"❌ instant_dashboard.sub_agents import failed: {e}")

# Test 3: query_planner module import
try:
    from instant_dashboard.sub_agents import query_planner
    print("✅ instant_dashboard.sub_agents.query_planner import successful")
except Exception as e:
    print(f"❌ instant_dashboard.sub_agents.query_planner import failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: specific function import
try:
    from instant_dashboard.sub_agents.query_planner import generate_query_plan
    print("✅ generate_query_plan function import successful")
except Exception as e:
    print(f"❌ generate_query_plan function import failed: {e}")
    import traceback
    traceback.print_exc()

print("\n🔍 Module paths:")
print(f"instant_dashboard location: {instant_dashboard.__file__ if 'instant_dashboard' in locals() else 'Not imported'}")

print("\n🔍 Available files in sub_agents:")
import os
sub_agents_path = os.path.join(current_dir, "instant_dashboard", "sub_agents")
if os.path.exists(sub_agents_path):
    files = os.listdir(sub_agents_path)
    for file in files:
        print(f"   - {file}")
else:
    print("   sub_agents directory not found") 