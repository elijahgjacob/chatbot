"""
Base Agent class for Al Essa Kuwait - Contains common functionality for all agents.
"""

from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from app.core.conversation_memory import conversation_memory
import logging

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all chatbot agents with common functionality."""
    
    def __init__(self, agent_type: str):
        """Initialize base agent."""
        self.agent_type = agent_type
        self.tools = []
    
    @abstractmethod
    def handle_chat(self, query: str, session_id: str) -> Dict[str, Any]:
        """Handle chat request - must be implemented by subclasses."""
        pass
    
    def _build_context_prompt(self, query: str, history: List[Dict], user_context: Dict[str, Any]) -> str:
        """Build a context-aware prompt for the LLM."""
        prompt = f"Current query: {query}\n\n"
        
        if history:
            prompt += "Recent conversation history:\n"
            for msg in history[-3:]:  # Last 3 messages for context
                role = "User" if msg["role"] == "user" else "You"
                prompt += f"{role}: {msg['content']}\n"
            prompt += "\n"
        
        if user_context:
            prompt += "User context:\n"
            for key, value in user_context.items():
                prompt += f"- {key}: {value}\n"
            prompt += "\n"
        
        prompt += "Please respond naturally, considering the conversation history and user context."
        return prompt
    
    def _handle_conversation_memory(self, session_id: str, query: str, reply: str, 
                                   products: List[Dict], workflow_steps: List[str]) -> None:
        """Handle conversation memory storage."""
        try:
            from app.core.conversation_memory import conversation_memory
            # Add user message
            conversation_memory.add_message(
                session_id=session_id,
                role="user",
                content=query
            )
            
            # Add assistant message
            conversation_memory.add_message(
                session_id=session_id,
                role="assistant", 
                content=reply,
                agent_type=self.agent_type,
                products=products,
                workflow_steps=workflow_steps
            )
        except Exception as e:
            logger.warning(f"Failed to store conversation memory: {e}")
    
    def _build_response(self, success: bool, reply: str, products: List[Dict] = None,
                       workflow_steps: List[str] = None, error: str = None) -> Dict[str, Any]:
        """Build standardized response structure."""
        response = {
            "success": success,
            "reply": reply,
            "products": products or [],
            "workflow_steps": workflow_steps or [],
            "agent_type": self.agent_type
        }
        
        if error:
            response["error"] = error
            
        return response
    
    def _deduplicate_products(self, products: List[Dict], limit: int = 5) -> List[Dict]:
        """Remove duplicate products based on name and limit results."""
        unique_products = []
        seen_names = set()
        
        for product in products:
            product_name = product.get("name", "")
            if product_name and product_name not in seen_names:
                unique_products.append(product)
                seen_names.add(product_name)
                
                if len(unique_products) >= limit:
                    break
        
        return unique_products
    
    def _get_conversation_context(self, session_id: str) -> tuple[List[Dict], Dict[str, Any]]:
        """Get conversation history and user context."""
        try:
            from app.core.conversation_memory import conversation_memory
            history = conversation_memory.get_conversation_history(session_id, max_messages=10)
            user_context = conversation_memory.get_user_context(session_id)
            return history, user_context
        except Exception as e:
            logger.warning(f"Failed to get conversation context: {e}")
            return [], {}
    
    @abstractmethod
    def _update_user_context(self, session_id: str, query: str, products: List[Dict]) -> None:
        """Update user context - must be implemented by subclasses with domain-specific logic."""
        pass