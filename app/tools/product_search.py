from langchain.tools import tool
import logging
from app.core.scraping import get_product_prices_from_search
import re

logger = logging.getLogger(__name__)

def extract_keywords(query: str) -> list:
    """Extract meaningful keywords from a query."""
    stop_words = {
        'what', 'products', 'do', 'you', 'have', 'for', 'this', 'that', 'the', 'a', 'an',
        'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are',
        'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
        'will', 'would', 'could', 'should', 'may', 'might', 'can', 'show', 'me', 'tell',
        'about', 'like', 'similar', 'same', 'other', 'more', 'less', 'cheap', 'expensive',
        'good', 'best', 'worst', 'new', 'old', 'used', 'available', 'price', 'cost'
    }
    words = re.findall(r'\b\w+\b', query.lower())
    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    return keywords

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
        keywords = extract_keywords(query)
        logger.info(f"ProductSearchTool: Extracted keywords: {keywords}")
        if not keywords:
            logger.info(f"ProductSearchTool: No keywords found, returning all {len(products)} products")
            return {
                "success": True,
                "query": query,
                "products": products[:10],
                "count": len(products),
                "formatted_response": result.get('formatted_reply', '')
            }
        filtered_products = []
        for product in products:
            product_name = product.get('name', '').lower()
            product_category = product.get('category', '').lower()
            for keyword in keywords:
                if keyword in product_name or keyword in product_category:
                    filtered_products.append(product)
                    break
        logger.info(f"ProductSearchTool: Found {len(filtered_products)} relevant products for '{query}'")
        if not filtered_products and products:
            logger.info(f"ProductSearchTool: No keyword matches, returning first 5 products")
            filtered_products = products[:5]
        return {
            "success": True,
            "query": query,
            "products": filtered_products,
            "count": len(filtered_products),
            "formatted_response": result.get('formatted_reply', '')
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