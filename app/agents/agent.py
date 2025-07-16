"""
ChatbotAgent implementation for the agentic workflow.
"""

from typing import Dict, List, Any
from app.tools.product_search import product_search_tool
from app.tools.response_filter import response_filter_tool
from app.tools.query_refinement import query_refinement_tool
from app.core.llm import llm
from app.core.prompts import SYSTEM_PROMPT

AVAILABLE_TOOLS = [product_search_tool, response_filter_tool, query_refinement_tool]

class ChatbotAgent:
    """Agent for processing queries with tools using LLM reasoning."""
    
    def __init__(self):
        """Initialize the agent with tools and LLM."""
        self.memory = []
        self.tools = AVAILABLE_TOOLS
        
    def process_query(self, query: str, session_id: str = "default") -> Dict[str, Any]:
        """
        Process a user query using LLM reasoning and tools.
        
        Args:
            query: The user's query
            session_id: The session ID for tracking conversation
            
        Returns:
            Dictionary containing the response and workflow information
        """
        try:
            workflow_steps = []
            
            # Use LLM to determine the type of query and appropriate response
            llm_prompt = f"""
{SYSTEM_PROMPT}

User Query: "{query}"

Based on the user's query, determine:
1. Is this a conversational/greeting query (like "hi", "how are you", "hello")?
2. Is this a medical/health question that requires doctor knowledge?
3. Is this a product search query?
4. Is this a combination of the above?

Respond appropriately:
- For greetings: Be friendly and conversational
- For medical questions: Provide helpful advice with appropriate disclaimers
- For product queries: Use the product_search tool
- For complex queries: Use query_refinement first, then product_search

If you need to search for products, use the product_search tool with the appropriate query.
If you need to filter results, use the response_filter tool.

Remember to be conversational, helpful, and use the tools when appropriate.
"""
            
            # Get LLM response
            llm_response = llm.invoke(llm_prompt)
            response_content = llm_response.content if hasattr(llm_response, 'content') else str(llm_response)
            
            # Check if LLM wants to use tools
            if "product_search" in response_content.lower() or any(word in query.lower() for word in ["wheelchair", "walker", "crutch", "medical", "equipment", "appliance"]):
                workflow_steps.append("llm_reasoning")
                
                # Use product search tool
                search_result = product_search_tool(query)
                workflow_steps.append("product_search")
                
                if search_result.get("success") and search_result.get("products"):
                    products = search_result["products"]
                    
                    # Generate final response with products
                    final_prompt = f"""
{SYSTEM_PROMPT}

User Query: "{query}"

Products Found: {products}

Generate a helpful, conversational response that:
1. Addresses the user's query
2. Presents the products in a friendly, sales-oriented way
3. Maintains the conversational tone
4. Includes appropriate medical disclaimers if relevant

Response:
"""
                    final_response = llm.invoke(final_prompt)
                    response = final_response.content if hasattr(final_response, 'content') else str(final_response)
                    
                    return {
                        "success": True,
                        "response": response,
                        "products": products,
                        "workflow_steps": workflow_steps
                    }
                else:
                    # No products found, but still be conversational
                    no_products_prompt = f"""
{SYSTEM_PROMPT}

User Query: "{query}"

No products were found for this query. Generate a helpful, conversational response that:
1. Acknowledges the user's request
2. Suggests alternative approaches or rephrasing
3. Maintains a helpful, sales-oriented tone
4. Offers to help with other products or questions

Response:
"""
                    no_products_response = llm.invoke(no_products_prompt)
                    response = no_products_response.content if hasattr(no_products_response, 'content') else str(no_products_response)
                    
                    return {
                        "success": True,
                        "response": response,
                        "products": [],
                        "workflow_steps": workflow_steps
                    }
            else:
                # Conversational or medical query - use LLM response directly
                workflow_steps.append("llm_conversation")
                return {
                    "success": True,
                    "response": response_content,
                    "products": [],
                    "workflow_steps": workflow_steps
                }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": "I encountered an error while processing your request. Please try again.",
                "products": [],
                "workflow_steps": []
            }

# Create a global agent instance
chatbot_agent = ChatbotAgent()