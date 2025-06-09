#!/usr/bin/env python3

"""Convenience script to run all InstantDashboard tests and demos."""

import sys
import os
import argparse

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(parent_dir)


def run_foundation_tests():
    """Run the comprehensive foundation and phase tests."""
    print("🧪 Running Foundation & Phase Tests...")
    print("=" * 50)
    
    try:
        # Import and run the test suite
        import subprocess
        result = subprocess.run([
            sys.executable, 
            os.path.join(current_dir, "test_foundation.py")
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running foundation tests: {e}")
        return False


def run_phase_2_demo():
    """Run the Phase 2 QueryPlannerAgent demo."""
    print("\n🚀 Running Phase 2 Demo...")
    print("=" * 50)
    
    try:
        import subprocess
        result = subprocess.run([
            sys.executable,
            os.path.join(current_dir, "test_phase_2_demo.py")
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running Phase 2 demo: {e}")
        return False


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run InstantDashboard tests and demos")
    parser.add_argument("--foundation", action="store_true", help="Run foundation tests only")
    parser.add_argument("--demo", action="store_true", help="Run Phase 2 demo only")
    parser.add_argument("--all", action="store_true", help="Run all tests and demos (default)")
    
    args = parser.parse_args()
    
    # Default to running all if no specific option chosen
    if not (args.foundation or args.demo):
        args.all = True
    
    print("🚀 InstantDashboard Test Runner")
    print("=" * 50)
    print(f"📍 Working directory: {os.getcwd()}")
    print(f"📁 Test directory: {current_dir}")
    
    results = []
    
    if args.foundation or args.all:
        results.append(("Foundation Tests", run_foundation_tests()))
    
    if args.demo or args.all:
        results.append(("Phase 2 Demo", run_phase_2_demo()))
    
    # Summary
    print("\n📊 Test Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} test suites passed")
    
    if passed == total:
        print("\n🎉 All test suites completed successfully!")
        print("💡 InstantDashboard is ready for development")
    else:
        print(f"\n⚠️  {total - passed} test suite(s) failed")
        print("🔧 Please check the output above for details")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 