"""
Sales Agent for Al Essa Kuwait - Specialized in product sales and customer service.
"""

from typing import Dict, List, Any
from app.core.llm import llm
from app.core.conversation_memory import conversation_memory
from app.tools.product_search import product_search_tool
from app.tools.response_filter import response_filter_tool
from langchain.schema import HumanMessage, SystemMessage

SALES_AGENT_PROMPT = """You are a professional sales representative for Al Essa Kuwait, specializing in medical equipment and home appliances.

**🎯 YOUR ROLE**
- Help customers find the perfect products for their needs
- Provide expert product knowledge and recommendations
- Guide customers through the purchasing process
- Build trust and rapport with customers
- Remember previous conversations and build on them

**💼 SALES APPROACH**
- Ask qualifying questions to understand customer needs
- Present relevant products with benefits and features
- Address concerns and objections professionally
- Suggest complementary products when appropriate
- Provide clear pricing and availability information
- Reference previous conversations when relevant

**🛍️ PRODUCT KNOWLEDGE**
- Medical equipment: wheelchairs, walkers, crutches, braces, splints, ice packs, heating pads
- Home appliances: air conditioners, refrigerators, washing machines, etc.
- Technology: computers, phones, accessories

**💬 CONVERSATION STYLE**
- Professional yet friendly
- Ask ONE question at a time
- Listen to customer needs
- Be consultative, not pushy
- Provide clear, actionable recommendations
- Be conversational and natural

**🎯 RESPONSE GUIDELINES**
- For product queries: Search and present relevant options
- For general questions: Provide helpful information
- For pricing: Be transparent about costs
- For concerns: Address them professionally
- Always ask follow-up questions to better serve the customer
- Reference previous conversation context when appropriate

Remember: Your goal is to help customers make informed decisions that improve their lives!"""

class SalesAgent:
    """Sales agent for product recommendations and customer service."""
    
    def __init__(self):
        """Initialize the sales agent."""
        self.tools = [product_search_tool, response_filter_tool]
        
    def process_query(self, query: str, session_id: str = "default") -> Dict[str, Any]:
        """Process a sales-related query with conversation memory."""
        try:
            workflow_steps = []
            products = []
            
            # Get conversation history for context
            history = conversation_memory.get_conversation_history(session_id, max_messages=5)
            user_context = conversation_memory.get_user_context(session_id)
            
            # Build context-aware prompt
            context_prompt = self._build_context_prompt(query, history, user_context)
            
            # Use LLM to understand the query and determine response
            messages = [
                SystemMessage(content=SALES_AGENT_PROMPT),
                HumanMessage(content=context_prompt)
            ]
            
            response = llm.invoke(messages)
            llm_response = response.content
            
            # Check if product search is needed
            if any(keyword in query.lower() for keyword in ["product", "buy", "price", "wheelchair", "walker", "brace", "splint", "ice pack", "air conditioner", "appliance", "show me", "looking for"]):
                workflow_steps.extend(["sales_analysis", "product_search"])
                
                # Search for products
                search_result = product_search_tool.invoke({"query": query})
                products = search_result.get("products", [])
                
                # Generate sales-focused response with context
                final_messages = [
                    SystemMessage(content=SALES_AGENT_PROMPT),
                    HumanMessage(content=f"Customer query: {query}\nConversation history: {history}\nProducts found: {products}\nGenerate a conversational, sales-focused response that references previous context and presents these products professionally.")
                ]
                final_response = llm.invoke(final_messages)
                reply = final_response.content
            else:
                # General sales conversation
                workflow_steps.append("sales_conversation")
                reply = llm_response
            
            # Update conversation memory
            conversation_memory.add_message(
                session_id=session_id,
                role="user",
                content=query
            )
            conversation_memory.add_message(
                session_id=session_id,
                role="assistant",
                content=reply,
                agent_type="sales",
                products=products,
                workflow_steps=workflow_steps
            )
            
            # Update user context based on the conversation
            self._update_user_context(session_id, query, products)
            
            return {
                "success": True,
                "reply": reply,
                "products": products,
                "workflow_steps": workflow_steps,
                "agent_type": "sales"
            }
            
        except Exception as e:
            return {
                "success": False,
                "reply": f"I'm sorry, I encountered an error: {str(e)}",
                "products": [],
                "workflow_steps": ["error"],
                "agent_type": "sales"
            }
    
    def _build_context_prompt(self, query: str, history: List[Dict], user_context: Dict[str, Any]) -> str:
        """Build a context-aware prompt for the LLM."""
        prompt = f"Current customer query: {query}\n\n"
        
        if history:
            prompt += "Recent conversation history:\n"
            for msg in history[-3:]:  # Last 3 messages for context
                role = "Customer" if msg["role"] == "user" else "You"
                prompt += f"{role}: {msg['content']}\n"
            prompt += "\n"
        
        if user_context:
            prompt += "Customer context:\n"
            for key, value in user_context.items():
                prompt += f"- {key}: {value}\n"
            prompt += "\n"
        
        prompt += "Please respond naturally, considering the conversation history and customer context."
        return prompt
    
    def _update_user_context(self, session_id: str, query: str, products: List[Dict]) -> None:
        """Update user context based on the conversation."""
        context_updates = {}
        
        # Extract product interests
        if products:
            product_types = [p.get("name", "").lower() for p in products]
            if any("wheelchair" in pt for pt in product_types):
                context_updates["interested_in"] = "wheelchairs"
            elif any("walker" in pt for pt in product_types):
                context_updates["interested_in"] = "walkers"
            elif any("brace" in pt for pt in product_types):
                context_updates["interested_in"] = "braces/supports"
            elif any("air conditioner" in pt for pt in product_types):
                context_updates["interested_in"] = "appliances"
        
        # Extract budget mentions
        if any(word in query.lower() for word in ["cheap", "budget", "under", "less than", "kwd", "dinar"]):
            context_updates["budget_conscious"] = True
        
        # Extract urgency
        if any(word in query.lower() for word in ["urgent", "asap", "immediately", "today"]):
            context_updates["urgency"] = "high"
        
        if context_updates:
            conversation_memory.update_user_context(session_id, context_updates)

# Initialize sales agent
sales_agent = SalesAgent()