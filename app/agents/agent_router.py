"""
Intelligent Agent Router - Routes queries to appropriate agents based on content analysis.
"""

from typing import Dict, Any
from app.core.llm import llm
from app.agents.sales_agent import sales_agent
from app.agents.doctor_agent import doctor_agent
from langchain.schema import HumanMessage, SystemMessage

ROUTER_PROMPT = """You are an intelligent query router for Al Essa Kuwait's chatbot system.

**🎯 YOUR TASK**
Analyze the user's query and determine which specialized agent should handle it:
- **SALES AGENT**: For product purchases, pricing, general product questions, home appliances, technology
- **DOCTOR AGENT**: For medical symptoms, health advice, injury descriptions, medical conditions

**🔍 ANALYSIS CRITERIA**

**Route to DOCTOR AGENT if the query contains:**
- Medical symptoms: pain, ache, hurt, sore, injury, sprain, strain
- Health conditions: fever, cough, cold, breathing issues, diabetes, arthritis
- Body parts with problems: wrist pain, back pain, knee pain, headache
- Medical advice requests: "what should I do for...", "how to treat...", "I have..."
- Injury descriptions: "I fell", "I hurt my...", "I injured my..."
- Health monitoring: blood pressure, temperature, blood sugar

**Route to SALES AGENT if the query contains:**
- Product purchases: "I want to buy...", "show me...", "price of..."
- General product questions: "do you have...", "what products...", "catalog"
- Brand-specific queries: "Sunrise", "brand", "model", "type"
- Pricing queries: "cheapest", "cheap", "expensive", "how much", "cost"
- Home appliances: air conditioner, refrigerator, washing machine
- Technology: computer, phone, accessories
- Pricing and availability: "how much", "cost", "available"
- General shopping: "looking for", "need", "want"
- Product availability: "do you have", "in stock", "available"

**💬 RESPONSE FORMAT**
Respond with ONLY one word: either "SALES" or "DOCTOR"

**📝 EXAMPLES**
- "I have wrist pain" → DOCTOR
- "Show me wheelchairs" → SALES  
- "What should I do for a headache?" → DOCTOR
- "How much does an air conditioner cost?" → SALES
- "I hurt my ankle" → DOCTOR
- "Do you have walkers?" → SALES
- "I need medical advice" → DOCTOR
- "Looking for a refrigerator" → SALES
- "Do you have Sunrise wheelchairs?" → SALES
- "What's the cheapest wheelchair?" → SALES
- "Sunrise brand products" → SALES
- "Cheapest option" → SALES"""

class AgentRouter:
    """Intelligent router that determines which agent should handle a query."""
    
    def __init__(self):
        """Initialize the agent router."""
        self.sales_agent = sales_agent
        self.doctor_agent = doctor_agent
        
    def route_query(self, query: str, session_id: str = "default") -> Dict[str, Any]:
        """Route a query to the appropriate agent."""
        try:
            # Use LLM to determine which agent should handle the query
            messages = [
                SystemMessage(content=ROUTER_PROMPT),
                HumanMessage(content=f"User query: {query}")
            ]
            
            response = llm.invoke(messages)
            agent_choice = response.content.strip().upper()
            
            # Route to appropriate agent
            if agent_choice == "DOCTOR":
                result = self.doctor_agent.process_query(query, session_id)
                result["routing_decision"] = "doctor"
                return result
            elif agent_choice == "SALES":
                result = self.sales_agent.process_query(query, session_id)
                result["routing_decision"] = "sales"
                return result
            else:
                # Default to sales agent if routing is unclear
                result = self.sales_agent.process_query(query, session_id)
                result["routing_decision"] = "sales (default)"
                return result
                
        except Exception as e:
            # Fallback to sales agent on error
            result = self.sales_agent.process_query(query, session_id)
            result["routing_decision"] = "sales (fallback)"
            result["error"] = str(e)
            return result

# Initialize agent router
agent_router = AgentRouter()