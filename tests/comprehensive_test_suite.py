"""
Comprehensive Test Suite for Chatbot Agents
Tests various scenarios, tool calls, and edge cases to achieve 95% accuracy.
"""

import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock
from typing import Dict, List, Any
import asyncio

# Import the agents and tools
from app.agents.sales_agent import SalesAgent
from app.agents.doctor_agent import DoctorAgent
from app.agents.agent_router import agent_router
from app.agents.agent import chatbot_agent
from app.tools.product_search import product_search_tool
from app.tools.price_filter import price_filter_tool
from app.tools.response_filter import response_filter_tool
from app.core.conversation_memory import conversation_memory

# Test data
REAL_PRODUCTS = [
    {
        "name": "Sunrise Breezy Style Light Wheelchair, 12 inch Solid Wheel",
        "price": 150.0,
        "url": "https://www.alessaonline.com/default/catalog/product/view/id/123",
        "vendor": "Sunrise",
        "currency": "KWD"
    },
    {
        "name": "Al Essa CA9791LF Light Wheelchair Light Wheelchair",
        "price": 75.0,
        "url": "https://www.alessaonline.com/default/catalog/product/view/id/456",
        "vendor": "Al Essa",
        "currency": "KWD"
    },
    {
        "name": "Drive Medical Deluxe Transport Chair",
        "price": 200.0,
        "url": "https://www.alessaonline.com/default/catalog/product/view/id/789",
        "vendor": "Drive Medical",
        "currency": "KWD"
    },
    {
        "name": "Wrist Brace Support for Carpal Tunnel",
        "price": 25.0,
        "url": "https://www.alessaonline.com/default/catalog/product/view/id/101",
        "vendor": "Medical Supply Co",
        "currency": "KWD"
    },
    {
        "name": "Knee Brace with Side Stabilizers",
        "price": 45.0,
        "url": "https://www.alessaonline.com/default/catalog/product/view/id/102",
        "vendor": "Medical Supply Co",
        "currency": "KWD"
    }
]

# Test scenarios for different accuracy levels
BASIC_SCENARIOS = [
    # Sales Agent Scenarios
    {
        "category": "sales_basic",
        "query": "show me wheelchairs",
        "expected_agent": "sales",
        "expected_tools": ["product_search"],
        "expected_products": True,
        "description": "Basic product search"
    },
    {
        "category": "sales_basic",
        "query": "do you have sunrise wheelchairs?",
        "expected_agent": "sales",
        "expected_tools": ["product_search"],
        "expected_products": True,
        "description": "Brand-specific search"
    },
    {
        "category": "sales_basic",
        "query": "what's the cheapest wheelchair?",
        "expected_agent": "sales",
        "expected_tools": ["product_search", "price_filter"],
        "expected_products": True,
        "description": "Price-based search"
    },
    {
        "category": "sales_basic",
        "query": "hello",
        "expected_agent": "sales",
        "expected_tools": [],
        "expected_products": False,
        "description": "Greeting conversation"
    },
    
    # Doctor Agent Scenarios
    {
        "category": "doctor_basic",
        "query": "I have wrist pain",
        "expected_agent": "doctor",
        "expected_tools": ["product_search"],
        "expected_products": True,
        "description": "Symptom-based product recommendation"
    },
    {
        "category": "doctor_basic",
        "query": "my knee hurts when I walk",
        "expected_agent": "doctor",
        "expected_tools": ["product_search"],
        "expected_products": True,
        "description": "Mobility issue recommendation"
    },
    {
        "category": "doctor_basic",
        "query": "how are you today?",
        "expected_agent": "doctor",
        "expected_tools": [],
        "expected_products": False,
        "description": "General conversation"
    }
]

