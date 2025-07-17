"""
Enhanced Comprehensive Test Suite for Al Essa Kuwait Virtual Assistant
Addresses core issues and implements 95% accuracy testing framework
"""

import sys
import os
import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_framework import (
    TestDataGenerator, TestExecutor, TestScenario, ExpectedAgent, 
    get_golden_test_cases, setup_mock_services
)

class TestEnhancedSuite:
    """Enhanced test suite with comprehensive coverage and mock services"""
    
    @pytest.fixture(autouse=True)
    def setup_test_environment(self):
        """Setup mock services and test environment"""
        # Mock the LLM to avoid OpenAI API key issues
        with patch('app.core.llm.llm') as mock_llm:
            mock_llm.invoke.return_value = Mock(content="Mocked LLM response for testing")
            
            # Mock analytics to avoid KeyError issues
            with patch('app.core.analytics.analytics_manager') as mock_analytics:
                mock_analytics.record_query = Mock()
                mock_analytics.system_metrics.error_counts = {}
                
                # Setup comprehensive mock services
                setup_mock_services()
                yield
    
    def test_agent_routing_accuracy(self):
        """Test agent routing accuracy with golden test cases"""
        generator = TestDataGenerator()
        executor = TestExecutor(use_mocks=True)
        
        # Get golden test cases that should always pass
        golden_cases = get_golden_test_cases()
        
        results = []
        for scenario in golden_cases:
            result = executor.execute_scenario(scenario)
            results.append(result)
        
        # Calculate routing accuracy
        correct_routing = sum(1 for r in results if r.actual_agent == r.scenario.expected_agent.value)
        routing_accuracy = correct_routing / len(results)
        
        print(f"\n🎯 Agent Routing Accuracy: {routing_accuracy:.2%}")
        print(f"   Correct: {correct_routing}/{len(results)}")
        
        # Should achieve >95% on golden cases
        assert routing_accuracy >= 0.95, f"Expected ≥95% routing accuracy, got {routing_accuracy:.2%}"
    
    def test_product_search_scenarios(self):
        """Test product search functionality"""
        generator = TestDataGenerator()
        executor = TestExecutor(use_mocks=True)
        
        # Generate product search scenarios
        scenarios = generator.generate_product_search_scenarios(20)
        
        results = []
        for scenario in scenarios:
            result = executor.execute_scenario(scenario)
            results.append(result)
        
        # Calculate success rate
        success_rate = sum(1 for r in results if r.success) / len(results)
        avg_accuracy = sum(r.accuracy_score for r in results) / len(results)
        
        print(f"\n🛍️  Product Search Results:")
        print(f"   Success Rate: {success_rate:.2%}")
        print(f"   Average Accuracy: {avg_accuracy:.2%}")
        
        # Should achieve >90% success rate for product searches
        assert success_rate >= 0.90, f"Expected ≥90% success rate, got {success_rate:.2%}"
        assert avg_accuracy >= 0.85, f"Expected ≥85% accuracy, got {avg_accuracy:.2%}"
    
    def test_medical_inquiry_scenarios(self):
        """Test medical inquiry handling"""
        generator = TestDataGenerator()
        executor = TestExecutor(use_mocks=True)
        
        # Generate medical scenarios
        scenarios = generator.generate_medical_inquiry_scenarios(15)
        
        results = []
        for scenario in scenarios:
            result = executor.execute_scenario(scenario)
            results.append(result)
        
        # Calculate medical routing accuracy
        medical_accuracy = sum(1 for r in results if r.actual_agent == "doctor") / len(results)
        avg_accuracy = sum(r.accuracy_score for r in results) / len(results)
        
        print(f"\n🏥 Medical Inquiry Results:")
        print(f"   Medical Routing: {medical_accuracy:.2%}")
        print(f"   Average Accuracy: {avg_accuracy:.2%}")
        
        # Medical queries should route to doctor agent with high accuracy
        assert medical_accuracy >= 0.85, f"Expected ≥85% medical routing, got {medical_accuracy:.2%}"
        assert avg_accuracy >= 0.80, f"Expected ≥80% accuracy, got {avg_accuracy:.2%}"
    
    def test_emergency_scenarios_100_percent(self):
        """Test emergency scenarios - must achieve 100% accuracy"""
        generator = TestDataGenerator()
        executor = TestExecutor(use_mocks=True)
        
        # Generate emergency scenarios
        scenarios = generator.generate_emergency_scenarios(5)
        
        results = []
        for scenario in scenarios:
            result = executor.execute_scenario(scenario)
            results.append(result)
        
        # Emergency scenarios must have 100% accuracy
        emergency_accuracy = sum(1 for r in results if r.actual_agent == "doctor" and r.success) / len(results)
        
        print(f"\n🚨 Emergency Scenario Results:")
        print(f"   Emergency Accuracy: {emergency_accuracy:.2%}")
        
        # Emergency scenarios are critical - must be 100%
        assert emergency_accuracy == 1.0, f"Emergency scenarios must be 100% accurate, got {emergency_accuracy:.2%}"
    
    def test_conversation_context_scenarios(self):
        """Test conversation context handling"""
        generator = TestDataGenerator()
        executor = TestExecutor(use_mocks=True)
        
        # Generate context-aware scenarios
        scenarios = generator.generate_conversation_context_scenarios(10)
        
        results = []
        for scenario in scenarios:
            result = executor.execute_scenario(scenario)
            results.append(result)
        
        # Calculate context handling accuracy
        context_accuracy = sum(r.accuracy_score for r in results) / len(results)
        
        print(f"\n💬 Conversation Context Results:")
        print(f"   Context Accuracy: {context_accuracy:.2%}")
        
        # Context handling should be reasonably accurate
        assert context_accuracy >= 0.75, f"Expected ≥75% context accuracy, got {context_accuracy:.2%}"
    
    def test_mixed_ambiguous_scenarios(self):
        """Test mixed and ambiguous scenarios"""
        generator = TestDataGenerator()
        executor = TestExecutor(use_mocks=True)
        
        # Generate mixed scenarios
        scenarios = generator.generate_mixed_scenarios(8)
        
        results = []
        for scenario in scenarios:
            result = executor.execute_scenario(scenario)
            results.append(result)
        
        # Calculate handling of ambiguous cases
        success_rate = sum(1 for r in results if r.success) / len(results)
        
        print(f"\n🔀 Mixed/Ambiguous Results:")
        print(f"   Success Rate: {success_rate:.2%}")
        
        # Ambiguous cases should still be handled reasonably well
        assert success_rate >= 0.70, f"Expected ≥70% success on ambiguous cases, got {success_rate:.2%}"
    
    def test_edge_cases_and_error_handling(self):
        """Test edge cases and error handling"""
        generator = TestDataGenerator()
        executor = TestExecutor(use_mocks=True)
        
        # Generate edge case scenarios
        scenarios = generator.generate_edge_case_scenarios(10)
        
        results = []
        for scenario in scenarios:
            result = executor.execute_scenario(scenario)
            results.append(result)
        
        # Edge cases should be handled gracefully (no crashes)
        no_errors = sum(1 for r in results if r.error_message is None) / len(results)
        
        print(f"\n⚠️  Edge Case Results:")
        print(f"   No Errors: {no_errors:.2%}")
        
        # Should handle edge cases without errors
        assert no_errors >= 0.80, f"Expected ≥80% error-free handling, got {no_errors:.2%}"
    
    def test_performance_benchmarks(self):
        """Test performance benchmarks"""
        generator = TestDataGenerator()
        executor = TestExecutor(use_mocks=True)
        
        # Get a sample of scenarios for performance testing
        scenarios = get_golden_test_cases()[:10]
        
        start_time = time.time()
        results = []
        for scenario in scenarios:
            result = executor.execute_scenario(scenario)
            results.append(result)
        
        total_time = time.time() - start_time
        avg_response_time = total_time / len(scenarios)
        
        print(f"\n⚡ Performance Results:")
        print(f"   Average Response Time: {avg_response_time:.3f}s")
        print(f"   Total Test Time: {total_time:.2f}s")
        
        # Response time should be reasonable (under 2 seconds average for mocked tests)
        assert avg_response_time < 2.0, f"Expected <2s response time, got {avg_response_time:.3f}s"
    
    def test_overall_system_accuracy(self):
        """Test overall system accuracy across all scenario types"""
        generator = TestDataGenerator()
        executor = TestExecutor(use_mocks=True)
        
        # Comprehensive test across all scenario types
        all_scenarios = []
        all_scenarios.extend(get_golden_test_cases())
        all_scenarios.extend(generator.generate_product_search_scenarios(15))
        all_scenarios.extend(generator.generate_medical_inquiry_scenarios(10))
        all_scenarios.extend(generator.generate_emergency_scenarios(3))
        all_scenarios.extend(generator.generate_conversation_context_scenarios(8))
        all_scenarios.extend(generator.generate_mixed_scenarios(5))
        all_scenarios.extend(generator.generate_edge_case_scenarios(4))
        
        results = []
        for scenario in all_scenarios:
            result = executor.execute_scenario(scenario)
            results.append(result)
        
        # Calculate overall metrics
        overall_accuracy = sum(r.accuracy_score for r in results) / len(results)
        success_rate = sum(1 for r in results if r.success) / len(results)
        
        print(f"\n🏆 OVERALL SYSTEM RESULTS:")
        print(f"   Total Scenarios Tested: {len(results)}")
        print(f"   Overall Accuracy: {overall_accuracy:.2%}")
        print(f"   Success Rate: {success_rate:.2%}")
        print(f"   Target: 95% Accuracy")
        
        # Calculate accuracy by scenario type
        accuracy_by_type = {}
        for result in results:
            scenario_type = result.scenario.query_type.value
            if scenario_type not in accuracy_by_type:
                accuracy_by_type[scenario_type] = []
            accuracy_by_type[scenario_type].append(result.accuracy_score)
        
        print(f"\n📊 ACCURACY BY SCENARIO TYPE:")
        for scenario_type, scores in accuracy_by_type.items():
            avg_score = sum(scores) / len(scores)
            print(f"   {scenario_type.replace('_', ' ').title()}: {avg_score:.2%} ({len(scores)} tests)")
        
        # Main assertion: Overall accuracy should be ≥95%
        if overall_accuracy >= 0.95:
            print(f"\n🎉 SUCCESS! Achieved {overall_accuracy:.2%} accuracy - Target reached!")
        else:
            gap = 0.95 - overall_accuracy
            print(f"\n⚠️  Gap to target: {gap:.2%} - Need improvement in:")
            
            # Identify areas needing improvement
            for scenario_type, scores in accuracy_by_type.items():
                avg_score = sum(scores) / len(scores)
                if avg_score < 0.90:
                    print(f"     - {scenario_type.replace('_', ' ').title()}: {avg_score:.2%}")
        
        # Assert overall system quality
        assert overall_accuracy >= 0.90, f"System accuracy too low: {overall_accuracy:.2%}. Need ≥90% for production readiness."
        assert success_rate >= 0.95, f"Success rate too low: {success_rate:.2%}. Need ≥95% for reliability."
        
        # Stretch goal: 95% accuracy
        if overall_accuracy >= 0.95:
            print("🌟 STRETCH GOAL ACHIEVED: 95% accuracy reached!")
        
        return {
            'overall_accuracy': overall_accuracy,
            'success_rate': success_rate,
            'total_tests': len(results),
            'accuracy_by_type': {k: sum(v)/len(v) for k, v in accuracy_by_type.items()}
        }


# Integration test to run the comprehensive suite
def test_run_full_comprehensive_suite():
    """Integration test that runs the full comprehensive test suite"""
    from tests.test_framework.test_executor import run_comprehensive_test_suite
    
    print("\n🚀 Running Full Comprehensive Test Suite")
    print("=" * 60)
    
    # Run the comprehensive test suite
    summary = run_comprehensive_test_suite()
    
    print(f"\n📊 COMPREHENSIVE SUITE RESULTS:")
    print(f"   Total Tests: {summary.total_tests}")
    print(f"   Passed Tests: {summary.passed_tests}")
    print(f"   Overall Accuracy: {summary.overall_accuracy:.2%}")
    print(f"   Average Response Time: {summary.average_response_time:.3f}s")
    
    # Verify the comprehensive suite meets quality standards
    assert summary.overall_accuracy >= 0.85, f"Comprehensive suite accuracy too low: {summary.overall_accuracy:.2%}"
    assert summary.passed_tests >= summary.total_tests * 0.90, f"Too many test failures: {summary.passed_tests}/{summary.total_tests}"
    
    return summary


if __name__ == "__main__":
    # Allow running this file directly for quick testing
    pytest.main([__file__, "-v", "-s"])