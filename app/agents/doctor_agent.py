"""
Doctor Agent for Al Essa Kuwait - Specialized in medical advice and product recommendations based on symptoms.
"""

from typing import Dict, List, Any
from app.core.llm import llm
from app.tools.product_search import product_search_tool
from app.agents.base_agent import BaseAgent
from langchain.schema import HumanMessage, SystemMessage

DOCTOR_AGENT_PROMPT = """You are a knowledgeable virtual doctor for Al Essa Kuwait, specializing in providing medical advice and recommending appropriate medical products.

**🩺 YOUR ROLE**
- Provide general health advice and symptom assessment
- Recommend appropriate medical products based on symptoms
- Ask relevant medical questions to understand the condition
- Always include appropriate medical disclaimers
- Guide patients toward professional medical care when needed
- Remember previous conversations and build on them

**💊 MEDICAL KNOWLEDGE**
- Common symptoms and conditions
- Appropriate medical products for different conditions
- When to seek professional medical attention
- Basic first aid and self-care recommendations

**🔍 SYMPTOM ANALYSIS**
- Ask ONE question at a time to understand the condition
- Consider severity, duration, and associated symptoms
- Recommend appropriate products based on symptoms
- Always prioritize safety and professional medical care
- Reference previous symptoms and conditions mentioned

**🛍️ PRODUCT RECOMMENDATIONS**
Based on symptoms, recommend appropriate products:
- **Pain/Injury**: Braces, splints, ice packs, heating pads, pain relievers
- **Mobility Issues**: Wheelchairs, walkers, crutches, canes
- **Respiratory**: Nebulizers, inhalers, humidifiers
- **Monitoring**: Blood pressure monitors, thermometers, pulse oximeters
- **Rehabilitation**: Exercise equipment, therapy tools
- **Daily Living**: Bathroom aids, kitchen aids, dressing aids

**⚠️ SAFETY DISCLAIMERS**
- Always remind patients that your advice doesn't replace professional medical care
- For severe symptoms, immediately recommend seeking medical attention
- Include appropriate warnings about self-diagnosis
- Emphasize the importance of consulting healthcare professionals

**💬 CONVERSATION STYLE**
- Professional and caring
- Ask ONE question at a time
- Be thorough but not overwhelming
- Show empathy and understanding
- Provide clear, actionable advice
- Be conversational and natural

**🎯 RESPONSE GUIDELINES**
- For symptoms: Ask clarifying questions and recommend appropriate products
- For general health: Provide helpful information with disclaimers
- For emergencies: Immediately recommend professional medical care
- For product questions: Explain medical benefits and proper usage
- Always include safety disclaimers
- Reference previous conversation context when appropriate

Remember: Your primary goal is to help patients while ensuring their safety and encouraging professional medical care when appropriate!"""