INTERMEDIATE_SCENARIOS = [
    # Complex Sales Scenarios
    {
        "category": "sales_intermediate",
        "query": "I need a wheelchair under 100 KWD",
        "expected_agent": "sales",
        "expected_tools": ["product_search", "price_filter"],
        "expected_products": True,
        "expected_price_constraint": True,
        "description": "Price-constrained search"
    },
    {
        "category": "sales_intermediate",
        "query": "show me wheelchairs between 50 and 150 KWD",
        "expected_agent": "sales",
        "expected_tools": ["product_search", "price_filter"],
        "expected_products": True,
        "expected_price_constraint": True,
        "description": "Price range search"
    },
    {
        "category": "sales_intermediate",
        "query": "what's the best wheelchair for daily use?",
        "expected_agent": "sales",
        "expected_tools": ["product_search", "response_filter"],
        "expected_products": True,
        "description": "Quality-based recommendation"
    },
    
    # Complex Medical Scenarios
    {
        "category": "doctor_intermediate",
        "query": "I have severe back pain that's been going on for weeks",
        "expected_agent": "doctor",
        "expected_tools": ["product_search"],
        "expected_products": True,
        "expected_disclaimer": True,
        "description": "Severe chronic condition"
    },
    {
        "category": "doctor_intermediate",
        "query": "my grandmother needs help with mobility, she's 85",
        "expected_agent": "doctor",
        "expected_tools": ["product_search"],
        "expected_products": True,
        "expected_disclaimer": True,
        "description": "Elderly care recommendation"
    }
]

ADVANCED_SCENARIOS = [
    # Multi-turn Conversations
    {
        "category": "conversation_flow",
        "conversation": [
            ("user", "I have wrist pain"),
            ("assistant", "I understand you're experiencing wrist pain. Let me help you find appropriate products."),
            ("user", "it's been hurting for 3 days"),
            ("assistant", "Thank you for that additional information. Since this has been ongoing for 3 days, I'd recommend...")
        ],
        "expected_agent": "doctor",
        "expected_context_retention": True,
        "description": "Multi-turn symptom discussion"
    },
    {
        "category": "conversation_flow",
        "conversation": [
            ("user", "show me wheelchairs"),
            ("assistant", "Here are some wheelchair options for you..."),
            ("user", "do you have anything cheaper?"),
            ("assistant", "Let me filter those results to show you more affordable options...")
        ],
        "expected_agent": "sales",
        "expected_context_retention": True,
        "description": "Multi-turn product refinement"
    },
    
    # Edge Cases
    {
        "category": "edge_cases",
        "query": "",
        "expected_agent": "sales",  # Default fallback
        "expected_tools": [],
        "expected_products": False,
        "description": "Empty query handling"
    },
    {
        "category": "edge_cases",
        "query": "   ",  # Whitespace only
        "expected_agent": "sales",
        "expected_tools": [],
        "expected_products": False,
        "description": "Whitespace-only query"
    },
    {
        "category": "edge_cases",
        "query": "show me products that don't exist in your catalog",
        "expected_agent": "sales",
        "expected_tools": ["product_search"],
        "expected_products": False,
        "expected_alternative_suggestions": True,
        "description": "No results handling"
    }
]

TOOL_CALL_SCENARIOS = [
    {
        "category": "tool_calls",
        "query": "wheelchairs under 80 KWD",
        "expected_tool_calls": [
            {"tool": "product_search", "params": {"query": "wheelchairs"}},
            {"tool": "price_filter", "params": {"products": "previous_results", "query": "wheelchairs under 80 KWD"}}
        ],
        "description": "Sequential tool calls"
    },
    {
        "category": "tool_calls",
        "query": "best medical equipment for elderly",
        "expected_tool_calls": [
            {"tool": "product_search", "params": {"query": "medical equipment elderly"}},
            {"tool": "response_filter", "params": {"products": "search_results", "query": "best medical equipment for elderly"}}
        ],
        "description": "Quality-based filtering"
    }
]

