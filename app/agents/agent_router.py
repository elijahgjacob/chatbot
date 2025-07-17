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
- **SALES AGENT**: For product purchases, pricing, general product questions, home appliances, technology, brand inquiries, availability questions
- **DOCTOR AGENT**: For medical symptoms, health advice, injury descriptions, medical conditions, treatment questions

**🔍 ANALYSIS CRITERIA**

**Route to DOCTOR AGENT if the query:**
- Describes medical symptoms or health problems
- Asks for medical advice or treatment recommendations
- Mentions injuries, pain, or medical conditions
- Seeks health-related guidance
- Asks "what should I do for..." medical issues
- **MENTIONS ANY MEDICAL CONDITION** (scoliosis, arthritis, diabetes, etc.)
- **Asks for products to help with medical conditions**
- **Contains medical terms** (pain, symptoms, condition, treatment, etc.)

**Route to SALES AGENT if the query:**
- Asks about products, brands, or availability
- Inquires about pricing or costs
- Seeks product recommendations or comparisons
- Asks about specific models or types
- Mentions shopping, buying, or purchasing
- Asks "do you have..." or "show me..." products

**💬 RESPONSE FORMAT**
Respond with ONLY one word: either "SALES" or "DOCTOR"

**🔍 IMPORTANT: If the user mentions ANY medical condition (like scoliosis, arthritis, diabetes, etc.) or asks for products to help with medical issues, ALWAYS route to DOCTOR.**

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
- "Cheapest option" → SALES
- "I have scoliosis" → DOCTOR
- "Help me with back pain" → DOCTOR
- "I need products for my medical condition" → DOCTOR
- "What can help with my spine problem?" → DOCTOR
- "I need medical equipment for my condition" → DOCTOR

Use your judgment to determine the most appropriate agent based on the user's intent."""

class AgentRouter:
    """Intelligent router that determines which agent should handle a query."""
    
    def __init__(self):
        """Initialize the agent router."""
        self.sales_agent = sales_agent
        self.doctor_agent = doctor_agent
        
    def route_query(self, query: str, session_id: str = "default") -> Dict[str, Any]:
        """Route a query to the appropriate agent."""
        try:
            # ------------ NEW HEURISTIC ROUTING LOGIC ------------
            query_lower = query.lower()
            doctor_keywords = [
                "pain", "ache", "injury", "hurt", "headache", "fever", "symptom", "dizziness", "nausea",
                "diagnosis", "treatment", "therapy", "medicine", "medical condition", "scoliosis", "arthritis",
                "diabetes", "asthma", "fracture", "sprain", "bruise", "swelling", "burn", "infection",
                "bleeding", "rash", "wound", "cough", "breathing", "respiratory", "blood pressure", "pulse",
                "glucose", "monitor", "wheelchair for", "doctor", "should i", "consult"
            ]
            sales_keywords = [
                "price", "cost", "buy", "purchase", "have", "do you have", "show me", "looking for", "sell",
                "cheapest", "expensive", "wheelchair", "walker", "brace", "splint", "crutch", "air conditioner",
                "refrigerator", "washing machine", "brand", "model", "availability", "stock", "kwd", "kd", "dinar"
            ]

            # Quick keyword-based classification; if both classes detected we will defer to LLM
            agent_choice: str | None = None
            if any(k in query_lower for k in doctor_keywords) and not any(k in query_lower for k in sales_keywords):
                agent_choice = "DOCTOR"
            elif any(k in query_lower for k in sales_keywords):
                # If explicitly medical keywords also present, we still treat as doctor
                if any(k in query_lower for k in doctor_keywords):
                    agent_choice = "DOCTOR"
                else:
                    agent_choice = "SALES"

            # Fallback to LLM only if heuristic couldn't decide
            if agent_choice is None and llm is not None:
                messages = [
                    SystemMessage(content=ROUTER_PROMPT),
                    HumanMessage(content=f"User query: {query}")
                ]
                try:
                    response = llm.invoke(messages)
                    agent_choice = response.content.strip().upper()
                except Exception as e:
                    # If LLM fails, default later
                    agent_choice = None

            # If still undecided, default to SALES
            if agent_choice not in {"SALES", "DOCTOR"}:
                agent_choice = "SALES"

            # ---------------- END HEURISTIC LOGIC ----------------

            # Route to appropriate agent
            if agent_choice == "DOCTOR":
                result = self.doctor_agent.process_query(query, session_id)
                result["routing_decision"] = "doctor"
                return result
            else:  # SALES or default
                result = self.sales_agent.process_query(query, session_id)
                result["routing_decision"] = "sales"
                return result

        except Exception as e:
            # Fallback to sales agent on error
            result = self.sales_agent.process_query(query, session_id)
            result["routing_decision"] = "sales (fallback)"
            result["error"] = str(e)
            return result

# Initialize agent router
agent_router = AgentRouter()