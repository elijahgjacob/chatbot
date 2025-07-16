"""
ChatbotAgent implementation for the agentic workflow.
"""

from typing import Dict, List, Any
from app.tools.product_search import product_search_tool
from app.tools.response_filter import response_filter_tool
from app.tools.query_refinement import query_refinement_tool
from app.core.llm import llm
from app.core.prompts import SYSTEM_PROMPT
from langchain.schema import HumanMessage, SystemMessage

AVAILABLE_TOOLS = [product_search_tool, response_filter_tool, query_refinement_tool]

class ChatbotAgent:
    """Agent for processing queries with tools using LLM reasoning."""
    
    def __init__(self):
        """Initialize the agent with tools and LLM."""
        self.memory = []
        self.tools = AVAILABLE_TOOLS
        
    def process_query(self, query: str, session_id: str = "default") -> Dict[str, Any]:
        """
        Process a user query using LLM reasoning and tools when appropriate.
        """
        try:
            workflow_steps = []
            products = []
            
            # Use LLM to determine the appropriate response
            messages = [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=f"User query: {query}")
            ]
            
            # Get LLM response
            response = llm.invoke(messages)
            llm_response = response.content
            
            # Check if the LLM wants to use any tools
            if "product_search" in llm_response.lower() or any(keyword in query.lower() for keyword in ["wheelchair", "walker", "air conditioner", "product", "buy", "price"]):
                workflow_steps.append("llm_reasoning")
                workflow_steps.append("product_search")
                
                # Use product search tool
                search_result = product_search_tool.invoke({"query": query})
                products = search_result.get("products", [])
                
                # Let LLM format the final response with products
                final_messages = [
                    SystemMessage(content=SYSTEM_PROMPT),
                    HumanMessage(content=f"User query: {query}\nProducts found: {products}\nFormat a conversational response with these products.")
                ]
                final_response = llm.invoke(final_messages)
                reply = final_response.content
            else:
                # Simple conversational response
                workflow_steps.append("llm_conversation")
                reply = llm_response
            
            return {
                "success": True,
                "reply": reply,
                "products": products,
                "workflow_steps": workflow_steps
            }
            
        except Exception as e:
            return {
                "success": False,
                "reply": f"I'm sorry, I encountered an error: {str(e)}",
                "products": [],
                "workflow_steps": ["error"]
            }

# Initialize the agent
chatbot_agent = ChatbotAgent()