class TestComprehensiveScenarios:
    """Comprehensive test suite for all chatbot scenarios."""
    
    def setup_method(self):
        """Set up test environment."""
        self.sales_agent = SalesAgent()
        self.doctor_agent = DoctorAgent()
        
    def teardown_method(self):
        """Clean up after tests."""
        # Clear conversation memory
        conversation_memory.clear_all_sessions()
    
    @pytest.mark.parametrize("scenario", BASIC_SCENARIOS)
    def test_basic_scenarios(self, scenario):
        """Test basic functionality scenarios."""
        query = scenario["query"]
        expected_agent = scenario["expected_agent"]
        expected_tools = scenario["expected_tools"]
        expected_products = scenario["expected_products"]
        
        with patch('app.tools.product_search.product_search_tool') as mock_search:
            mock_search.invoke.return_value = {
                "success": True,
                "products": REAL_PRODUCTS,
                "count": len(REAL_PRODUCTS)
            }
            
            with patch('app.tools.price_filter.price_filter_tool') as mock_price:
                mock_price.invoke.return_value = {
                    "success": True,
                    "products": [p for p in REAL_PRODUCTS if p["price"] < 100],
                    "constraints": {"max_price": 100}
                }
                
                with patch('app.tools.response_filter.response_filter_tool') as mock_filter:
                    mock_filter.invoke.return_value = {
                        "success": True,
                        "filtered_products": REAL_PRODUCTS[:2],
                        "filter_type": "best"
                    }
                    
                    # Test agent routing
                    with patch('app.core.llm.llm') as mock_llm:
                        mock_llm.invoke.return_value.content = expected_agent.upper()
                        
                        result = agent_router.route_query(query, "test_session")
                        
                        assert result["agent_type"] == expected_agent
                        assert result["success"] is True
                        
                        # Verify tool calls
                        if "product_search" in expected_tools:
                            mock_search.invoke.assert_called()
                        if "price_filter" in expected_tools:
                            mock_price.invoke.assert_called()
                        if "response_filter" in expected_tools:
                            mock_filter.invoke.assert_called()
                        
                        # Verify products
                        if expected_products:
                            assert len(result.get("products", [])) > 0
                        else:
                            assert len(result.get("products", [])) == 0
    
    @pytest.mark.parametrize("scenario", INTERMEDIATE_SCENARIOS)
    def test_intermediate_scenarios(self, scenario):
        """Test intermediate complexity scenarios."""
        query = scenario["query"]
        expected_agent = scenario["expected_agent"]
        expected_tools = scenario["expected_tools"]
        
        with patch('app.tools.product_search.product_search_tool') as mock_search:
            mock_search.invoke.return_value = {
                "success": True,
                "products": REAL_PRODUCTS,
                "count": len(REAL_PRODUCTS)
            }
            
            with patch('app.tools.price_filter.price_filter_tool') as mock_price:
                mock_price.invoke.return_value = {
                    "success": True,
                    "products": [p for p in REAL_PRODUCTS if p["price"] < 100],
                    "constraints": {"max_price": 100}
                }
                
                with patch('app.core.llm.llm') as mock_llm:
                    mock_llm.invoke.return_value.content = expected_agent.upper()
                    
                    result = agent_router.route_query(query, "test_session")
                    
                    assert result["agent_type"] == expected_agent
                    assert result["success"] is True
                    
                    # Check for price constraints
                    if scenario.get("expected_price_constraint"):
                        assert "price_filter" in result.get("workflow_steps", [])
                    
                    # Check for medical disclaimers
                    if scenario.get("expected_disclaimer"):
                        reply = result.get("reply", "").lower()
                        assert any(word in reply for word in ["disclaimer", "medical", "professional", "consult"])
    
    @pytest.mark.parametrize("scenario", ADVANCED_SCENARIOS)
    def test_advanced_scenarios(self, scenario):
        """Test advanced scenarios including multi-turn conversations."""
        if "conversation" in scenario:
            # Test multi-turn conversation
            conversation = scenario["conversation"]
            session_id = f"test_session_{scenario['category']}"
            
            for i, (role, content) in enumerate(conversation):
                if role == "user":
                    with patch('app.tools.product_search.product_search_tool') as mock_search:
                        mock_search.invoke.return_value = {
                            "success": True,
                            "products": REAL_PRODUCTS,
                            "count": len(REAL_PRODUCTS)
                        }
                        
                        with patch('app.core.llm.llm') as mock_llm:
                            mock_llm.invoke.return_value.content = scenario["expected_agent"].upper()
                            
                            result = agent_router.route_query(content, session_id)
                            
                            # Verify context retention
                            if scenario.get("expected_context_retention") and i > 0:
                                history = conversation_memory.get_conversation_history(session_id)
                                assert len(history) >= i + 1
        else:
            # Test edge cases
            query = scenario["query"]
            expected_agent = scenario["expected_agent"]
            
            with patch('app.tools.product_search.product_search_tool') as mock_search:
                if scenario.get("expected_alternative_suggestions"):
                    mock_search.invoke.return_value = {
                        "success": True,
                        "products": [],
                        "count": 0
                    }
                else:
                    mock_search.invoke.return_value = {
                        "success": True,
                        "products": REAL_PRODUCTS,
                        "count": len(REAL_PRODUCTS)
                    }
                
                with patch('app.core.llm.llm') as mock_llm:
                    mock_llm.invoke.return_value.content = expected_agent.upper()
                    
                    result = agent_router.route_query(query, "test_session")
                    
                    assert result["success"] is True
                    
                    # Check for alternative suggestions when no products found
                    if scenario.get("expected_alternative_suggestions"):
                        reply = result.get("reply", "").lower()
                        assert any(word in reply for word in ["alternative", "similar", "related", "suggest"])
    
    @pytest.mark.parametrize("scenario", TOOL_CALL_SCENARIOS)
    def test_tool_call_sequences(self, scenario):
        """Test complex tool call sequences."""
        query = scenario["query"]
        expected_tool_calls = scenario["expected_tool_calls"]
        
        with patch('app.tools.product_search.product_search_tool') as mock_search:
            mock_search.invoke.return_value = {
                "success": True,
                "products": REAL_PRODUCTS,
                "count": len(REAL_PRODUCTS)
            }
            
            with patch('app.tools.price_filter.price_filter_tool') as mock_price:
                mock_price.invoke.return_value = {
                    "success": True,
                    "products": [p for p in REAL_PRODUCTS if p["price"] < 100],
                    "constraints": {"max_price": 100}
                }
                
                with patch('app.tools.response_filter.response_filter_tool') as mock_filter:
                    mock_filter.invoke.return_value = {
                        "success": True,
                        "filtered_products": REAL_PRODUCTS[:2],
                        "filter_type": "best"
                    }
                    
                    with patch('app.core.llm.llm') as mock_llm:
                        mock_llm.invoke.return_value.content = "SALES"
                        
                        result = agent_router.route_query(query, "test_session")
                        
                        assert result["success"] is True
                        
                        # Verify tool call sequence
                        workflow_steps = result.get("workflow_steps", [])
                        for tool_call in expected_tool_calls:
                            tool_name = tool_call["tool"]
                            if tool_name == "product_search":
                                assert "product_search" in workflow_steps
                                mock_search.invoke.assert_called()
                            elif tool_name == "price_filter":
                                assert "price_filtering" in workflow_steps
                                mock_price.invoke.assert_called()
                            elif tool_name == "response_filter":
                                assert "response_filtering" in workflow_steps
                                mock_filter.invoke.assert_called()

