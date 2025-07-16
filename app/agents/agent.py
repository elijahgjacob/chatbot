"""
ChatbotAgent implementation for the agentic workflow.
"""

from typing import Dict, List, Any
import random
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
        
        # Conversation starters and connectors
        self.conversation_starters = [
            "That's a great question! ",
            "I'm excited to help you with this! ",
            "Perfect! Let me find some amazing options for you. ",
            "Wonderful! I have some fantastic suggestions. ",
            "I'd love to help you find exactly what you need! "
        ]
        
        self.enthusiasm_phrases = [
            "I found some fantastic options for you!",
            "I'm thrilled to show you what we have!",
            "Here are some amazing products I think you'll love:",
            "I've discovered some excellent choices for you!",
            "I'm excited to share these great options with you!"
        ]
        
        self.follow_up_questions = [
            "Which of these catches your interest?",
            "What would you like to know more about?",
            "Which one feels right for your needs?",
            "Would you like me to tell you more about any of these?",
            "What matters most to you in making this decision?",
            "Is there a particular price range you're most comfortable with?",
            "Would you like to hear about the features that make each one special?"
        ]
        
        # Memory for conversation context
        self.conversation_context = {}
    
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
            
            # Initialize conversation context if not exists
            if session_id not in self.conversation_context:
                self.conversation_context[session_id] = {
                    "previous_queries": [],
                    "mentioned_products": [],
                    "user_preferences": {},
                    "conversation_stage": "discovery"
                }
            
            # Update conversation context
            context = self.conversation_context[session_id]
            context["previous_queries"].append(query)
            
            # Keep only last 5 queries for memory efficiency
            if len(context["previous_queries"]) > 5:
                context["previous_queries"] = context["previous_queries"][-5:]
            
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
            
            # Update mentioned products in context
            for product in products[:3]:  # Track top 3 products
                if product not in context["mentioned_products"]:
                    context["mentioned_products"].append(product)
            
            # Step 3: Response Filtering (if needed)
            if self._needs_filtering(query) and products:
                filter_result = self.response_filter_tool._run(products, query)
                workflow_steps.append("response_filter")
                if filter_result.get("success"):
                    products = filter_result.get("filtered_products", products)
            
            # Generate conversational response
            response = self._generate_conversational_response(query, products, context)
            
            return {
                "success": True,
                "response": response,
                "products": products,
                "workflow_steps": workflow_steps
            }
            
        except Exception as e:
            # More empathetic error response
            error_responses = [
                "I'm so sorry, but I ran into a little technical hiccup while searching for you. Let me try that again!",
                "Oops! Something went wrong on my end. Don't worry though - let me help you find what you need another way.",
                "I apologize, but I'm having a technical moment. Could you try rephrasing your request? I'm here to help!"
            ]
            return {
                "success": False,
                "error": str(e),
                "response": random.choice(error_responses),
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
    
    def _generate_conversational_response(self, query: str, products: List[Dict], context: Dict) -> str:
        """Generate a conversational response based on the query and products."""
        query_lower = query.lower()
        
        # Handle greetings and general conversation
        if self._is_greeting(query):
            return self._handle_greeting(context)
        
        if self._is_thanks(query):
            return self._handle_thanks()
        
        if self._is_general_question(query):
            return self._handle_general_question(query)
        
        # Handle product queries
        if not products:
            return self._handle_no_products(query, context)
        
        # Check if this was a filtered query
        is_filtered = any(keyword in query_lower for keyword in ["cheapest", "most expensive", "best", "lowest", "highest"])
        
        # Generate product response based on number of products
        if len(products) == 1:
            return self._generate_single_product_response(products[0], query, is_filtered, context)
        else:
            return self._generate_multiple_products_response(products, query, context)
    
    def _is_greeting(self, query: str) -> bool:
        """Check if the query is a greeting."""
        greetings = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening", "greetings"]
        return any(greeting in query.lower() for greeting in greetings)
    
    def _is_thanks(self, query: str) -> bool:
        """Check if the query is expressing thanks."""
        thanks = ["thank", "thanks", "appreciate", "grateful"]
        return any(thank in query.lower() for thank in thanks)
    
    def _is_general_question(self, query: str) -> bool:
        """Check if it's a general question about the company or services."""
        general_keywords = ["who are you", "what do you do", "tell me about", "company", "services", "help"]
        return any(keyword in query.lower() for keyword in general_keywords)
    
    def _handle_greeting(self, context: Dict) -> str:
        """Handle greeting messages."""
        greetings = [
            "Hello! I'm so glad you're here! 😊 I'm your Al Essa Kuwait sales representative, and I'm excited to help you find exactly what you need. What brings you to us today?",
            "Hi there! Welcome to Al Essa Kuwait! I'm thrilled to assist you with finding the perfect medical equipment or appliances. How can I make your day better?",
            "Hey! It's wonderful to meet you! I'm here to help you discover amazing products from Al Essa Kuwait. What can I help you find today?",
            "Good to see you! I'm your personal Al Essa Kuwait assistant, and I'm excited to help you find something amazing. What are you looking for today?"
        ]
        return random.choice(greetings)
    
    def _handle_thanks(self) -> str:
        """Handle thank you messages."""
        responses = [
            "You're so welcome! I'm thrilled I could help! 😊 Is there anything else you'd like to explore? I'm here whenever you need me!",
            "It's absolutely my pleasure! I love helping customers find exactly what they need. Feel free to ask me anything else!",
            "Aww, thank you! That makes me so happy to hear! Don't hesitate to reach out if you need anything else - I'm always here to help!",
            "You're very welcome! I'm just glad I could assist you. If anything else comes to mind, please let me know!"
        ]
        return random.choice(responses)
    
    def _handle_general_question(self, query: str) -> str:
        """Handle general questions about the company or services."""
        return """I'm your virtual sales representative for Al Essa Kuwait! 🌟 We're a trusted leader in:

• Medical Technology & Equipment 🏥
• Premium Home Appliances (including Hitachi!) 🏠  
• Consumer Electronics & Technology 📱
• Professional Engineering Solutions ⚙️

I'm here to help you find the perfect products for your needs, answer your questions, and guide you through our amazing selection. I love connecting people with solutions that genuinely improve their lives!

What specific area interests you most? I'd be thrilled to show you what we have! 😊"""
    
    def _handle_no_products(self, query: str, context: Dict) -> str:
        """Handle cases where no products are found."""
        responses = [
            f"I'm sorry, but I couldn't find any products matching '{query}' right now. But don't worry - I'm here to help! Could you try describing what you need in a different way? Or tell me more about what you're hoping to accomplish?",
            f"Hmm, I didn't find results for '{query}', but I bet we have something perfect for you! Could you tell me a bit more about what you're looking for? I'd love to help you find exactly what you need!",
            f"I wasn't able to locate products for '{query}' at the moment, but let's figure this out together! What specific type of product or solution are you hoping to find? I'm confident we can find something amazing for you!"
        ]
        
        # Add context-aware suggestions if we have previous conversation
        if context.get("mentioned_products"):
            response = random.choice(responses)
            response += f"\n\nBy the way, earlier we looked at some great options. Would any of those work, or are you looking for something completely different?"
            return response
            
        return random.choice(responses)
    
    def _generate_single_product_response(self, product: Dict, query: str, is_filtered: bool, context: Dict) -> str:
        """Generate response for single product."""
        name = product.get('name', 'Product')
        price = product.get('price', 'Price available upon request')
        link = product.get('link', product.get('url', ''))
        
        starter = random.choice(self.conversation_starters)
        
        if is_filtered:
            filter_type = "perfect" if "best" in query.lower() else "most affordable" if "cheapest" in query.lower() else "premium"
            response = f"{starter}I found the {filter_type} option for you: **{name}** at {price}! 🌟\n\n"
        else:
            response = f"{starter}I found something wonderful: **{name}** for {price}! ✨\n\n"
        
        response += f"This is actually one of our fantastic products, and I think you're going to love it! "
        
        if link:
            response += f"You can check out all the amazing details here: {link}\n\n"
        
        # Add conversational follow-up
        follow_ups = [
            "What would you like to know more about regarding this product?",
            "Does this look like what you had in mind?",
            "Would you like me to tell you more about its features?",
            "Is this the kind of solution you were hoping for?",
            "What questions can I answer about this for you?"
        ]
        
        response += random.choice(follow_ups)
        return response
    
    def _generate_multiple_products_response(self, products: List[Dict], query: str, context: Dict) -> str:
        """Generate response for multiple products."""
        starter = random.choice(self.enthusiasm_phrases)
        
        response = f"{starter} 🌟\n\n"
        
        # Show top 3 products with enthusiasm
        for i, product in enumerate(products[:3], 1):
            name = product.get('name', f'Product {i}')
            price = product.get('price', 'Price available')
            link = product.get('link', product.get('url', ''))
            
            if i == 1:
                response += f"✨ **{name}** - {price}"
                response += " (This is one of my absolute favorites!)"
            elif i == 2:
                response += f"\n🌟 **{name}** - {price}"
                response += " (Perfect for premium features)"
            else:
                response += f"\n💎 **{name}** - {price}"
                response += " (Our top-of-the-line choice)"
                
            if link:
                response += f" [View details]({link})"
        
        if len(products) > 3:
            response += f"\n\n*And I found {len(products) - 3} more amazing options!*"
        
        # Add engaging follow-up
        response += "\n\n" + random.choice(self.follow_up_questions)
        
        # Add context-aware suggestion
        if context.get("previous_queries") and len(context["previous_queries"]) > 1:
            response += "\n\nI can also help you compare these with anything else you've been considering!"
        
        return response

# Create a global agent instance
chatbot_agent = ChatbotAgent()