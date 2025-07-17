#!/usr/bin/env python3
"""
Comprehensive Test Runner for Al Essa Kuwait Virtual Assistant
Demonstrates comprehensive testing framework with 95% accuracy targets
"""

import sys
import os
import time
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Main function to run comprehensive tests"""
    print("🚀 AL ESSA KUWAIT VIRTUAL ASSISTANT - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print("Target: Achieve 95% accuracy across all test scenarios")
    print("Framework: Custom testing framework with mock services")
    print("Scope: Agent routing, tool execution, response quality")
    print("=" * 80)
    print()
    
    try:
        # Import and run the comprehensive test framework
        from tests.test_framework.test_executor import run_comprehensive_test_suite
        
        print("🔧 Initializing test framework...")
        start_time = time.time()
        
        # Run the comprehensive test suite
        summary = run_comprehensive_test_suite()
        
        execution_time = time.time() - start_time
        
        print("\n" + "=" * 80)
        print("📊 FINAL RESULTS SUMMARY")
        print("=" * 80)
        
        # Display key metrics
        print(f"🎯 Target Accuracy: 95%")
        print(f"📈 Achieved Accuracy: {summary.overall_accuracy:.2%}")
        print(f"✅ Tests Passed: {summary.passed_tests}/{summary.total_tests}")
        print(f"⏱️  Execution Time: {execution_time:.2f} seconds")
        print(f"⚡ Average Response Time: {summary.average_response_time:.3f} seconds")
        
        print("\n📋 ACCURACY BY CATEGORY:")
        for category, accuracy in summary.accuracy_by_type.items():
            status = "✅" if accuracy >= 0.95 else "⚠️" if accuracy >= 0.80 else "❌"
            print(f"  {status} {category.replace('_', ' ').title()}: {accuracy:.2%}")
        
        print("\n🎚️  ACCURACY BY DIFFICULTY:")
        for difficulty, accuracy in summary.accuracy_by_difficulty.items():
            status = "✅" if accuracy >= 0.95 else "⚠️" if accuracy >= 0.80 else "❌"
            print(f"  {status} Level {difficulty}: {accuracy:.2%}")
        
        # Overall assessment
        print("\n🏆 OVERALL ASSESSMENT:")
        if summary.overall_accuracy >= 0.95:
            print("  🎉 TARGET ACHIEVED! Excellent performance across all scenarios.")
            print("  🌟 System ready for production deployment.")
            return_code = 0
        elif summary.overall_accuracy >= 0.85:
            print("  ⚠️  Good performance but needs improvement to reach 95% target.")
            print("  🔧 Focus on areas with lower accuracy scores.")
            return_code = 1
        else:
            print("  ❌ Performance below acceptable threshold.")
            print("  🚨 Significant improvements needed before deployment.")
            return_code = 2
        
        # Recommendations
        print("\n💡 NEXT STEPS:")
        if summary.overall_accuracy < 0.95:
            worst_category = min(summary.accuracy_by_type.items(), key=lambda x: x[1])
            print(f"  1. Focus on improving {worst_category[0].replace('_', ' ')} accuracy")
            print(f"  2. Review agent routing logic and prompts")
            print(f"  3. Enhance tool integration and error handling")
            print(f"  4. Expand training data for problematic scenarios")
        else:
            print(f"  1. Monitor performance to maintain quality")
            print(f"  2. Gradually expand test coverage")
            print(f"  3. Consider real-world user testing")
            print(f"  4. Implement continuous testing pipeline")
        
        print("\n" + "=" * 80)
        print("🔗 Test results saved to JSON file for detailed analysis")
        print("📚 Full report available in generated documentation")
        print("=" * 80)
        
        return return_code
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("🔧 Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        return 3
        
    except Exception as e:
        print(f"💥 Unexpected Error: {e}")
        print("🐛 Please check the test framework implementation")
        return 4

def run_quick_demo():
    """Run a quick demonstration of the testing framework"""
    print("🚀 QUICK DEMONSTRATION - AL ESSA TEST FRAMEWORK")
    print("=" * 60)
    
    try:
        from tests.test_framework.test_data_generator import TestDataGenerator, get_golden_test_cases
        from tests.test_framework.test_executor import TestExecutor
        
        # Generate a small set of test scenarios
        generator = TestDataGenerator()
        print("📊 Generating test scenarios...")
        
        # Get golden test cases (should always pass)
        golden_cases = get_golden_test_cases()
        print(f"✨ Golden test cases: {len(golden_cases)}")
        
        # Generate some additional scenarios
        product_scenarios = generator.generate_product_search_scenarios(5)
        medical_scenarios = generator.generate_medical_inquiry_scenarios(3)
        emergency_scenarios = generator.generate_emergency_scenarios(2)
        
        all_scenarios = golden_cases + product_scenarios + medical_scenarios + emergency_scenarios
        print(f"📋 Total scenarios: {len(all_scenarios)}")
        
        # Execute the test scenarios
        print("\n🔄 Executing test scenarios...")
        executor = TestExecutor(use_mocks=True)
        
        results = []
        for i, scenario in enumerate(all_scenarios):
            print(f"  Running test {i+1}/{len(all_scenarios)}: {scenario.query[:50]}...")
            result = executor.execute_scenario(scenario)
            results.append(result)
        
        # Calculate summary statistics
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r.success)
        overall_accuracy = sum(r.accuracy_score for r in results) / total_tests
        avg_response_time = sum(r.response_time for r in results) / total_tests
        
        print("\n📊 QUICK DEMO RESULTS:")
        print(f"  Tests Executed: {total_tests}")
        print(f"  Success Rate: {successful_tests/total_tests:.2%}")
        print(f"  Overall Accuracy: {overall_accuracy:.2%}")
        print(f"  Average Response Time: {avg_response_time:.3f}s")
        
        # Show some example results
        print("\n🔍 SAMPLE TEST RESULTS:")
        for i, result in enumerate(results[:3]):
            status = "✅" if result.success else "❌"
            print(f"  {status} Test {i+1}: '{result.scenario.query}'")
            print(f"     Expected: {result.scenario.expected_agent.value}")
            print(f"     Actual: {result.actual_agent}")
            print(f"     Accuracy: {result.accuracy_score:.2%}")
        
        if overall_accuracy >= 0.90:
            print("\n🎉 Demo shows excellent performance! Framework is working well.")
        else:
            print("\n⚠️  Demo shows room for improvement in the testing framework.")
            
        return 0
        
    except Exception as e:
        print(f"❌ Demo Error: {e}")
        return 1

if __name__ == "__main__":
    print("Al Essa Kuwait Virtual Assistant - Test Framework")
    print("Choose an option:")
    print("1. Run full comprehensive test suite")
    print("2. Run quick demo")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        exit_code = main()
        sys.exit(exit_code)
    elif choice == "2":
        exit_code = run_quick_demo()
        sys.exit(exit_code)
    elif choice == "3":
        print("👋 Goodbye!")
        sys.exit(0)
    else:
        print("❌ Invalid choice. Please run the script again.")
        sys.exit(1)