class TestAccuracyMetrics:
    """Test suite for measuring and improving accuracy metrics."""
    
    def setup_method(self):
        """Set up test environment."""
        self.test_results = []
        
    def test_response_accuracy(self):
        """Test that responses are accurate and relevant."""
        test_queries = [
            ("show me wheelchairs", "sales", "product_search"),
            ("I have wrist pain", "doctor", "product_search"),
            ("hello", "sales", "conversation"),
            ("what's the cheapest wheelchair?", "sales", "price_filter"),
            ("my back hurts", "doctor", "product_search")
        ]
        
        accuracy_count = 0
        total_tests = len(test_queries)
        
        for query, expected_agent, expected_action in test_queries:
            with patch('app.tools.product_search.product_search_tool') as mock_search:
                mock_search.invoke.return_value = {
                    "success": True,
                    "products": REAL_PRODUCTS,
                    "count": len(REAL_PRODUCTS)
                }
                
                with patch('app.core.llm.llm') as mock_llm:
                    mock_llm.invoke.return_value.content = expected_agent.upper()
                    
                    result = agent_router.route_query(query, "test_session")
                    
                    # Check accuracy
                    is_accurate = (
                        result["agent_type"] == expected_agent and
                        result["success"] is True
                    )
                    
                    if is_accurate:
                        accuracy_count += 1
                    
                    self.test_results.append({
                        "query": query,
                        "expected_agent": expected_agent,
                        "actual_agent": result["agent_type"],
                        "expected_action": expected_action,
                        "actual_workflow": result.get("workflow_steps", []),
                        "accurate": is_accurate
                    })
        
        accuracy_rate = (accuracy_count / total_tests) * 100
        assert accuracy_rate >= 95, f"Accuracy rate {accuracy_rate}% is below 95% target"
        
        # Log detailed results
        print(f"\nAccuracy Test Results:")
        print(f"Total Tests: {total_tests}")
        print(f"Accurate: {accuracy_count}")
        print(f"Accuracy Rate: {accuracy_rate:.1f}%")
        
        for result in self.test_results:
            status = "✅" if result["accurate"] else "❌"
            print(f"{status} {result['query']} -> {result['actual_agent']} (expected: {result['expected_agent']})")
    
    def test_tool_call_accuracy(self):
        """Test that tool calls are made correctly."""
        test_cases = [
            {
                "query": "wheelchairs under 100 KWD",
                "expected_tools": ["product_search", "price_filter"],
                "description": "Price-constrained search"
            },
            {
                "query": "best medical equipment",
                "expected_tools": ["product_search", "response_filter"],
                "description": "Quality-based search"
            },
            {
                "query": "hello there",
                "expected_tools": [],
                "description": "Conversation only"
            }
        ]
        
        tool_accuracy_count = 0
        total_tool_tests = len(test_cases)
        
        for test_case in test_cases:
            query = test_case["query"]
            expected_tools = test_case["expected_tools"]
            
            with patch('app.tools.product_search.product_search_tool') as mock_search:
                mock_search.invoke.return_value = {
                    "success": True,
                    "products": REAL_PRODUCTS,
                    "count": len(REAL_PRODUCTS)
                }
                
                with patch('app.tools.price_filter.price_filter_tool') as mock_price:
                    mock_price.invoke.return_value = {
                        "success": True,
                        "products": [p for p in REAL_PRODUCTS if p["price"] < 100],
                        "constraints": {"max_price": 100}
                    }
                    
                    with patch('app.tools.response_filter.response_filter_tool') as mock_filter:
                        mock_filter.invoke.return_value = {
                            "success": True,
                            "filtered_products": REAL_PRODUCTS[:2],
                            "filter_type": "best"
                        }
                        
                        with patch('app.core.llm.llm') as mock_llm:
                            mock_llm.invoke.return_value.content = "SALES"
                            
                            result = agent_router.route_query(query, "test_session")
                            
                            # Check tool call accuracy
                            workflow_steps = result.get("workflow_steps", [])
                            actual_tools = []
                            
                            if "product_search" in workflow_steps:
                                actual_tools.append("product_search")
                            if "price_filtering" in workflow_steps:
                                actual_tools.append("price_filter")
                            if "response_filtering" in workflow_steps:
                                actual_tools.append("response_filter")
                            
                            is_tool_accurate = set(actual_tools) == set(expected_tools)
                            
                            if is_tool_accurate:
                                tool_accuracy_count += 1
                            
                            print(f"Tool Test: {test_case['description']}")
                            print(f"  Expected: {expected_tools}")
                            print(f"  Actual: {actual_tools}")
                            print(f"  Accurate: {'✅' if is_tool_accurate else '❌'}")
        
        tool_accuracy_rate = (tool_accuracy_count / total_tool_tests) * 100
        assert tool_accuracy_rate >= 95, f"Tool call accuracy rate {tool_accuracy_rate}% is below 95% target"
        
        print(f"\nTool Call Accuracy: {tool_accuracy_rate:.1f}%")

