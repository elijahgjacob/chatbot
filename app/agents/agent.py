"""
Main Chatbot Agent - Uses intelligent routing to delegate to specialized agents.
"""

from typing import Dict, List, Any
from app.agents.agent_router import agent_router

class ChatbotAgent:
    """Main agent that routes queries to specialized agents."""
    
    def __init__(self):
        """Initialize the main agent."""
        self.router = agent_router
        
    def process_query(self, query: str, session_id: str = "default") -> Dict[str, Any]:
        """
        Process a user query by routing to the appropriate specialized agent.
        """
        try:
            # Use the intelligent router to determine which agent should handle the query
            result = self.router.route_query(query, session_id)
            
            # Add main agent workflow step
            if "workflow_steps" in result:
                result["workflow_steps"].insert(0, "intelligent_routing")
            else:
                result["workflow_steps"] = ["intelligent_routing"]
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "reply": f"I'm sorry, I encountered an error: {str(e)}",
                "products": [],
                "workflow_steps": ["error"],
                "agent_type": "main",
                "routing_decision": "error"
            }

# Initialize the main chatbot agent
chatbot_agent = ChatbotAgent()