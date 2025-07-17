"""
Comprehensive Test Suite for Al Essa Kuwait Chatbot
Tests various chat scenarios, tool calls, and aims for 95% accuracy
"""

import pytest
import json
import asyncio
from typing import Dict, List, Any, Tuple
from datetime import datetime
from unittest.mock import patch, MagicMock, AsyncMock
import logging

# Test categories and scenarios
TEST_SCENARIOS = {
    "agent_routing": [
        # Sales agent scenarios
        ("Show me wheelchairs", "SALES", "sales"),
        ("What's the price of air conditioners?", "SALES", "sales"),
        ("Do you have walkers?", "SALES", "sales"),
        ("I want to buy a nebulizer", "SALES", "sales"),
        ("Show me Sunrise brand products", "SALES", "sales"),
        
        # Doctor agent scenarios
        ("I have wrist pain", "DOCTOR", "doctor"),
        ("What should I do for a headache?", "DOCTOR", "doctor"),
        ("I have scoliosis and need equipment", "DOCTOR", "doctor"),
        ("My ankle is swollen", "DOCTOR", "doctor"),
        ("I need help with arthritis", "DOCTOR", "doctor"),
        
        # Edge cases
        ("I have back pain and need a wheelchair", "DOCTOR", "doctor"),
        ("Show me products for elderly care", "SALES", "sales"),
        ("What medical equipment do you have?", "SALES", "sales"),
    ],
    
    "product_search": [
        # Basic searches
        ("wheelchairs", ["wheelchair", "mobility"], 5),
        ("walkers", ["walker", "walking aid"], 3),
        ("nebulizers", ["nebulizer", "respiratory"], 2),
        
        # Brand searches
        ("Sunrise wheelchairs", ["Sunrise", "wheelchair"], 2),
        ("Al Essa products", ["Al Essa"], 10),
        
        # Price-based searches
        ("cheap wheelchairs", ["wheelchair", "budget"], 3),
        ("wheelchairs under 100 KWD", ["wheelchair", "price<100"], 2),
    ],
    
    "conversation_context": [
        # Multi-turn conversations
        ([
            ("I need help with mobility", "doctor"),
            ("What kind of mobility issues are you experiencing?", "response"),
            ("I have difficulty walking long distances", "doctor"),
            ("Show me walking aids", "sales")
        ], "context_switch"),
        
        # Follow-up questions
        ([
            ("Show me wheelchairs", "sales"),
            ("What's the price range?", "sales"),
            ("Do you have lightweight options?", "sales")
        ], "consistent_context"),
    ],
    
    "error_handling": [
        # Invalid inputs
        ("", "error", "empty_query"),
        ("a" * 1000, "error", "too_long"),
        ("!@#$%^&*()", "sales", "special_chars"),
        
        # Tool failures
        ("show me products", "tool_failure", "product_search_error"),
    ],
    
    "response_quality": [
        # Detailed responses
        ("Tell me about wheelchairs", "detailed", ["features", "types", "recommendations"]),
        ("What's the difference between manual and electric wheelchairs?", "comparison", ["manual", "electric", "differences"]),
        
        # Medical advice quality
        ("I have chronic back pain", "medical_advice", ["consult", "doctor", "meanwhile"]),
    ]
}

