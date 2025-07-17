"""
Test Runner for Comprehensive Chatbot Testing
Executes test suites and provides analytics for iterative improvement.
"""

import pytest
import json
import time
import statistics
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

# Import test modules
from comprehensive_test_suite import (
    TestComprehensiveScenarios,
    TestAccuracyMetrics,
    TestEdgeCasesAndErrorHandling,
    TestPerformanceAndScalability
)

class TestRunner:
    """Test runner for comprehensive chatbot testing."""
    
    def __init__(self):
        """Initialize the test runner."""
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "test_suites": {},
            "overall_metrics": {},
            "improvement_suggestions": []
        }
        self.output_dir = Path("test_results")
        self.output_dir.mkdir(exist_ok=True)
    
    def run_comprehensive_suite(self) -> Dict[str, Any]:
        """Run the comprehensive test suite."""
        print("🚀 Starting Comprehensive Test Suite...")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run each test class
        test_classes = [
            ("Comprehensive Scenarios", TestComprehensiveScenarios),
            ("Accuracy Metrics", TestAccuracyMetrics),
            ("Edge Cases", TestEdgeCasesAndErrorHandling),
            ("Performance", TestPerformanceAndScalability)
        ]
        
        for suite_name, test_class in test_classes:
            print(f"\n📋 Running {suite_name}...")
            suite_start = time.time()
            
            # Run the test class
            suite_results = self._run_test_class(test_class)
            
            suite_time = time.time() - suite_start
            suite_results["execution_time"] = suite_time
            
            self.results["test_suites"][suite_name] = suite_results
            
            # Print suite summary
            self._print_suite_summary(suite_name, suite_results)
        
        total_time = time.time() - start_time
        self.results["overall_metrics"]["total_execution_time"] = total_time
        
        # Calculate overall metrics
        self._calculate_overall_metrics()
        
        # Generate improvement suggestions
        self._generate_improvement_suggestions()
        
        # Save results
        self._save_results()
        
        # Print final summary
        self._print_final_summary()
        
        return self.results
    
    def _run_test_class(self, test_class) -> Dict[str, Any]:
        """Run a specific test class and collect results."""
        results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "test_details": [],
            "accuracy_metrics": {}
        }
        
        # Create test instance
        test_instance = test_class()
        
        # Get all test methods
        test_methods = [method for method in dir(test_instance) 
                       if method.startswith('test_') and callable(getattr(test_instance, method))]
        
        for method_name in test_methods:
            method = getattr(test_instance, method_name)
            
            # Check if it's a parametrized test
            if hasattr(method, 'pytestmark'):
                # Handle parametrized tests
                for param in self._get_test_parameters(method):
                    test_result = self._run_single_test(test_instance, method, param)
                    results["test_details"].append(test_result)
                    results["total_tests"] += 1
                    
                    if test_result["status"] == "passed":
                        results["passed"] += 1
                    elif test_result["status"] == "failed":
                        results["failed"] += 1
                    else:
                        results["errors"] += 1
            else:
                # Regular test
                test_result = self._run_single_test(test_instance, method)
                results["test_details"].append(test_result)
                results["total_tests"] += 1
                
                if test_result["status"] == "passed":
                    results["passed"] += 1
                elif test_result["status"] == "failed":
                    results["failed"] += 1
                else:
                    results["errors"] += 1
        
        # Calculate accuracy metrics for this suite
        if results["total_tests"] > 0:
            results["accuracy_metrics"] = {
                "pass_rate": (results["passed"] / results["total_tests"]) * 100,
                "failure_rate": (results["failed"] / results["total_tests"]) * 100,
                "error_rate": (results["errors"] / results["total_tests"]) * 100
            }
        
        return results
    
    def _run_single_test(self, test_instance, method, param=None) -> Dict[str, Any]:
        """Run a single test method."""
        test_name = method.__name__
        if param:
            test_name += f"[{param}]"
        
        result = {
            "test_name": test_name,
            "status": "unknown",
            "execution_time": 0,
            "error_message": None,
            "details": {}
        }
        
        try:
            # Set up test
            if hasattr(test_instance, 'setup_method'):
                test_instance.setup_method()
            
            # Run test
            start_time = time.time()
            
            if param:
                method(test_instance, param)
            else:
                method(test_instance)
            
            end_time = time.time()
            
            result["status"] = "passed"
            result["execution_time"] = end_time - start_time
            
        except AssertionError as e:
            result["status"] = "failed"
            result["error_message"] = str(e)
        except Exception as e:
            result["status"] = "error"
            result["error_message"] = str(e)
        finally:
            # Clean up test
            if hasattr(test_instance, 'teardown_method'):
                test_instance.teardown_method()
        
        return result
    
    def _get_test_parameters(self, method):
        """Get parameters for parametrized tests."""
        # This is a simplified version - in practice, you'd need to extract
        # the actual parameters from the pytest.mark.parametrize decorator
        if "scenario" in method.__name__:
            # Return sample parameters for demonstration
            return ["basic", "intermediate", "advanced"]
        return []
    
    def _print_suite_summary(self, suite_name: str, results: Dict[str, Any]):
        """Print summary for a test suite."""
        total = results["total_tests"]
        passed = results["passed"]
        failed = results["failed"]
        errors = results["errors"]
        
        if total > 0:
            pass_rate = (passed / total) * 100
            print(f"  ✅ Passed: {passed}/{total} ({pass_rate:.1f}%)")
            print(f"  ❌ Failed: {failed}/{total}")
            print(f"  ⚠️  Errors: {errors}/{total}")
            print(f"  ⏱️  Time: {results['execution_time']:.2f}s")
        else:
            print("  ⚠️  No tests executed")
    
    def _calculate_overall_metrics(self):
        """Calculate overall metrics across all test suites."""
        total_tests = 0
        total_passed = 0
        total_failed = 0
        total_errors = 0
        execution_times = []
        
        for suite_name, suite_results in self.results["test_suites"].items():
            total_tests += suite_results["total_tests"]
            total_passed += suite_results["passed"]
            total_failed += suite_results["failed"]
            total_errors += suite_results["errors"]
            execution_times.append(suite_results["execution_time"])
        
        if total_tests > 0:
            self.results["overall_metrics"] = {
                "total_tests": total_tests,
                "total_passed": total_passed,
                "total_failed": total_failed,
                "total_errors": total_errors,
                "overall_pass_rate": (total_passed / total_tests) * 100,
                "overall_failure_rate": (total_failed / total_tests) * 100,
                "overall_error_rate": (total_errors / total_tests) * 100,
                "average_execution_time": statistics.mean(execution_times) if execution_times else 0,
                "total_execution_time": sum(execution_times)
            }
    
    def _generate_improvement_suggestions(self):
        """Generate improvement suggestions based on test results."""
        suggestions = []
        
        overall_metrics = self.results["overall_metrics"]
        
        # Check overall pass rate
        if overall_metrics.get("overall_pass_rate", 0) < 95:
            suggestions.append({
                "category": "accuracy",
                "priority": "high",
                "suggestion": f"Overall pass rate is {overall_metrics.get('overall_pass_rate', 0):.1f}%, target is 95%. Focus on fixing failing tests.",
                "impact": "critical"
            })
        
        # Check specific test suites
        for suite_name, suite_results in self.results["test_suites"].items():
            if suite_results.get("accuracy_metrics", {}).get("pass_rate", 0) < 90:
                suggestions.append({
                    "category": "test_suite",
                    "priority": "medium",
                    "suggestion": f"{suite_name} has low pass rate ({suite_results['accuracy_metrics']['pass_rate']:.1f}%). Review and fix failing tests.",
                    "impact": "moderate"
                })
        
        # Check performance
        avg_time = overall_metrics.get("average_execution_time", 0)
        if avg_time > 2.0:  # More than 2 seconds average
            suggestions.append({
                "category": "performance",
                "priority": "medium",
                "suggestion": f"Average test execution time is {avg_time:.2f}s. Consider optimizing slow tests.",
                "impact": "moderate"
            })
        
        # Check error rates
        error_rate = overall_metrics.get("overall_error_rate", 0)
        if error_rate > 5:
            suggestions.append({
                "category": "stability",
                "priority": "high",
                "suggestion": f"High error rate ({error_rate:.1f}%). Fix test setup and teardown issues.",
                "impact": "high"
            })
        
        self.results["improvement_suggestions"] = suggestions
    
    def _save_results(self):
        """Save test results to files."""
        # Save detailed results
        results_file = self.output_dir / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        # Save summary
        summary_file = self.output_dir / "latest_summary.json"
        summary = {
            "timestamp": self.results["timestamp"],
            "overall_metrics": self.results["overall_metrics"],
            "improvement_suggestions": self.results["improvement_suggestions"]
        }
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {results_file}")
        print(f"📊 Summary saved to: {summary_file}")
    
    def _print_final_summary(self):
        """Print final test summary."""
        print("\n" + "=" * 60)
        print("🎯 FINAL TEST SUMMARY")
        print("=" * 60)
        
        metrics = self.results["overall_metrics"]
        
        print(f"📈 Overall Pass Rate: {metrics.get('overall_pass_rate', 0):.1f}%")
        print(f"📊 Total Tests: {metrics.get('total_tests', 0)}")
        print(f"✅ Passed: {metrics.get('total_passed', 0)}")
        print(f"❌ Failed: {metrics.get('total_failed', 0)}")
        print(f"⚠️  Errors: {metrics.get('total_errors', 0)}")
        print(f"⏱️  Total Time: {metrics.get('total_execution_time', 0):.2f}s")
        print(f"⚡ Avg Time: {metrics.get('average_execution_time', 0):.2f}s")
        
        # Print improvement suggestions
        if self.results["improvement_suggestions"]:
            print(f"\n🔧 IMPROVEMENT SUGGESTIONS:")
            for i, suggestion in enumerate(self.results["improvement_suggestions"], 1):
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(suggestion["priority"], "⚪")
                print(f"  {i}. {priority_emoji} {suggestion['suggestion']}")
        
        # Check if we've achieved 95% accuracy
        pass_rate = metrics.get('overall_pass_rate', 0)
        if pass_rate >= 95:
            print(f"\n🎉 SUCCESS! Achieved {pass_rate:.1f}% accuracy (target: 95%)")
        else:
            print(f"\n📈 PROGRESS: Current accuracy {pass_rate:.1f}% (target: 95%)")
            print("   Continue iterating to improve accuracy.")