class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling scenarios."""
    
    def test_empty_and_whitespace_queries(self):
        """Test handling of empty and whitespace-only queries."""
        test_queries = ["", "   ", "\n", "\t"]
        
        for query in test_queries:
            with patch('app.core.llm.llm') as mock_llm:
                mock_llm.invoke.return_value.content = "SALES"
                
                result = agent_router.route_query(query, "test_session")
                
                # Should handle gracefully without crashing
                assert result["success"] is True
                assert "reply" in result
    
    def test_very_long_queries(self):
        """Test handling of very long queries."""
        long_query = "I need a wheelchair " * 50  # Very long query
        
        with patch('app.tools.product_search.product_search_tool') as mock_search:
            mock_search.invoke.return_value = {
                "success": True,
                "products": REAL_PRODUCTS,
                "count": len(REAL_PRODUCTS)
            }
            
            with patch('app.core.llm.llm') as mock_llm:
                mock_llm.invoke.return_value.content = "SALES"
                
                result = agent_router.route_query(long_query, "test_session")
                
                assert result["success"] is True
                assert len(result.get("reply", "")) > 0
    
    def test_special_characters(self):
        """Test handling of queries with special characters."""
        special_queries = [
            "wheelchairs with @#$% symbols",
            "I need a wheelchair!",
            "What about wheelchairs?",
            "Wheelchairs: the best ones",
            "Wheelchairs (manual) vs electric"
        ]
        
        for query in special_queries:
            with patch('app.tools.product_search.product_search_tool') as mock_search:
                mock_search.invoke.return_value = {
                    "success": True,
                    "products": REAL_PRODUCTS,
                    "count": len(REAL_PRODUCTS)
                }
                
                with patch('app.core.llm.llm') as mock_llm:
                    mock_llm.invoke.return_value.content = "SALES"
                    
                    result = agent_router.route_query(query, "test_session")
                    
                    assert result["success"] is True
                    assert "reply" in result
    
    def test_tool_failure_handling(self):
        """Test handling when tools fail."""
        with patch('app.tools.product_search.product_search_tool') as mock_search:
            mock_search.invoke.side_effect = Exception("Tool failed")
            
            with patch('app.core.llm.llm') as mock_llm:
                mock_llm.invoke.return_value.content = "SALES"
                
                result = agent_router.route_query("show me wheelchairs", "test_session")
                
                # Should handle tool failure gracefully
                assert result["success"] is True
                assert "error" in result.get("reply", "").lower() or "sorry" in result.get("reply", "").lower()
    
    def test_llm_failure_handling(self):
        """Test handling when LLM fails."""
        with patch('app.core.llm.llm') as mock_llm:
            mock_llm.invoke.side_effect = Exception("LLM failed")
            
            result = agent_router.route_query("hello", "test_session")
            
            # Should handle LLM failure gracefully
            assert result["success"] is True
            assert "error" in result.get("reply", "").lower() or "sorry" in result.get("reply", "").lower()

class TestPerformanceAndScalability:
    """Test performance and scalability aspects."""
    
    def test_response_time(self):
        """Test that responses are generated within acceptable time limits."""
        import time
        
        test_queries = [
            "show me wheelchairs",
            "I have wrist pain",
            "what's the cheapest wheelchair?",
            "hello"
        ]
        
        max_response_time = 5.0  # 5 seconds max
        
        for query in test_queries:
            with patch('app.tools.product_search.product_search_tool') as mock_search:
                mock_search.invoke.return_value = {
                    "success": True,
                    "products": REAL_PRODUCTS,
                    "count": len(REAL_PRODUCTS)
                }
                
                with patch('app.core.llm.llm') as mock_llm:
                    mock_llm.invoke.return_value.content = "SALES"
                    
                    start_time = time.time()
                    result = agent_router.route_query(query, "test_session")
                    end_time = time.time()
                    
                    response_time = end_time - start_time
                    assert response_time < max_response_time, f"Response time {response_time}s exceeds limit {max_response_time}s"
                    assert result["success"] is True
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        import threading
        import time
        
        results = []
        errors = []
        
        def make_request(query, session_id):
            try:
                with patch('app.tools.product_search.product_search_tool') as mock_search:
                    mock_search.invoke.return_value = {
                        "success": True,
                        "products": REAL_PRODUCTS,
                        "count": len(REAL_PRODUCTS)
                    }
                    
                    with patch('app.core.llm.llm') as mock_llm:
                        mock_llm.invoke.return_value.content = "SALES"
                        
                        result = agent_router.route_query(query, session_id)
                        results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(
                target=make_request,
                args=(f"test query {i}", f"session_{i}")
            )
            threads.append(thread)
        
        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        end_time = time.time()
        
        # Verify results
        assert len(errors) == 0, f"Concurrent requests produced errors: {errors}"
        assert len(results) == 5, f"Expected 5 results, got {len(results)}"
        
        for result in results:
            assert result["success"] is True
        
        total_time = end_time - start_time
        print(f"Concurrent requests completed in {total_time:.2f}s")

if __name__ == "__main__":
    # Run the comprehensive test suite
    pytest.main([__file__, "-v", "--tb=short"])