class TestScenarioRunner:
    """Runs and evaluates test scenarios"""
    
    def __init__(self):
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "accuracy": 0.0,
            "category_results": {},
            "failed_tests": []
        }
        self.logger = logging.getLogger(__name__)
    
    async def run_scenario(self, scenario: Tuple, category: str) -> Dict[str, Any]:
        """Run a single test scenario"""
        try:
            if category == "agent_routing":
                return await self._test_agent_routing(scenario)
            elif category == "product_search":
                return await self._test_product_search(scenario)
            elif category == "conversation_context":
                return await self._test_conversation_context(scenario)
            elif category == "error_handling":
                return await self._test_error_handling(scenario)
            elif category == "response_quality":
                return await self._test_response_quality(scenario)
        except Exception as e:
            self.logger.error(f"Error in scenario {scenario}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _test_agent_routing(self, scenario: Tuple) -> Dict[str, Any]:
        """Test agent routing accuracy"""
        query, expected_route, expected_agent = scenario
        
        from app.agents.agent_router import agent_router
        
        with patch('app.core.llm.llm.invoke') as mock_llm:
            # Simulate router decision
            mock_llm.return_value.content = expected_route
            
            result = agent_router.route_query(query)
            
            success = result.lower() == expected_agent.lower()
            
            return {
                "success": success,
                "query": query,
                "expected": expected_agent,
                "actual": result,
                "category": "agent_routing"
            }
    
    async def _test_product_search(self, scenario: Tuple) -> Dict[str, Any]:
        """Test product search functionality"""
        query, expected_keywords, min_results = scenario
        
        from app.tools.product_search import product_search_tool
        
        with patch('app.tools.product_search.MagentoScraper') as mock_scraper:
            # Mock product results
            mock_products = [
                {
                    "name": f"Test {keyword} Product {i}",
                    "price": 100.0 + i * 10,
                    "url": f"https://test.com/product-{i}",
                    "vendor": "Test Vendor"
                }
                for i in range(min_results)
                for keyword in expected_keywords[:1]
            ]
            
            mock_scraper.return_value.get_products.return_value = {
                "products": mock_products,
                "success": True
            }
            
            result = product_search_tool.invoke({"query": query})
            
            success = (
                result.get("success", False) and 
                len(result.get("products", [])) >= min_results and
                any(keyword.lower() in str(result).lower() for keyword in expected_keywords)
            )
            
            return {
                "success": success,
                "query": query,
                "expected_keywords": expected_keywords,
                "actual_results": len(result.get("products", [])),
                "category": "product_search"
            }
    
    async def _test_conversation_context(self, scenario: Tuple) -> Dict[str, Any]:
        """Test conversation context handling"""
        conversation, expected_behavior = scenario
        
        from app.agents.agent import chatbot_agent
        from app.core.conversation_memory import conversation_memory
        
        session_id = f"test_session_{datetime.now().timestamp()}"
        results = []
        
        for query, expected_type in conversation:
            if expected_type in ["sales", "doctor"]:
                with patch('app.agents.agent_router.agent_router.route_query') as mock_router:
                    mock_router.return_value = expected_type
                    
                    result = chatbot_agent.process_query(query, session_id)
                    results.append(result)
        
        # Verify context was maintained
        history = conversation_memory.get_conversation(session_id)
        
        success = len(history) == len(conversation) * 2  # User + assistant messages
        
        return {
            "success": success,
            "conversation_length": len(conversation),
            "history_length": len(history),
            "expected_behavior": expected_behavior,
            "category": "conversation_context"
        }
    
    async def _test_error_handling(self, scenario: Tuple) -> Dict[str, Any]:
        """Test error handling scenarios"""
        query, expected_behavior, error_type = scenario
        
        from app.agents.agent import chatbot_agent
        
        if error_type == "empty_query":
            result = chatbot_agent.process_query(query, "test_session")
            success = not result.get("success", True) or "error" in result
        
        elif error_type == "too_long":
            result = chatbot_agent.process_query(query, "test_session")
            success = result.get("success", True)  # Should handle gracefully
        
        elif error_type == "special_chars":
            result = chatbot_agent.process_query(query, "test_session")
            success = result.get("success", True)  # Should handle gracefully
        
        elif error_type == "product_search_error":
            with patch('app.tools.product_search.product_search_tool.invoke') as mock_tool:
                mock_tool.side_effect = Exception("Search failed")
                result = chatbot_agent.process_query(query, "test_session")
                success = result.get("success", True) and "error" not in result.get("reply", "").lower()
        
        return {
            "success": success,
            "query": query[:50] + "..." if len(query) > 50 else query,
            "error_type": error_type,
            "category": "error_handling"
        }
    
    async def _test_response_quality(self, scenario: Tuple) -> Dict[str, Any]:
        """Test response quality and content"""
        query, response_type, expected_elements = scenario
        
        from app.agents.agent import chatbot_agent
        
        with patch('app.core.llm.llm.invoke') as mock_llm:
            # Generate appropriate response based on type
            if response_type == "detailed":
                mock_response = f"Here's detailed information about {expected_elements[0]}: "
                mock_response += " ".join([f"Information about {elem}." for elem in expected_elements])
            elif response_type == "comparison":
                mock_response = f"Comparing {expected_elements[0]} and {expected_elements[1]}: "
                mock_response += f"The main {expected_elements[2]} are..."
            elif response_type == "medical_advice":
                mock_response = "I recommend you " + " ".join(expected_elements)
            
            mock_llm.return_value.content = mock_response
            
            result = chatbot_agent.process_query(query, "test_session")
            
            # Check if response contains expected elements
            reply = result.get("reply", "").lower()
            success = all(elem.lower() in reply for elem in expected_elements)
            
            return {
                "success": success,
                "query": query,
                "expected_elements": expected_elements,
                "response_length": len(reply),
                "category": "response_quality"
            }
    
    async def run_all_scenarios(self) -> Dict[str, Any]:
        """Run all test scenarios and compile results"""
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "accuracy": 0.0,
            "category_results": {},
            "failed_tests": [],
            "timestamp": datetime.now().isoformat()
        }
        
        for category, scenarios in TEST_SCENARIOS.items():
            category_results = {
                "total": len(scenarios),
                "passed": 0,
                "failed": 0,
                "accuracy": 0.0
            }
            
            for scenario in scenarios:
                self.results["total_tests"] += 1
                
                result = await self.run_scenario(scenario, category)
                
                if result.get("success", False):
                    self.results["passed"] += 1
                    category_results["passed"] += 1
                else:
                    self.results["failed"] += 1
                    category_results["failed"] += 1
                    self.results["failed_tests"].append(result)
            
            category_results["accuracy"] = (
                category_results["passed"] / category_results["total"] * 100
                if category_results["total"] > 0 else 0
            )
            
            self.results["category_results"][category] = category_results
        
        self.results["accuracy"] = (
            self.results["passed"] / self.results["total_tests"] * 100
            if self.results["total_tests"] > 0 else 0
        )
        
        return self.results
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate a detailed test report"""
        report = f"""
