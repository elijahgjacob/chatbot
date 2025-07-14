"""
Tests for the Agentic Workflow
"""
import pytest
from unittest.mock import patch, MagicMock
from app.agents.agent import ChatbotAgent
from app.tools.tools import ProductSearchTool, ResponseFilterTool, QueryRefinementTool


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
    
    @patch('app.agents.agent.query_refinement_tool._run')
    @patch('app.agents.agent.product_search_tool._run')
    def test_simple_product_query(self, mock_search, mock_refine):
        """Test processing a simple product query"""
        # Mock search results
        mock_search.return_value = {
            "success": True,
            "products": [
                {"name": "Basic Wheelchair", "price": "150 KWD", "link": "http://example.com/1"},
                {"name": "Premium Wheelchair", "price": "300 KWD", "link": "http://example.com/2"}
            ],
            "count": 2
        }
        
        # Mock refinement (should not be called for simple query)
        mock_refine.return_value = {"success": True, "search_query": "wheelchair"}
        
        result = self.agent.process_query("wheelchair")
        
        assert result["success"] is True
        assert "wheelchair" in result["response"].lower()
        assert len(result["products"]) == 2
        assert "product_search" in result["workflow_steps"]
    
    @patch('app.agents.agent.query_refinement_tool._run')
    @patch('app.agents.agent.product_search_tool._run')
    @patch('app.agents.agent.response_filter_tool._run')
    def test_complex_query_with_filtering(self, mock_filter, mock_search, mock_refine):
        """Test processing a complex query that needs refinement and filtering"""
        # Mock refinement
        mock_refine.return_value = {
            "success": True,
            "search_query": "wheelchair",
            "product": "wheelchair",
            "requirements": "cheapest"
        }
        
        # Mock search results
        mock_search.return_value = {
            "success": True,
            "products": [
                {"name": "Basic Wheelchair", "price": "150 KWD", "link": "http://example.com/1"},
                {"name": "Premium Wheelchair", "price": "300 KWD", "link": "http://example.com/2"},
                {"name": "Luxury Wheelchair", "price": "500 KWD", "link": "http://example.com/3"}
            ],
            "count": 3
        }
        
        # Mock filtering
        mock_filter.return_value = {
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
    
    def test_error_handling(self):
        """Test error handling in the agent"""
        # Test with a query that will cause an error
        with patch('app.agents.agent.product_search_tool._run', side_effect=Exception("Test error")):
            result = self.agent.process_query("wheelchair")
            
            assert result["success"] is False
            assert "error" in result
            assert "Test error" in result["error"]


class TestTools:
    """Test the individual tools"""
    
    def test_product_search_tool(self):
        """Test the ProductSearchTool"""
        tool = ProductSearchTool()
        assert tool.name == "product_search"
        assert "Search for products" in tool.description
    
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