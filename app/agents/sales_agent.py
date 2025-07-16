"""
Sales Agent for Al Essa Kuwait - Specialized in product sales and customer service.
"""

from typing import Dict, List, Any
from app.core.llm import llm
from app.tools.product_search import product_search_tool
from app.tools.response_filter import response_filter_tool
from langchain.schema import HumanMessage, SystemMessage

SALES_AGENT_PROMPT = """You are a professional sales representative for Al Essa Kuwait, specializing in medical equipment and home appliances.

**🎯 YOUR ROLE**
- Help customers find the perfect products for their needs
- Provide expert product knowledge and recommendations
- Guide customers through the purchasing process
- Build trust and rapport with customers

**💼 SALES APPROACH**
- Ask qualifying questions to understand customer needs
- Present relevant products with benefits and features
- Address concerns and objections professionally
- Suggest complementary products when appropriate
- Provide clear pricing and availability information

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

**🎯 RESPONSE GUIDELINES**
- For product queries: Search and present relevant options
- For general questions: Provide helpful information
- For pricing: Be transparent about costs
- For concerns: Address them professionally
- Always ask follow-up questions to better serve the customer

Remember: Your goal is to help customers make informed decisions that improve their lives!"""

class SalesAgent:
    """Sales agent for product recommendations and customer service."""
    
    def __init__(self):
        """Initialize the sales agent."""
        self.tools = [product_search_tool, response_filter_tool]
        
    def process_query(self, query: str, session_id: str = "default") -> Dict[str, Any]:
        """Process a sales-related query."""
        try:
            workflow_steps = []
            products = []
            
            # Use LLM to understand the query and determine response
            messages = [
                SystemMessage(content=SALES_AGENT_PROMPT),
                HumanMessage(content=f"Customer query: {query}")
            ]
            
            response = llm.invoke(messages)
            llm_response = response.content
            
            # Check if product search is needed
            if any(keyword in query.lower() for keyword in ["product", "buy", "price", "wheelchair", "walker", "brace", "splint", "ice pack", "air conditioner", "appliance"]):
                workflow_steps.extend(["sales_analysis", "product_search"])
                
                # Search for products
                search_result = product_search_tool.invoke({"query": query})
                products = search_result.get("products", [])
                
                # Generate sales-focused response
                final_messages = [
                    SystemMessage(content=SALES_AGENT_PROMPT),
                    HumanMessage(content=f"Customer query: {query}\nProducts found: {products}\nGenerate a sales-focused response that presents these products professionally and asks relevant follow-up questions.")
                ]
                final_response = llm.invoke(final_messages)
                reply = final_response.content
            else:
                # General sales conversation
                workflow_steps.append("sales_conversation")
                reply = llm_response
            
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

# Initialize sales agent
sales_agent = SalesAgent()