"""
Al Essa Kuwait Sales Agent - LangChain Agent with Sales-focused Tools
"""
import logging
from typing import Dict, Any, List, Optional
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from app.core.llm import llm
from app.core.prompts import SYSTEM_PROMPT, SALES_DISCOVERY_PROMPT
from app.tools.tools import ProductSearchTool
from app.tools.sales_tools import (
    PriceComparisonTool, 
    ProductRecommendationTool,
    CustomerQualificationTool,
    UpsellingSuggestionTool
)

logger = logging.getLogger(__name__)


class SalesConversationMemory(ConversationBufferMemory):
    """Enhanced memory for sales conversations with customer context tracking"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.customer_profile = {
            'budget': None,
            'product_type': None,
            'timeline': None,
            'special_requirements': [],
            'price_sensitivity': 'medium',
            'previous_interests': []
        }
    
    def update_customer_profile(self, key: str, value: Any):
        """Update customer profile information"""
        self.customer_profile[key] = value
        logger.info(f"Updated customer profile: {key} = {value}")


class AlEssaSalesAgent:
    """Al Essa Kuwait Sales Agent with advanced sales tools and conversation management"""
    
    def __init__(self, session_id: str = "default"):
        self.session_id = session_id
        self.memory = SalesConversationMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Initialize sales tools
        self.tools = [
            ProductSearchTool(),
            PriceComparisonTool(),
            ProductRecommendationTool(),
            CustomerQualificationTool(),
            UpsellingSuggestionTool()
        ]
        
        # Create the sales agent prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create the agent
        self.agent = create_openai_functions_agent(
            llm=llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )
    
    def process_customer_query(self, query: str) -> Dict[str, Any]:
        """
        Process customer query with sales-focused approach
        """
        try:
            logger.info(f"Sales Agent processing query: {query}")
            
            # Analyze query for sales intent
            sales_context = self._analyze_sales_intent(query)
            
            # Add sales context to the query
            enhanced_query = f"""
            Customer Query: {query}
            
            Sales Context:
            - Intent: {sales_context.get('intent', 'information')}
            - Urgency: {sales_context.get('urgency', 'low')}
            - Budget mentioned: {sales_context.get('budget_mentioned', False)}
            - Product category: {sales_context.get('product_category', 'unknown')}
            
            Customer Profile: {self.memory.customer_profile}
            
            Remember to act as a sales professional and guide the customer toward a purchase decision.
            """
            
            # Process with agent
            result = self.agent_executor.invoke({
                "input": enhanced_query
            })
            
            # Extract and format response
            response = self._format_sales_response(result)
            
            # Update customer profile based on conversation
            self._update_customer_profile(query, result)
            
            return {
                "success": True,
                "response": response.get("output", ""),
                "sales_stage": sales_context.get("intent", "discovery"),
                "customer_profile": self.memory.customer_profile,
                "recommended_actions": self._get_recommended_actions(sales_context),
                "session_id": self.session_id
            }
            
        except Exception as e:
            logger.error(f"Error in sales agent: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "I apologize, but I'm having technical difficulties. Please let me connect you with a human sales representative who can assist you immediately.",
                "session_id": self.session_id
            }
    
    def _analyze_sales_intent(self, query: str) -> Dict[str, Any]:
        """Analyze customer query for sales intent and context"""
        query_lower = query.lower()
        
        # Determine sales intent
        intent = "discovery"
        if any(word in query_lower for word in ["buy", "purchase", "order", "get", "need"]):
            intent = "interest"
        elif any(word in query_lower for word in ["price", "cost", "how much", "expensive"]):
            intent = "consideration"
        elif any(word in query_lower for word in ["compare", "vs", "difference", "better"]):
            intent = "evaluation"
        elif any(word in query_lower for word in ["urgent", "asap", "immediately", "today"]):
            intent = "urgency"
        
        # Determine urgency level
        urgency = "low"
        if any(word in query_lower for word in ["urgent", "emergency", "asap", "immediately"]):
            urgency = "high"
        elif any(word in query_lower for word in ["soon", "quickly", "this week"]):
            urgency = "medium"
        
        # Check for budget mentions
        budget_mentioned = any(word in query_lower for word in ["budget", "kwd", "dinar", "cheap", "expensive", "under", "below"])
        
        # Determine product category
        product_category = "unknown"
        if any(word in query_lower for word in ["wheelchair", "crutch", "walker", "mobility"]):
            product_category = "medical_mobility"
        elif any(word in query_lower for word in ["refrigerator", "fridge", "freezer", "air conditioner"]):
            product_category = "appliances"
        elif any(word in query_lower for word in ["vacuum", "cleaner", "washing machine"]):
            product_category = "home_appliances"
        
        return {
            "intent": intent,
            "urgency": urgency,
            "budget_mentioned": budget_mentioned,
            "product_category": product_category
        }
    
    def _format_sales_response(self, agent_result: Dict[str, Any]) -> Dict[str, Any]:
        """Format agent response with sales enhancements"""
        output = agent_result.get("output", "")
        
        # Add sales call-to-action if not present
        if not any(phrase in output.lower() for phrase in ["contact", "call", "order", "buy", "purchase"]):
            output += "\n\n💬 Would you like me to help you place an order or get more information about any of these products?"
        
        return {"output": output}
    
    def _update_customer_profile(self, query: str, result: Dict[str, Any]):
        """Update customer profile based on conversation"""
        query_lower = query.lower()
        
        # Extract budget information
        import re
        budget_match = re.search(r'(\d+)\s*(kwd|dinar)', query_lower)
        if budget_match:
            self.memory.update_customer_profile('budget', float(budget_match.group(1)))
        
        # Extract product type
        if "wheelchair" in query_lower:
            self.memory.update_customer_profile('product_type', 'wheelchair')
        elif "air conditioner" in query_lower or "ac" in query_lower:
            self.memory.update_customer_profile('product_type', 'air_conditioner')
        elif "refrigerator" in query_lower or "fridge" in query_lower:
            self.memory.update_customer_profile('product_type', 'refrigerator')
        
        # Extract urgency
        if any(word in query_lower for word in ["urgent", "asap", "today"]):
            self.memory.update_customer_profile('timeline', 'urgent')
        elif any(word in query_lower for word in ["this week", "soon"]):
            self.memory.update_customer_profile('timeline', 'this_week')
    
    def _get_recommended_actions(self, sales_context: Dict[str, Any]) -> List[str]:
        """Get recommended next actions for the sales process"""
        actions = []
        
        intent = sales_context.get('intent', 'discovery')
        
        if intent == 'discovery':
            actions.append("Qualify customer needs and budget")
            actions.append("Show product catalog")
        elif intent == 'interest':
            actions.append("Present specific product recommendations")
            actions.append("Highlight key benefits and value proposition")
        elif intent == 'consideration':
            actions.append("Provide detailed pricing information")
            actions.append("Offer financing options if available")
        elif intent == 'evaluation':
            actions.append("Create product comparison")
            actions.append("Address potential objections")
        elif intent == 'urgency':
            actions.append("Check immediate availability")
            actions.append("Offer expedited delivery options")
        
        return actions
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of the sales conversation"""
        return {
            "session_id": self.session_id,
            "customer_profile": self.memory.customer_profile,
            "conversation_length": len(self.memory.chat_memory.messages),
            "last_interaction": self.memory.chat_memory.messages[-1].content if self.memory.chat_memory.messages else None
        }


# Create a global sales agent instance
sales_agent = AlEssaSalesAgent()


def process_sales_query(query: str, session_id: str = "default") -> Dict[str, Any]:
    """
    Process a sales query using the Al Essa Kuwait Sales Agent
    """
    global sales_agent
    
    if sales_agent.session_id != session_id:
        sales_agent = AlEssaSalesAgent(session_id)
    
    return sales_agent.process_customer_query(query)