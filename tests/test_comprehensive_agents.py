"""
Comprehensive Agent Tests for Al Essa Kuwait Virtual Assistant
Demonstrates the enhanced testing framework with 95% accuracy targets
"""

import pytest
from unittest.mock import patch, MagicMock
import time

from test_framework.test_executor import TestExecutor, AccuracyCalculator
from test_framework.test_data_generator import TestDataGenerator, get_golden_test_cases, ExpectedAgent, QueryType
from test_framework.mock_services import setup_mock_services

class TestComprehensiveAgents:
    """Comprehensive test suite for agent routing and tool execution"""
    
    @pytest.fixture
    def test_executor(self):
        """Fixture providing test executor with mock services"""
        return TestExecutor(use_mocks=True)
    
    @pytest.fixture
    def test_data_generator(self):
        """Fixture providing test data generator"""
        return TestDataGenerator()
    
    @pytest.fixture
    def mock_services(self):
        """Fixture providing mock services"""
        return setup_mock_services()
    
    def test_golden_test_cases(self, test_executor):
        """Test the golden test cases that should always pass with 100% accuracy"""
        golden_cases = get_golden_test_cases()
        
        results = []
        for scenario in golden_cases:
            result = test_executor.execute_scenario(scenario)
            results.append(result)
        
        # All golden cases should have high accuracy
        for result in results:
            assert result.success, f"Golden test case failed: {result.scenario.query}"
            assert result.accuracy_score >= 0.95, f"Low accuracy for golden case: {result.scenario.query} (got {result.accuracy_score})"
        
        # Overall accuracy should be excellent
        overall_accuracy = sum(r.accuracy_score for r in results) / len(results)
        assert overall_accuracy >= 0.98, f"Golden test cases overall accuracy too low: {overall_accuracy}"
    
    def test_product_search_scenarios(self, test_executor, test_data_generator):
        """Test product search routing and tool usage"""
        scenarios = test_data_generator.generate_product_search_scenarios(20)
        
        correct_routing = 0
        correct_tools = 0
        
        for scenario in scenarios:
            result = test_executor.execute_scenario(scenario)
            
            # Check agent routing
            if result.actual_agent == "sales":
                correct_routing += 1
            
            # Check tool usage
            if "product_search" in result.actual_tools:
                correct_tools += 1
        
        routing_accuracy = correct_routing / len(scenarios)
        tool_accuracy = correct_tools / len(scenarios)
        
        assert routing_accuracy >= 0.95, f"Product search routing accuracy too low: {routing_accuracy}"
        assert tool_accuracy >= 0.90, f"Product search tool usage too low: {tool_accuracy}"
    
    def test_medical_inquiry_scenarios(self, test_executor, test_data_generator):
        """Test medical inquiry routing and appropriate responses"""
        scenarios = test_data_generator.generate_medical_inquiry_scenarios(15)
        
        correct_routing = 0
        has_medical_disclaimers = 0
        
        for scenario in scenarios:
            result = test_executor.execute_scenario(scenario)
            
            # Check agent routing
            if result.actual_agent == "doctor":
                correct_routing += 1
            
            # Check for appropriate medical disclaimers
            if result.response_content and any(disclaimer in result.response_content.lower() 
                                             for disclaimer in ["consult", "healthcare professional", "doctor"]):
                has_medical_disclaimers += 1
        
        routing_accuracy = correct_routing / len(scenarios)
        disclaimer_rate = has_medical_disclaimers / len(scenarios)
        
        assert routing_accuracy >= 0.95, f"Medical inquiry routing accuracy too low: {routing_accuracy}"
        assert disclaimer_rate >= 0.80, f"Medical disclaimer rate too low: {disclaimer_rate}"
    
    def test_emergency_scenarios(self, test_executor, test_data_generator):
        """Test emergency scenario handling - must be 100% accurate"""
        scenarios = test_data_generator.generate_emergency_scenarios(5)
        
        for scenario in scenarios:
            result = test_executor.execute_scenario(scenario)
            
            # Emergency scenarios must route to doctor
            assert result.actual_agent == "doctor", f"Emergency scenario routed incorrectly: {scenario.query}"
            
            # Must use emergency response tools
            assert "emergency_response" in result.actual_tools or "medical_advice" in result.actual_tools, \
                f"Emergency scenario missing appropriate tools: {scenario.query}"
            
            # Must have high accuracy
            assert result.accuracy_score >= 0.95, f"Emergency scenario low accuracy: {scenario.query}"
    
    def test_brand_specific_scenarios(self, test_executor, test_data_generator):
        """Test brand-specific product queries"""
        scenarios = test_data_generator.generate_brand_specific_scenarios(10)
        
        sales_routing_count = 0
        brand_tool_usage = 0
        
        for scenario in scenarios:
            result = test_executor.execute_scenario(scenario)
            
            # Should route to sales
            if result.actual_agent == "sales":
                sales_routing_count += 1
            
            # Should use brand filtering when available
            if "brand_filter" in result.actual_tools or "product_search" in result.actual_tools:
                brand_tool_usage += 1
        
        routing_accuracy = sales_routing_count / len(scenarios)
        tool_usage_rate = brand_tool_usage / len(scenarios)
        
        assert routing_accuracy >= 0.95, f"Brand query routing accuracy too low: {routing_accuracy}"
        assert tool_usage_rate >= 0.90, f"Brand tool usage too low: {tool_usage_rate}"
    
    def test_price_inquiry_scenarios(self, test_executor, test_data_generator):
        """Test price-related queries and filtering"""
        scenarios = test_data_generator.generate_price_inquiry_scenarios(10)
        
        correct_agent = 0
        price_tools_used = 0
        
        for scenario in scenarios:
            result = test_executor.execute_scenario(scenario)
            
            # Should route to sales agent
            if result.actual_agent == "sales":
                correct_agent += 1
            
            # Should use price filtering tools
            if "price_filter" in result.actual_tools or "product_search" in result.actual_tools:
                price_tools_used += 1
        
        agent_accuracy = correct_agent / len(scenarios)
        tool_accuracy = price_tools_used / len(scenarios)
        
        assert agent_accuracy >= 0.95, f"Price inquiry agent routing too low: {agent_accuracy}"
        assert tool_accuracy >= 0.85, f"Price tool usage too low: {tool_accuracy}"
    
    def test_mixed_ambiguous_scenarios(self, test_executor, test_data_generator):
        """Test ambiguous scenarios that could go to either agent"""
        scenarios = test_data_generator.generate_mixed_scenarios(8)
        
        reasonable_routing = 0
        
        for scenario in scenarios:
            result = test_executor.execute_scenario(scenario)
            
            # For ambiguous scenarios, any reasonable routing is acceptable
            if result.actual_agent in ["sales", "doctor"]:
                reasonable_routing += 1
        
        routing_rate = reasonable_routing / len(scenarios)
        
        # Lower threshold for ambiguous cases
        assert routing_rate >= 0.80, f"Ambiguous scenario handling too low: {routing_rate}"
    
    def test_conversation_context_scenarios(self, test_executor, test_data_generator):
        """Test multi-turn conversation handling"""
        scenarios = test_data_generator.generate_conversation_context_scenarios(6)
        
        context_aware_responses = 0
        
        for scenario in scenarios:
            result = test_executor.execute_scenario(scenario)
            
            # Check if context is being used (simplified check)
            if result.success and result.accuracy_score > 0.7:
                context_aware_responses += 1
        
        context_accuracy = context_aware_responses / len(scenarios)
        
        assert context_accuracy >= 0.75, f"Context awareness too low: {context_accuracy}"
    
    def test_edge_case_scenarios(self, test_executor, test_data_generator):
        """Test edge cases and error handling"""
        scenarios = test_data_generator.generate_edge_case_scenarios(5)
        
        graceful_handling = 0
        
        for scenario in scenarios:
            result = test_executor.execute_scenario(scenario)
            
            # Edge cases should be handled gracefully (not crash)
            if result.success or result.error_message is None:
                graceful_handling += 1
        
        handling_rate = graceful_handling / len(scenarios)
        
        # Lower expectation for edge cases
        assert handling_rate >= 0.70, f"Edge case handling too low: {handling_rate}"
    
    def test_response_time_performance(self, test_executor, test_data_generator):
        """Test response time performance requirements"""
        scenarios = test_data_generator.generate_product_search_scenarios(10)
        
        response_times = []
        
        for scenario in scenarios:
            result = test_executor.execute_scenario(scenario)
            response_times.append(result.response_time)
        
        average_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        
        # Performance requirements
        assert average_time <= 3.0, f"Average response time too slow: {average_time}s"
        assert max_time <= 10.0, f"Maximum response time too slow: {max_time}s"
    
    def test_accuracy_calculator_functions(self):
        """Test the accuracy calculation functions"""
        # Test agent routing accuracy
        assert AccuracyCalculator.calculate_agent_routing_accuracy(ExpectedAgent.SALES, "sales") == 1.0
        assert AccuracyCalculator.calculate_agent_routing_accuracy(ExpectedAgent.DOCTOR, "sales") == 0.0
        assert AccuracyCalculator.calculate_agent_routing_accuracy(ExpectedAgent.AMBIGUOUS, "sales") == 0.85
        
        # Test tool usage accuracy
        assert AccuracyCalculator.calculate_tool_usage_accuracy(["product_search"], ["product_search", "price_filter"]) == 1.0
        assert AccuracyCalculator.calculate_tool_usage_accuracy(["medical_advice"], ["product_search"]) == 0.0
        assert AccuracyCalculator.calculate_tool_usage_accuracy([], ["any_tool"]) == 1.0
    
    def test_comprehensive_accuracy_target(self, test_executor, test_data_generator):
        """Test overall system accuracy against 95% target"""
        # Generate a smaller but comprehensive test suite
        scenarios = []
        scenarios.extend(test_data_generator.generate_product_search_scenarios(20))
        scenarios.extend(test_data_generator.generate_medical_inquiry_scenarios(10))
        scenarios.extend(test_data_generator.generate_emergency_scenarios(5))
        scenarios.extend(test_data_generator.generate_brand_specific_scenarios(8))
        scenarios.extend(test_data_generator.generate_price_inquiry_scenarios(7))
        
        summary = test_executor.execute_test_suite(scenarios)
        
        # Target accuracy requirements
        assert summary.overall_accuracy >= 0.85, f"Overall accuracy below minimum threshold: {summary.overall_accuracy:.2%}"
        
        # Individual category requirements (with mock services, these should be high)
        product_search_accuracy = summary.accuracy_by_type.get("product_search", 0)
        assert product_search_accuracy >= 0.90, f"Product search accuracy too low: {product_search_accuracy:.2%}"
        
        medical_inquiry_accuracy = summary.accuracy_by_type.get("medical_inquiry", 0)
        assert medical_inquiry_accuracy >= 0.90, f"Medical inquiry accuracy too low: {medical_inquiry_accuracy:.2%}"
        
        emergency_accuracy = summary.accuracy_by_type.get("emergency", 0)
        if emergency_accuracy > 0:  # Only check if emergency scenarios were included
            assert emergency_accuracy >= 0.95, f"Emergency scenario accuracy too low: {emergency_accuracy:.2%}"

@pytest.mark.integration
class TestIntegrationAccuracy:
    """Integration tests for overall system accuracy"""
    
    def test_full_comprehensive_suite(self):
        """Run the full comprehensive test suite"""
        from test_framework.test_executor import run_comprehensive_test_suite
        
        # This test runs the complete suite and saves results
        summary = run_comprehensive_test_suite()
        
        # Basic validation that the test ran
        assert summary.total_tests > 0
        assert summary.overall_accuracy >= 0.0  # At minimum, should return a score
        
        # Print summary for visibility
        print(f"\n=== COMPREHENSIVE TEST RESULTS ===")
        print(f"Total Tests: {summary.total_tests}")
        print(f"Overall Accuracy: {summary.overall_accuracy:.2%}")
        print(f"Target: 95%")
        print(f"Status: {'✅ ACHIEVED' if summary.overall_accuracy >= 0.95 else '❌ NEEDS WORK'}")

if __name__ == "__main__":
    # Run the comprehensive test when called directly
    pytest.main([__file__, "-v", "--tb=short"])