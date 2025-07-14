from langchain.tools import tool
import logging
from app.core.llm import get_llm_response
import re

logger = logging.getLogger(__name__)

@tool("query_refinement", return_direct=False)
def query_refinement_tool(user_query: str, context: str = "", history=None) -> dict:
    """
    Analyze and clarify the user's query to extract the main product or category and any specific requirements (e.g., price, quality, features).
    Use this tool when the user's query is ambiguous, complex, or contains multiple requests.
    Return the refined product, requirements, and a clean search query.
    """
    logging.info("TOOL | query_refinement")
    logger.info(f"QueryRefinementTool: Refining query '{user_query}'")
    try:
        refinement_prompt = f"""
You are a query refinement assistant. Your job is to extract the core product or intent from user queries.

User Query: {user_query}
Context: {context}

Please extract:
1. The main product or category the user is looking for
2. Any specific requirements or modifiers (price, quality, etc.)
3. A clean search query for product search

If the user's query is not about a product or is a meta/conversational question (e.g., 'what did I just say?', 'how are you?', 'tell me a joke'), return:
PRODUCT: None
REQUIREMENTS: None
SEARCH_QUERY: None

Return your response in this format:
PRODUCT: [main product/category]
REQUIREMENTS: [specific requirements or modifiers]
SEARCH_QUERY: [clean query for product search]
"""
        refined_response = get_llm_response(refinement_prompt, history=history)
        product_match = re.search(r'PRODUCT:\s*(.+)', refined_response, re.IGNORECASE)
        requirements_match = re.search(r'REQUIREMENTS:\s*(.+)', refined_response, re.IGNORECASE)
        search_query_match = re.search(r'SEARCH_QUERY:\s*(.+)', refined_response, re.IGNORECASE)
        product = product_match.group(1).strip() if product_match else user_query
        requirements = requirements_match.group(1).strip() if requirements_match else ""
        search_query = search_query_match.group(1).strip() if search_query_match else product
        logger.info(f"QueryRefinementTool: Refined '{user_query}' to product='{product}', requirements='{requirements}', search_query='{search_query}'")
        return {
            "success": True,
            "original_query": user_query,
            "product": product,
            "requirements": requirements,
            "search_query": search_query,
            "refined_response": refined_response
        }
    except Exception as e:
        logger.error(f"QueryRefinementTool error: {e}")
        return {
            "success": False,
            "error": str(e),
            "original_query": user_query,
            "product": user_query,
            "requirements": "",
            "search_query": user_query
        } 