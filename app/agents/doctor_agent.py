"""
Doctor Agent for Al Essa Kuwait - Specialized in medical advice and product recommendations based on symptoms.
"""

from typing import Dict, List, Any
from app.core.llm import llm
from app.tools.product_search import product_search_tool
from langchain.schema import HumanMessage, SystemMessage

DOCTOR_AGENT_PROMPT = """You are a knowledgeable virtual doctor for Al Essa Kuwait, specializing in providing medical advice and recommending appropriate medical products.

**🩺 YOUR ROLE**
- Provide general health advice and symptom assessment
- Recommend appropriate medical products based on symptoms
- Ask relevant medical questions to understand the condition
- Always include appropriate medical disclaimers
- Guide patients toward professional medical care when needed

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

**🎯 RESPONSE GUIDELINES**
- For symptoms: Ask clarifying questions and recommend appropriate products
- For general health: Provide helpful information with disclaimers
- For emergencies: Immediately recommend professional medical care
- For product questions: Explain medical benefits and proper usage
- Always include safety disclaimers

Remember: Your primary goal is to help patients while ensuring their safety and encouraging professional medical care when appropriate!"""

class DoctorAgent:
    """Doctor agent for medical advice and product recommendations."""
    
    def __init__(self):
        """Initialize the doctor agent."""
        self.tools = [product_search_tool]
        
    def process_query(self, query: str, session_id: str = "default") -> Dict[str, Any]:
        """Process a medical-related query."""
        try:
            workflow_steps = []
            products = []
            
            # Use LLM to analyze the medical query
            messages = [
                SystemMessage(content=DOCTOR_AGENT_PROMPT),
                HumanMessage(content=f"Patient query: {query}")
            ]
            
            response = llm.invoke(messages)
            llm_response = response.content
            
            # Check if this is a symptom or condition that needs product recommendations
            medical_keywords = [
                "pain", "hurt", "ache", "sore", "injury", "sprain", "strain", "fracture",
                "swelling", "bruise", "cut", "burn", "headache", "back pain", "knee pain",
                "wrist pain", "ankle pain", "shoulder pain", "neck pain", "joint pain",
                "mobility", "walking", "balance", "fall", "weakness", "numbness",
                "breathing", "cough", "cold", "fever", "temperature", "blood pressure",
                "diabetes", "arthritis", "rehabilitation", "therapy", "exercise"
            ]
            
            if any(keyword in query.lower() for keyword in medical_keywords):
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
                unique_products = []
                seen_names = set()
                for product in all_products:
                    if product.get("name") not in seen_names:
                        unique_products.append(product)
                        seen_names.add(product.get("name"))
                
                products = unique_products[:5]  # Limit to 5 most relevant products
                
                # Generate medical advice with product recommendations
                final_messages = [
                    SystemMessage(content=DOCTOR_AGENT_PROMPT),
                    HumanMessage(content=f"Patient query: {query}\nRecommended products: {products}\nProvide medical advice with these product recommendations, including appropriate disclaimers and safety warnings.")
                ]
                final_response = llm.invoke(final_messages)
                reply = final_response.content
            else:
                # General medical conversation
                workflow_steps.append("medical_conversation")
                reply = llm_response
            
            return {
                "success": True,
                "reply": reply,
                "products": products,
                "workflow_steps": workflow_steps,
                "agent_type": "doctor"
            }
            
        except Exception as e:
            return {
                "success": False,
                "reply": f"I'm sorry, I encountered an error: {str(e)}",
                "products": [],
                "workflow_steps": ["error"],
                "agent_type": "doctor"
            }
    
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
        
        # If no specific matches, try general medical equipment
        if not queries:
            queries.append("medical equipment")
        
        return queries[:3]  # Limit to 3 search queries

# Initialize doctor agent
doctor_agent = DoctorAgent()