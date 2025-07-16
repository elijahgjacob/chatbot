"""
Tests for the Agentic Workflow
"""
import pytest
from unittest.mock import patch, MagicMock
from app.agents.agent import ChatbotAgent
from app.tools.tools import ResponseFilterTool, QueryRefinementTool


class TestChatbotAgent:
    """Test the ChatbotAgent class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.agent = ChatbotAgent()
    
    def test_agent_initialization(self):
        """Test that the agent initializes correctly"""
        assert self.agent is not None
        assert hasattr(self.agent, 'memory')
        assert hasattr(self.agent, 'prompt')
    
    def test_simple_product_query(self):
        """Test processing a simple product query"""
        # Mock the tools directly on the agent instance
        self.agent.product_search_tool._run = lambda query: {
            "success": True,
            "products": [
                {"name": "Basic Wheelchair", "price": "150 KWD", "link": "http://example.com/1"},
                {"name": "Premium Wheelchair", "price": "300 KWD", "link": "http://example.com/2"}
            ],
            "count": 2
        }
        
        self.agent.query_refinement_tool._run = lambda query: {"success": True, "search_query": "wheelchair"}
        
        result = self.agent.process_query("wheelchair")
        
        assert result["success"] is True
        assert "wheelchair" in result["response"].lower()
        assert len(result["products"]) == 2
        assert "product_search" in result["workflow_steps"]
    
    def test_complex_query_with_filtering(self):
        """Test processing a complex query that needs refinement and filtering"""
        # Mock the tools directly on the agent instance
        self.agent.query_refinement_tool._run = lambda query: {
            "success": True,
            "search_query": "wheelchair",
            "product": "wheelchair",
            "requirements": "cheapest"
        }
        
        self.agent.product_search_tool._run = lambda query: {
            "success": True,
            "products": [
                {"name": "Basic Wheelchair", "price": "150 KWD", "link": "http://example.com/1"},
                {"name": "Premium Wheelchair", "price": "300 KWD", "link": "http://example.com/2"},
                {"name": "Luxury Wheelchair", "price": "500 KWD", "link": "http://example.com/3"}
            ],
            "count": 3
        }
        
        self.agent.response_filter_tool._run = lambda products, query: {
            "success": True,
            "filtered_products": [
                {"name": "Basic Wheelchair", "price": "150 KWD", "link": "http://example.com/1"}
            ],
            "filter_type": "cheapest",
            "count": 1
        }
        
        result = self.agent.process_query("I need the cheapest wheelchair available")
        
        assert result["success"] is True
        assert "cheapest" in result["response"].lower()
        assert len(result["products"]) == 1
        assert "query_refinement" in result["workflow_steps"]
        assert "product_search" in result["workflow_steps"]
        assert "response_filter" in result["workflow_steps"]
    
    @patch('app.tools.tools.get_product_prices_from_search', side_effect=Exception("Test error"))
    def test_error_handling(self, mock_get):
        """Test error handling in the agent"""
        result = self.agent.process_query("wheelchair")
        assert result["success"] is False
        assert "error" in result
        assert "Test error" in result["error"]


class TestTools:
    """Test the individual tools"""
    
    def test_product_search_tool(self):
        """Test the product_search_tool from product_search.py"""
        from app.tools.product_search import product_search_tool
        assert product_search_tool.name == "product_search"
        assert "Search the Alessa Med website" in product_search_tool.description
    
    def test_response_filter_tool(self):
        """Test the ResponseFilterTool"""
        tool = ResponseFilterTool()
        assert tool.name == "response_filter"
        assert "Filter and sort products" in tool.description
    
    def test_query_refinement_tool(self):
        """Test the QueryRefinementTool"""
        tool = QueryRefinementTool()
        assert tool.name == "query_refinement"
        assert "Refine and clarify" in tool.description


if __name__ == "__main__":
    pytest.main([__file__]) 