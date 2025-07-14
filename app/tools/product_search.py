from langchain.tools import tool
import logging
from app.core.scraping import get_product_prices_from_search

logger = logging.getLogger(__name__)

@tool("product_search", return_direct=False)
def product_search_tool(query: str) -> dict:
    """
    Search the Alessa Med website for products matching the user's query.
    Use this tool when the user asks about a specific product, category, or type of medical equipment.
    Return a list of relevant products with their names, prices, and links.
    """
    logging.info("TOOL | product_search")
    logger.info(f"ProductSearchTool: Searching for '{query}'")
    try:
        result = get_product_prices_from_search(query)
        products = result.get('products', [])
        keyword = query.lower().strip()
        filtered_products = [
            p for p in products
            if keyword in p.get('name', '').lower() or keyword in p.get('category', '').lower()
        ] if keyword else products
        logger.info(f"ProductSearchTool: Found {len(filtered_products)} relevant products for '{query}'")
        return {
            "success": True,
            "query": query,
            "products": filtered_products,
            "count": len(filtered_products),
            "formatted_response": result.get('formatted_response', '')
        }
    except Exception as e:
        logger.error(f"ProductSearchTool error: {e}")
        return {
            "success": False,
            "query": query,
            "error": str(e),
            "products": [],
            "count": 0
        } 