class DoctorAgent(BaseAgent):
    """Doctor agent for medical advice and product recommendations."""
    
    def __init__(self):
        """Initialize the doctor agent."""
        super().__init__("doctor")
        self.tools = [product_search_tool]
        
    def handle_chat(self, query: str, session_id: str) -> Dict[str, Any]:
        """Handle chat request for medical queries."""
        return self.process_query(query, session_id)
    
    def process_query(self, query: str, session_id: str = "default") -> Dict[str, Any]:
        """Process a medical-related query with conversation memory."""
        try:
            workflow_steps = []
            products = []
            
            # Get conversation history for context
            history, user_context = self._get_conversation_context(session_id)
            
            # Build context-aware prompt
            context_prompt = self._build_context_prompt(query, history, user_context)
            
            # Use LLM to analyze the medical query
            messages = [
                SystemMessage(content=DOCTOR_AGENT_PROMPT),
                HumanMessage(content=context_prompt)
            ]
            
            response = llm.invoke(messages)
            llm_response = response.content
            
            # Let the LLM decide if this is a symptom that needs product recommendations
            decision_prompt = f"""
            Based on the patient query: "{query}"
            
            Should I search for medical products? Consider:
            - Are they describing symptoms or medical conditions?
            - Do they need medical advice with product recommendations?
            - Are they asking about treatment options or medical equipment?
            
            Respond with ONLY: "SEARCH" or "CONVERSATION"
            """
            
            decision_messages = [
                SystemMessage(content="You are a medical decision-making assistant. Respond with ONLY 'SEARCH' or 'CONVERSATION' based on whether the patient needs medical product recommendations."),
                HumanMessage(content=decision_prompt)
            ]
            
            decision_response = llm.invoke(decision_messages)
            should_search = "SEARCH" in decision_response.content.upper()
            
            if should_search:
                workflow_steps.extend(["symptom_analysis", "product_recommendation"])
                
                # Generate product search queries based on symptoms
                product_queries = self._generate_product_queries(query)
                
                # Search for relevant products
                all_products = []
                for search_query in product_queries:
                    search_result = product_search_tool.invoke({"query": search_query})
                    products_found = search_result.get("products", [])
                    all_products.extend(products_found)
                
                # Remove duplicates and limit results
                products = self._deduplicate_products(all_products, limit=5)
                
                # Generate medical advice with product recommendations
                final_messages = [
                    SystemMessage(content=DOCTOR_AGENT_PROMPT),
                    HumanMessage(content=f"Patient query: {query}\nConversation history: {history}\nRecommended products: {products}\nProvide medical advice with these product recommendations, including appropriate disclaimers and safety warnings. Reference previous context when relevant.")
                ]
                final_response = llm.invoke(final_messages)
                reply = final_response.content
            else:
                # General medical conversation
                workflow_steps.append("medical_conversation")
                reply = llm_response
            
            # Handle conversation memory and update context
            self._handle_conversation_memory(session_id, query, reply, products, workflow_steps)
            self._update_user_context(session_id, query, products)
            
            return self._build_response(True, reply, products, workflow_steps)
            
        except Exception as e:
            error_msg = f"I'm sorry, I encountered an error: {str(e)}"
            return self._build_response(False, error_msg, [], ["error"], str(e))
    

    
    def _update_user_context(self, session_id: str, query: str, products: List[Dict]) -> None:
        """Update user context based on the medical conversation."""
        context_updates = {}
        
        # Extract medical conditions/symptoms
        query_lower = query.lower()
        if any(word in query_lower for word in ["wrist", "hand", "arm"]):
            context_updates["current_symptoms"] = "wrist/hand/arm issues"
        elif any(word in query_lower for word in ["ankle", "foot", "leg"]):
            context_updates["current_symptoms"] = "ankle/foot/leg issues"
        elif any(word in query_lower for word in ["knee", "leg"]):
            context_updates["current_symptoms"] = "knee issues"
        elif any(word in query_lower for word in ["back", "spine"]):
            context_updates["current_symptoms"] = "back issues"
        elif any(word in query_lower for word in ["neck", "cervical"]):
            context_updates["current_symptoms"] = "neck issues"
        elif any(word in query_lower for word in ["headache", "migraine"]):
            context_updates["current_symptoms"] = "headache"
        elif any(word in query_lower for word in ["breathing", "asthma", "cough"]):
            context_updates["current_symptoms"] = "respiratory issues"
        
        # Extract severity
        if any(word in query_lower for word in ["severe", "bad", "terrible", "awful", "excruciating"]):
            context_updates["symptom_severity"] = "severe"
        elif any(word in query_lower for word in ["moderate", "medium", "okay"]):
            context_updates["symptom_severity"] = "moderate"
        elif any(word in query_lower for word in ["mild", "slight", "little"]):
            context_updates["symptom_severity"] = "mild"
        
        # Extract duration
        if any(word in query_lower for word in ["days", "weeks", "months", "years"]):
            context_updates["symptom_duration"] = "ongoing"
        elif any(word in query_lower for word in ["just", "recently", "today", "yesterday"]):
            context_updates["symptom_duration"] = "recent"
        
        if context_updates:
            from app.core.conversation_memory import conversation_memory
            conversation_memory.update_user_context(session_id, context_updates)
    
    def _generate_product_queries(self, symptom_query: str) -> List[str]:
        """Generate product search queries based on symptoms."""
        symptom_lower = symptom_query.lower()
        queries = []
        
        # Pain-related products
        if any(word in symptom_lower for word in ["wrist", "hand", "arm"]):
            queries.extend(["wrist brace", "wrist splint", "hand brace", "ice pack"])
        if any(word in symptom_lower for word in ["ankle", "foot", "leg"]):
            queries.extend(["ankle brace", "ankle support", "knee brace", "ice pack"])
        if any(word in symptom_lower for word in ["knee", "leg"]):
            queries.extend(["knee brace", "knee support", "ice pack", "heating pad"])
        if any(word in symptom_lower for word in ["shoulder", "arm"]):
            queries.extend(["shoulder brace", "arm sling", "ice pack"])
        if any(word in symptom_lower for word in ["back", "spine"]):
            queries.extend(["back brace", "back support", "heating pad", "ice pack"])
        if any(word in symptom_lower for word in ["neck", "cervical"]):
            queries.extend(["neck brace", "cervical collar", "heating pad"])
        
        # Mobility products
        if any(word in symptom_lower for word in ["walking", "mobility", "balance", "fall"]):
            queries.extend(["walker", "cane", "crutch", "wheelchair"])
        if any(word in symptom_lower for word in ["weakness", "paralysis", "stroke"]):
            queries.extend(["wheelchair", "walker", "mobility aid"])
        
        # Respiratory products
        if any(word in symptom_lower for word in ["breathing", "asthma", "cough", "cold"]):
            queries.extend(["nebulizer", "inhaler", "humidifier"])
        
        # Monitoring products
        if any(word in symptom_lower for word in ["fever", "temperature"]):
            queries.append("thermometer")
        if any(word in symptom_lower for word in ["blood pressure", "hypertension"]):
            queries.append("blood pressure monitor")
        if any(word in symptom_lower for word in ["diabetes", "blood sugar"]):
            queries.append("glucose monitor")
        
        # General pain relief
        if "pain" in symptom_lower:
            queries.extend(["ice pack", "heating pad", "pain relief"])
        
        # Scoliosis and spine-related products
        if any(word in symptom_lower for word in ["scoliosis", "curved spine", "spine curve"]):
            queries.extend(["back brace", "spinal brace", "posture support", "back support", "scoliosis brace"])
        
        # If no specific matches, try general medical equipment
        if not queries:
            queries.append("medical equipment")
        
        return queries[:3]  # Limit to 3 search queries

# Initialize doctor agent
doctor_agent = DoctorAgent()