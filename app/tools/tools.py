"""
LangChain Tools for the Chatbot Agent
"""
import logging
from typing import List, Dict, Any, Optional
from langchain.tools import BaseTool
from langchain.schema import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
import re

from app.core.scraping import get_product_prices_from_search
from app.core.llm import get_llm_response
from app.core.prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class ProductSearchInput(BaseModel):
    query: str = Field(description="The product search query (e.g., 'wheelchair', 'crutches')")


class ProductSearchTool(BaseTool):
    name: str = "product_search"
    description: str = "Search for products on the website. Use this when the user asks about specific products, medical equipment, or items that might be available for purchase."
    args_schema: type = ProductSearchInput

    def _run(self, query: str) -> Dict[str, Any]:
        logging.info("TOOL | product_search")
        """Search for products and return results"""
        logger.info(f"ProductSearchTool: Searching for '{query}'")
        
        try:
            result = get_product_prices_from_search(query)
            products = result.get('products', [])
            
            # Filter products to only include those with the main keyword in the name or category
            keyword = query.lower().strip()
            filtered_products = [
                p for p in products
                if keyword in p.get('name', '').lower() or keyword in p.get('category', '').lower()
            ] if keyword else products

            logger.info(f"ProductSearchTool: Found {len(filtered_products)} relevant products for '{query}'")
            
            return {
                "success": True,
                "query": query,
                "products": filtered_products,
                "count": len(filtered_products),
                "formatted_response": result.get('formatted_response', '')
            }
        except Exception as e:
            logger.error(f"ProductSearchTool error: {e}")
            return {
                "success": False,
                "query": query,
                "error": str(e),
                "products": [],
                "count": 0
            }


class ResponseFilterInput(BaseModel):
    products: List[Dict[str, Any]] = Field(description="List of products to filter")
    filter_criteria: str = Field(description="Filter criteria (e.g., 'cheapest', 'under 100 KWD', 'best quality')")


class ResponseFilterTool(BaseTool):
    name: str = "response_filter"
    description: str = "Filter and sort products based on user criteria like price, quality, or specific requirements. Use this when the user asks for 'cheapest', 'best', 'under X KWD', etc."
    args_schema: type = ResponseFilterInput

    def _run(self, products: List[Dict[str, Any]], filter_criteria: str) -> Dict[str, Any]:
        logging.info("TOOL | response_filter")
        """Filter products based on criteria"""
        logger.info(f"ResponseFilterTool: Filtering {len(products)} products with criteria '{filter_criteria}'")
        
        if not products:
            return {
                "success": False,
                "message": "No products to filter",
                "filtered_products": []
            }

        try:
            # Extract price from products (handle different price formats)
            def extract_price(product):
                price_str = str(product.get('price', '0'))
                # Remove currency symbols and extract numbers
                price_match = re.search(r'(\d+(?:\.\d+)?)', price_str.replace(',', ''))
                return float(price_match.group(1)) if price_match else float('inf')

            # Apply filters based on criteria
            filter_lower = filter_criteria.lower()
            
            if 'cheapest' in filter_lower or 'lowest' in filter_lower:
                # Sort by price ascending
                sorted_products = sorted(products, key=extract_price)
                filtered_products = sorted_products[:3]  # Top 3 cheapest
                filter_type = "cheapest"
                
            elif 'expensive' in filter_lower or 'highest' in filter_lower:
                # Sort by price descending
                sorted_products = sorted(products, key=extract_price, reverse=True)
                filtered_products = sorted_products[:3]  # Top 3 most expensive
                filter_type = "most expensive"
                
            elif 'under' in filter_lower or 'less than' in filter_lower:
                # Extract price limit
                price_match = re.search(r'(\d+(?:\.\d+)?)', filter_criteria)
                if price_match:
                    max_price = float(price_match.group(1))
                    filtered_products = [p for p in products if extract_price(p) <= max_price]
                    filter_type = f"under {max_price} KWD"
                else:
                    filtered_products = products
                    filter_type = "price filter (limit not found)"
                    
            elif 'best' in filter_lower or 'quality' in filter_lower:
                # For now, return first few products (could be enhanced with more logic)
                filtered_products = products[:3]
                filter_type = "best quality"
                
            else:
                # Default: return first few products
                filtered_products = products[:5]
                filter_type = "default"

            logger.info(f"ResponseFilterTool: Filtered to {len(filtered_products)} products using '{filter_type}' filter")
            
            return {
                "success": True,
                "filter_type": filter_type,
                "filtered_products": filtered_products,
                "count": len(filtered_products),
                "original_count": len(products)
            }
            
        except Exception as e:
            logger.error(f"ResponseFilterTool error: {e}")
            return {
                "success": False,
                "error": str(e),
                "filtered_products": products[:3]  # Fallback to first 3
            }


class QueryRefinementInput(BaseModel):
    user_query: str = Field(description="The original user query")
    context: str = Field(description="Additional context or conversation history")


class QueryRefinementTool(BaseTool):
    name: str = "query_refinement"
    description: str = "Refine and clarify user queries to extract the core product or intent. Use this when the user's query is unclear, contains multiple requests, or needs interpretation."
    args_schema: type = QueryRefinementInput

    def _run(self, user_query: str, context: str = "", history=None) -> Dict[str, Any]:
        logging.info("TOOL | query_refinement")
        logger.info(f"QueryRefinementTool: Refining query '{user_query}'")
        
        try:
            # Create a prompt for query refinement
            refinement_prompt = f"""
You are a query refinement assistant. Your job is to extract the core product or intent from user queries.

User Query: {user_query}
Context: {context}

Please extract:
1. The main product or category the user is looking for
2. Any specific requirements or modifiers (price, quality, etc.)
3. A clean search query for product search

If the user's query is not about a product or is a meta/conversational question (e.g., 'what did I just say?', 'how are you?', 'tell me a joke'), return:
PRODUCT: None
REQUIREMENTS: None
SEARCH_QUERY: None

Return your response in this format:
PRODUCT: [main product/category]
REQUIREMENTS: [specific requirements or modifiers]
SEARCH_QUERY: [clean query for product search]
"""

            # Get LLM response for refinement, passing history
            refined_response = get_llm_response(refinement_prompt, history=history)
            
            # Parse the response
            product_match = re.search(r'PRODUCT:\s*(.+)', refined_response, re.IGNORECASE)
            requirements_match = re.search(r'REQUIREMENTS:\s*(.+)', refined_response, re.IGNORECASE)
            search_query_match = re.search(r'SEARCH_QUERY:\s*(.+)', refined_response, re.IGNORECASE)
            
            product = product_match.group(1).strip() if product_match else user_query
            requirements = requirements_match.group(1).strip() if requirements_match else ""
            search_query = search_query_match.group(1).strip() if search_query_match else product
            
            logger.info(f"QueryRefinementTool: Refined '{user_query}' to product='{product}', requirements='{requirements}', search_query='{search_query}'")
            
            return {
                "success": True,
                "original_query": user_query,
                "product": product,
                "requirements": requirements,
                "search_query": search_query,
                "refined_response": refined_response
            }
            
        except Exception as e:
            logger.error(f"QueryRefinementTool error: {e}")
            return {
                "success": False,
                "error": str(e),
                "original_query": user_query,
                "product": user_query,
                "requirements": "",
                "search_query": user_query
            }


# Create tool instances
product_search_tool = ProductSearchTool()
response_filter_tool = ResponseFilterTool()
query_refinement_tool = QueryRefinementTool()

# List of all available tools
AVAILABLE_TOOLS = [product_search_tool, response_filter_tool, query_refinement_tool] 