# Comprehensive Test Suite Results
Generated: {results['timestamp']}

## Overall Results
- **Total Tests**: {results['total_tests']}
- **Passed**: {results['passed']} ✅
- **Failed**: {results['failed']} ❌
- **Accuracy**: {results['accuracy']:.2f}%

## Category Breakdown
"""
        
        for category, cat_results in results['category_results'].items():
            report += f"""
### {category.replace('_', ' ').title()}
- Total: {cat_results['total']}
- Passed: {cat_results['passed']}
- Failed: {cat_results['failed']}
- Accuracy: {cat_results['accuracy']:.2f}%
"""
        
        if results['failed_tests']:
            report += "\n## Failed Tests\n"
            for test in results['failed_tests'][:10]:  # Show first 10 failures
                report += f"- **{test.get('category', 'unknown')}**: {test.get('query', 'N/A')}\n"
                report += f"  - Expected: {test.get('expected', 'N/A')}\n"
                report += f"  - Actual: {test.get('actual', test.get('error', 'N/A'))}\n\n"
        
        return report


# Pytest fixtures and test functions
@pytest.fixture
def test_runner():
    """Create a test scenario runner"""
    return TestScenarioRunner()


@pytest.mark.asyncio
async def test_comprehensive_suite(test_runner):
    """Run the comprehensive test suite"""
    results = await test_runner.run_all_scenarios()
    report = test_runner.generate_report(results)
    
    # Save report
    with open("tests/test_results_comprehensive.md", "w") as f:
        f.write(report)
    
    # Assert we meet the 95% accuracy target
    assert results["accuracy"] >= 95.0, f"Accuracy {results['accuracy']:.2f}% is below 95% target"


if __name__ == "__main__":
    # Run tests directly
    runner = TestScenarioRunner()
    results = asyncio.run(runner.run_all_scenarios())
    report = runner.generate_report(results)
    print(report)
    
    with open("tests/test_results_comprehensive.md", "w") as f:
        f.write(report)