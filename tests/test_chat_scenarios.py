import pytest
from unittest.mock import patch

from app.agents.agent import chatbot_agent
from app.tools.product_search import product_search_tool

# Sample product list returned by the mocked product search tool
MOCK_PRODUCTS = [
    {"name": "Sample Product", "price": 99.0, "url": "https://example.com/p"}
]

# (query, expected_agent_type)
SCENARIOS = [
    ("Do you have Sunrise wheelchairs?", "sales"),
    ("I hurt my ankle", "doctor"),
    ("What's the cheapest wheelchair?", "sales"),
    ("I have scoliosis", "doctor"),
    ("Show me walkers", "sales"),
    ("What should I do for my headache?", "doctor"),
    ("Looking for a refrigerator", "sales"),
    ("Can you recommend a back brace?", "doctor"),
    ("Hello there!", "sales"),
    ("I need medical equipment for my diabetes", "doctor"),
]

@pytest.mark.parametrize("query,expected_agent", SCENARIOS)
@patch("app.tools.product_search.product_search_tool.invoke", return_value={"success": True, "products": MOCK_PRODUCTS, "count": len(MOCK_PRODUCTS)})
@patch("app.core.llm.llm")
def test_chatbot_routing_accuracy(mock_llm, mock_product_search, query, expected_agent):
    """Ensure the chatbot routes queries to the correct specialized agent."""

    # Configure the mocked llm to always return a generic conversation response to prevent external calls
    mock_llm.invoke.return_value.content = "CONVERSATION"

    result = chatbot_agent.process_query(query, session_id="test_session")

    assert result["success"] is True, f"Processing failed for query: {query}"
    assert result["agent_type"] == expected_agent, f"Incorrect agent for query: {query} -> got {result['agent_type']} expected {expected_agent}"


def test_overall_routing_accuracy():
    """Calculate overall accuracy across scenarios and ensure it meets the 95% threshold."""

    correct = 0
    total = len(SCENARIOS)

    with patch("app.tools.product_search.product_search_tool.invoke", return_value={"success": True, "products": MOCK_PRODUCTS, "count": len(MOCK_PRODUCTS)}), \
         patch("app.core.llm.llm") as mock_llm:

        mock_llm.invoke.return_value.content = "CONVERSATION"

        for query, expected_agent in SCENARIOS:
            result = chatbot_agent.process_query(query, session_id="accuracy_session")
            if result["agent_type"] == expected_agent:
                correct += 1

    accuracy = correct / total
    assert accuracy >= 0.95, f"Routing accuracy below threshold: {accuracy*100:.1f}% (expected >= 95%)"