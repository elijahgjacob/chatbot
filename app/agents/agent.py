"""
LangChain Agent for the Chatbot
"""
import logging
from typing import Dict, Any, List
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory

from app.agents.agent_handler import product_search_tool, response_filter_tool, query_refinement_tool
from app.core.llm import get_llm_response, llm
from app.core.prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class ChatbotAgent:
    """Main agent that orchestrates tools for handling user queries"""
    
    def __init__(self):
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Create the agent prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create the agent
        self.agent = create_openai_functions_agent(
            llm=llm,  # Use the actual LLM object
            tools=AVAILABLE_TOOLS,
            prompt=self.prompt
        )
        
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=AVAILABLE_TOOLS,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def process_query(self, user_query: str, session_id: str = "default") -> Dict[str, Any]:
        logger.info(f"Agent processing query: {user_query} (session: {session_id})")

        # Expansive greeting/intent detection
        greetings = [
            # English greetings
            "hi", "hello", "hey", "heya", "hiya", "yo", "sup", "what's up", "whats up", "good morning", "good afternoon", "good evening", "greetings", "howdy", "hey there", "hi there", "hello there", "morning", "afternoon", "evening", "how are you", "how's it going", "how are you doing", "how do you do", "how r u", "how are ya", "how are things", "how's everything", "how's life", "how's your day", "how's your day going", "how's your morning", "how's your afternoon", "how's your evening", "hope you're well", "hope you are well", "hope you're doing well", "hope you are doing well", "hope all is well", "hope all's well", "nice to meet you", "pleased to meet you", "good to see you", "long time no see", "yo what's up", "hey what's up", "hey there!", "hi!", "hello!", "hey!", "good day", "salutations",
            # Arabic greetings
            "السلام عليكم", "عليكم السلام", "مرحبا", "اهلا", "أهلاً", "أهلا وسهلا", "صباح الخير", "مساء الخير", "صباح النور", "مساء النور", "اهلين", "اهلا بك", "اهلا بكم", "اهلا وسهلا بكم", "كيف حالك", "كيفك", "كيف الحال", "كيف الامور", "كيفك اليوم", "كيف يومك", "كيف صباحك", "كيف مساك", "كيف أمورك", "كيف صحتك", "ان شاء الله بخير", "انشالله بخير", "شخبارك", "شو الاخبار", "ايش الاخبار", "شلونك", "شلونكم", "مرحبتين", "هلا", "هلا والله", "هلا وغلا", "هلا بك", "هلا بكم", "هلا وسهلا", "نورنا", "منور", "منورة", "يا هلا", "يا مرحبا", "يا اهلا", "يا اهلا وسهلا", "يا صباح الخير", "يا مساء الخير"
        ]
        if user_query.strip().lower() in greetings:
            return {
                "success": True,
                "response": "Hi, welcome to AlEssaMed—I'm here to help you find the right medical device today. How can I assist you?",
                "products": [],
                "workflow_steps": [],
            }

        try:
            # Simple workflow without complex agent execution
            # This is more reliable and easier to debug
            return self._simple_workflow(user_query, session_id)
        except Exception as e:
            logger.error(f"Agent error: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "I'm sorry, I encountered an error processing your request. Please try again."
            }
    
    def _simple_workflow(self, user_query: str, session_id: str) -> Dict[str, Any]:
        # Retrieve chat history for the session
        from app.api.main import chat_history
        session_history = chat_history.get(session_id, [])

        # Step 1: Query Refinement (if needed)
        refinement_result = query_refinement_tool._run(user_query, "", history=session_history)
        refined_query = refinement_result.get("search_query", user_query)
        main_product = refinement_result.get("product", user_query)
        requirements = refinement_result.get("requirements", "")

        # If the query is not about a product, respond conversationally
        if main_product is None or str(main_product).lower() == "none":
            return {
                "success": True,
                "response": "I'm here to help you find medical equipment or answer questions about our products. How can I assist you today?",
                "products": [],
                "workflow_steps": ["query_refinement"]
            }

        # Step 2: Product Search (use only the main product)
        search_result = product_search_tool._run(main_product)

        # Step 3: Apply Filters (if requirements exist)
        final_result = search_result
        if requirements and search_result.get("success") and search_result.get("products"):
            filter_result = response_filter_tool._run(
                search_result["products"],
                requirements
            )
            if filter_result.get("success"):
                final_result = {
                    **search_result,
                    "products": filter_result.get("filtered_products", []),
                    "filter_applied": True,
                    "filter_type": filter_result.get("filter_type", "unknown")
                }

        # Step 4: Generate Response
        response = self._generate_response(final_result, user_query)

        return {
            "success": True,
            "response": response,
            "products": final_result.get("products", []),
            "workflow_steps": [
                step for step in [
                    "query_refinement" if refined_query != user_query else None,
                    "product_search",
                    "response_filter" if final_result != search_result else None
                ] if step is not None
            ]
        }
    
    def _refine_query_if_needed(self, user_query: str) -> str:
        """Refine the query if it's complex or unclear"""
        # Simple heuristic: if query contains multiple words and modifiers, refine it
        words = user_query.lower().split()
        modifiers = ['cheapest', 'expensive', 'best', 'under', 'over', 'quality', 'budget']
        
        has_modifiers = any(mod in user_query.lower() for mod in modifiers)
        is_complex = len(words) > 3 or has_modifiers
        
        if is_complex:
            logger.info(f"Refining complex query: {user_query}")
            try:
                result = query_refinement_tool._run(user_query, "")
                if result.get("success"):
                    return result.get("search_query", user_query)
            except Exception as e:
                logger.error(f"Query refinement failed: {e}")
        
        return user_query
    
    def _search_products(self, query: str) -> Dict[str, Any]:
        """Search for products"""
        logger.info(f"Searching for products: {query}")
        try:
            result = product_search_tool._run(query)
            return result
        except Exception as e:
            logger.error(f"Product search failed: {e}")
            return {"success": False, "products": [], "error": str(e)}
    
    def _apply_filters_if_needed(self, search_result: Dict[str, Any], original_query: str) -> Dict[str, Any]:
        """Apply filters if the user has specific requirements"""
        if not search_result.get("success") or not search_result.get("products"):
            return search_result
        
        # Check if user has filtering requirements
        query_lower = original_query.lower()
        filter_keywords = ['cheapest', 'expensive', 'best', 'under', 'over', 'quality', 'budget', 'lowest', 'highest']
        
        has_filter_requirements = any(keyword in query_lower for keyword in filter_keywords)
        
        if has_filter_requirements:
            logger.info(f"Applying filters to {len(search_result['products'])} products")
            try:
                filter_result = response_filter_tool._run(
                    search_result["products"], 
                    original_query
                )
                
                if filter_result.get("success"):
                    return {
                        **search_result,
                        "products": filter_result.get("filtered_products", []),
                        "filter_applied": True,
                        "filter_type": filter_result.get("filter_type", "unknown")
                    }
            except Exception as e:
                logger.error(f"Filter application failed: {e}")
        
        return search_result
    
    def _generate_response(self, result: Dict[str, Any], original_query: str) -> str:
        """Generate a natural language response"""
        if not result.get("success"):
            return "I'm sorry, I couldn't find any products matching your request. Please try a different search term."
        
        products = result.get("products", [])
        
        if not products:
            return "I couldn't find any products matching your search. Please try a different search term or check the spelling."
        
        # Improved: Always show Product, Cost in KWD, and link
        lines = []
        for product in products:
            name = product.get('name', 'Unknown product')
            price = product.get('price', 'N/A')
            link = product.get('url', product.get('link', ''))
            lines.append(f"• Product: {name}\n  Cost: {price} KWD\n  Link: {link}")
        
        if len(products) == 1:
            return f"Here is the product I found for you:\n{lines[0]}"
        else:
            return f"Here are the products I found for you:\n" + "\n".join(lines)


# Create a global agent instance
chatbot_agent = ChatbotAgent() 