"""
ChatbotAgent implementation for the agentic workflow.
"""

from typing import Dict, List, Any
from app.tools.tools import ProductSearchTool, ResponseFilterTool, QueryRefinementTool

class ChatbotAgent:
    """Agent for processing queries with tools."""
    
    def __init__(self):
        """Initialize the agent with tools and memory."""
        self.memory = []
        self.prompt = "You are a helpful assistant that can search for products and provide information."
        
        # Initialize tools for test compatibility
        self.product_search_tool = ProductSearchTool()
        self.response_filter_tool = ResponseFilterTool()
        self.query_refinement_tool = QueryRefinementTool()
    
    def process_query(self, query: str, session_id: str = "default") -> Dict[str, Any]:
        """
        Process a user query using the agentic workflow.
        
        Args:
            query: The user's query
            session_id: The session ID for tracking conversation
            
        Returns:
            Dictionary containing the response and workflow information
        """
        try:
            workflow_steps = []
            products = []

            # Step 0: Check for general medical/doctor question
            medical_keywords = [
                "headache", "fever", "pain", "cough", "cold", "flu", "sick", "symptom", "medicine", "doctor", "health", "dizzy", "vomit", "nausea", "rash", "injury", "bleeding", "infection", "treatment", "advice", "prescription", "diagnosis"
            ]
            if any(word in query.lower() for word in medical_keywords):
                # Doctor-style response with disclaimer
                response = (
                    f"I'm a virtual assistant and can provide general information about your question: '{query}'. "
                    "However, my advice does not replace consultation with a real healthcare professional. "
                    "If your symptoms are severe or worsening, please seek immediate medical attention. "
                    "For a headache, common advice includes resting, staying hydrated, and avoiding triggers. "
                    "If the headache is severe, persistent, or accompanied by other symptoms, consult a doctor."
                )
                return {
                    "success": True,
                    "response": response,
                    "products": [],
                    "workflow_steps": ["doctor_response"]
                }

            # Step 1: Query Refinement (for complex queries)
            if self._needs_refinement(query):
                refinement_result = self.query_refinement_tool._run(query)
                workflow_steps.append("query_refinement")
                if refinement_result.get("success"):
                    refined_query = refinement_result.get("search_query", query)
                else:
                    refined_query = query
            else:
                refined_query = query
            
            # Step 2: Product Search
            from app.tools.tools import get_product_prices_from_search
            search_result = get_product_prices_from_search(refined_query)
            workflow_steps.append("product_search")
            products = search_result.get("products", [])
            
            # Step 3: Response Filtering (if needed)
            if self._needs_filtering(query) and products:
                filter_result = self.response_filter_tool._run(products, query)
                workflow_steps.append("response_filter")
                if filter_result.get("success"):
                    products = filter_result.get("filtered_products", products)
            
            # Generate response
            response = self._generate_response(query, products)
            
            return {
                "success": True,
                "response": response,
                "products": products,
                "workflow_steps": workflow_steps
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": "I encountered an error while processing your request.",
                "products": [],
                "workflow_steps": []
            }
    
    def _needs_refinement(self, query: str) -> bool:
        """Check if query needs refinement."""
        complex_keywords = ["cheapest", "best", "most expensive", "recommend", "suggest"]
        return any(keyword in query.lower() for keyword in complex_keywords)
    
    def _needs_filtering(self, query: str) -> bool:
        """Check if results need filtering."""
        filter_keywords = ["cheapest", "most expensive", "best", "top", "lowest", "highest"]
        return any(keyword in query.lower() for keyword in filter_keywords)
    
    def _generate_response(self, query: str, products: List[Dict]) -> str:
        """Generate a response based on the query and products."""
        if not products:
            return "I couldn't find any products matching your query. Could you try rephrasing it?"
        
        # Check if this was a filtered query (cheapest, most expensive, etc.)
        query_lower = query.lower()
        is_filtered = any(keyword in query_lower for keyword in ["cheapest", "most expensive", "best", "lowest", "highest"])
        
        def get_link(product):
            return product.get('link', product.get('url', ''))
        
        if len(products) == 1:
            product = products[0]
            if is_filtered:
                filter_type = "cheapest" if "cheapest" in query_lower else "most expensive" if "most expensive" in query_lower else "best"
                return f"I found the {filter_type} option: {product['name']} for {product['price']}. You can view it at {get_link(product)}."
            else:
                return f"I found {product['name']} for {product['price']}. You can view it at {get_link(product)}."
        
        product_list = "\n".join([
            f"- {p['name']}: {p['price']} ({get_link(p)})"
            for p in products[:3]  # Show top 3
        ])
        
        return f"I found {len(products)} products matching your query:\n{product_list}"

# Create a global agent instance
chatbot_agent = ChatbotAgent()