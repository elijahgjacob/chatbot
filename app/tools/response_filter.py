from langchain.tools import tool
import logging
from app.core.llm import get_llm_response

logger = logging.getLogger(__name__)

@tool("response_filter", return_direct=False)
def response_filter_tool(products, filter_criteria: str) -> dict:
    """
    Use the LLM to filter and sort a list of products based on user-specified criteria such as price, quality, or features.
    """
    logging.info("TOOL | response_filter")
    logger.info(f"ResponseFilterTool: Filtering {len(products)} products with criteria '{filter_criteria}'")
    if not products:
        return {
            "success": False,
            "message": "No products to filter",
            "filtered_products": []
        }
    try:
        # Prepare a prompt for the LLM
        prompt = (
            "You are an expert assistant. The user has asked to filter or sort the following products based on these criteria: "
            f"'{filter_criteria}'.\n"
            "Here is the product list (as JSON):\n"
            f"{products}\n"
            "Return a JSON list of the filtered and/or sorted products that best match the criteria. "
            "If nothing matches, return an empty list."
        )
        llm_response = get_llm_response(prompt)
        # Try to extract the JSON list from the LLM's response
        import json
        try:
            # Find the first JSON list in the response
            start = llm_response.find('[')
            end = llm_response.rfind(']')
            filtered_products = json.loads(llm_response[start:end+1]) if start != -1 and end != -1 else []
        except Exception as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            filtered_products = []
        return {
            "success": True,
            "filtered_products": filtered_products,
            "count": len(filtered_products),
            "original_count": len(products),
            "llm_response": llm_response
        }
    except Exception as e:
        logger.error(f"ResponseFilterTool error: {e}")
        return {
            "success": False,
            "error": str(e),
            "filtered_products": []
        }