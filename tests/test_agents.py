"""
Tests for the agent components.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.agents.sales_agent import sales_agent
from app.agents.doctor_agent import doctor_agent
from app.agents.agent_router import agent_router
from app.agents.agent import chatbot_agent

# Real product data for testing
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
    }
]

def test_sales_agent_product_search():
    """Test that sales agent performs real product searches."""
    with patch('app.tools.product_search.product_search_tool') as mock_tool:
        mock_tool.invoke.return_value = {
            "success": True,
            "products": REAL_PRODUCTS,
            "count": len(REAL_PRODUCTS)
        }
        
        result = sales_agent.process_query("show me wheelchairs", "test_session")
        
        assert result["success"] is True
        assert result["agent_type"] == "sales"
        assert "products" in result
        assert len(result["products"]) > 0
        
        # Verify the tool was called
        mock_tool.invoke.assert_called_with({"query": "show me wheelchairs"})

def test_sales_agent_brand_search():
    """Test that sales agent handles brand-specific searches."""
    with patch('app.tools.product_search.product_search_tool') as mock_tool:
        mock_tool.invoke.return_value = {
            "success": True,
            "products": [p for p in REAL_PRODUCTS if "sunrise" in p["name"].lower()],
            "count": 1
        }
        
        result = sales_agent.process_query("do you have sunrise wheelchairs", "test_session")
        
        assert result["success"] is True
        assert result["agent_type"] == "sales"
        assert "products" in result
        assert len(result["products"]) > 0
        
        # Verify the tool was called
        mock_tool.invoke.assert_called_with({"query": "do you have sunrise wheelchairs"})

def test_sales_agent_cheapest_search():
    """Test that sales agent handles cheapest queries."""
    with patch('app.tools.product_search.product_search_tool') as mock_tool:
        mock_tool.invoke.return_value = {
            "success": True,
            "products": REAL_PRODUCTS,
            "count": len(REAL_PRODUCTS)
        }
        
        result = sales_agent.process_query("what's the cheapest wheelchair", "test_session")
        
        assert result["success"] is True
        assert result["agent_type"] == "sales"
        assert "products" in result
        assert len(result["products"]) > 0
        
        # Verify the tool was called
        mock_tool.invoke.assert_called_with({"query": "what's the cheapest wheelchair"})

def test_sales_agent_conversation():
    """Test that sales agent handles general conversation."""
    with patch('app.tools.product_search.product_search_tool') as mock_tool:
        result = sales_agent.process_query("hello", "test_session")
        
        assert result["success"] is True
        assert result["agent_type"] == "sales"
        assert "products" in result
        assert len(result["products"]) == 0  # No products for conversation
        
        # Verify the tool was NOT called for conversation
        mock_tool.invoke.assert_not_called()

def test_doctor_agent_symptom_search():
    """Test that doctor agent performs medical product searches."""
    with patch('app.tools.product_search.product_search_tool') as mock_tool:
        mock_tool.invoke.return_value = {
            "success": True,
            "products": REAL_PRODUCTS,
            "count": len(REAL_PRODUCTS)
        }
        
        result = doctor_agent.process_query("I have wrist pain", "test_session")
        
        assert result["success"] is True
        assert result["agent_type"] == "doctor"
        assert "products" in result
        assert len(result["products"]) > 0
        
        # Verify the tool was called
        mock_tool.invoke.assert_called()

def test_agent_router_sales_routing():
    """Test that agent router correctly routes sales queries."""
    with patch('app.core.llm.llm') as mock_llm:
        mock_llm.invoke.return_value.content = "SALES"
        
        with patch('app.agents.sales_agent.sales_agent.process_query') as mock_sales:
            mock_sales.return_value = {
                "success": True,
                "reply": "Here are some products",
                "products": REAL_PRODUCTS,
                "agent_type": "sales"
            }
            
            result = agent_router.route_query("show me wheelchairs", "test_session")
            
            assert result["routing_decision"] == "sales"
            assert result["agent_type"] == "sales"
            assert "products" in result

def test_agent_router_doctor_routing():
    """Test that agent router correctly routes medical queries."""
    with patch('app.core.llm.llm') as mock_llm:
        mock_llm.invoke.return_value.content = "DOCTOR"
        
        with patch('app.agents.doctor_agent.doctor_agent.process_query') as mock_doctor:
            mock_doctor.return_value = {
                "success": True,
                "reply": "Here's medical advice",
                "products": [],
                "agent_type": "doctor"
            }
            
            result = agent_router.route_query("I have a headache", "test_session")
            
            assert result["routing_decision"] == "doctor"
            assert result["agent_type"] == "doctor"

def test_main_agent_integration():
    """Test that main agent integrates all components correctly."""
    with patch('app.agents.agent_router.agent_router.route_query') as mock_router:
        mock_router.return_value = {
            "success": True,
            "reply": "Here are some products",
            "products": REAL_PRODUCTS,
            "agent_type": "sales",
            "routing_decision": "sales",
            "workflow_steps": ["intelligent_routing", "sales_analysis", "product_search"]
        }
        
        result = chatbot_agent.process_query("show me wheelchairs", "test_session")
        
        assert result["success"] is True
        assert result["agent_type"] == "sales"
        assert result["routing_decision"] == "sales"
        assert "products" in result
        assert len(result["products"]) > 0
        assert "intelligent_routing" in result["workflow_steps"]

def test_no_fake_responses():
    """Test that agents don't generate fake product responses."""
    fake_product_names = [
        "Basic Manual Wheelchair",
        "Deluxe Manual Wheelchair",
        "Portable Travel Wheelchair",
        "Lightweight Electric Wheelchair",
        "Affordable Power Wheelchair"
    ]
    
    with patch('app.tools.product_search.product_search_tool') as mock_tool:
        mock_tool.invoke.return_value = {
            "success": True,
            "products": REAL_PRODUCTS,
            "count": len(REAL_PRODUCTS)
        }
        
        result = sales_agent.process_query("show me wheelchairs", "test_session")
        
        assert result["success"] is True
        reply = result["reply"].lower()
        
        # Check that no fake product names appear in the response
        for fake_name in fake_product_names:
            assert fake_name.lower() not in reply
        
        # Check that real product names appear in the response
        for product in REAL_PRODUCTS:
            # Check if part of the real product name appears in response
            product_words = product["name"].lower().split()[:3]  # First 3 words
            assert any(word in reply for word in product_words)

def test_conversation_memory():
    """Test that conversation memory is properly maintained."""
    from app.core.conversation_memory import conversation_memory
    
    session_id = "test_memory_session"
    
    # Clear any existing session
    conversation_memory.clear_session(session_id)
    
    # Test adding messages
    conversation_memory.add_message(session_id, "user", "show me wheelchairs")
    conversation_memory.add_message(session_id, "assistant", "Here are some wheelchairs", "sales", REAL_PRODUCTS)
    
    # Test retrieving history
    history = conversation_memory.get_conversation_history(session_id)
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "show me wheelchairs"
    assert history[1]["role"] == "assistant"
    assert history[1]["agent_type"] == "sales"
    
    # Clean up
    conversation_memory.clear_session(session_id)