def run_iterative_improvement(iterations: int = 5):
    """Run iterative improvement process."""
    print("🔄 Starting Iterative Improvement Process")
    print("=" * 60)
    
    improvement_history = []
    
    for iteration in range(1, iterations + 1):
        print(f"\n🔄 ITERATION {iteration}/{iterations}")
        print("-" * 40)
        
        # Run tests
        runner = TestRunner()
        results = runner.run_comprehensive_suite()
        
        # Store results
        improvement_history.append({
            "iteration": iteration,
            "timestamp": results["timestamp"],
            "metrics": results["overall_metrics"],
            "suggestions": results["improvement_suggestions"]
        })
        
        # Check if we've achieved target accuracy
        pass_rate = results["overall_metrics"].get("overall_pass_rate", 0)
        if pass_rate >= 95:
            print(f"\n🎉 TARGET ACHIEVED! Accuracy: {pass_rate:.1f}%")
            break
        
        # Apply improvements based on suggestions
        if iteration < iterations:
            print(f"\n🔧 Applying improvements for next iteration...")
            apply_improvements(results["improvement_suggestions"])
    
    # Save improvement history
    history_file = Path("test_results") / "improvement_history.json"
    with open(history_file, 'w') as f:
        json.dump(improvement_history, f, indent=2, default=str)
    
    print(f"\n📈 Improvement history saved to: {history_file}")
    
    return improvement_history

def apply_improvements(suggestions: List[Dict[str, Any]]):
    """Apply improvements based on test suggestions."""
    # This is a placeholder for actual improvement logic
    # In practice, you would implement specific fixes based on the suggestions
    
    for suggestion in suggestions:
        category = suggestion["category"]
        priority = suggestion["priority"]
        
        print(f"  🔧 {priority.upper()}: {suggestion['suggestion']}")
        
        # Example improvements (these would be actual code changes)
        if category == "accuracy":
            # Improve agent routing logic
            pass
        elif category == "performance":
            # Optimize slow operations
            pass
        elif category == "stability":
            # Fix error handling
            pass

if __name__ == "__main__":
    # Run single test suite
    print("Running single test suite...")
    runner = TestRunner()
    results = runner.run_comprehensive_suite()
    
    # Or run iterative improvement
    # print("Running iterative improvement...")
    # history = run_iterative_improvement(iterations=3)