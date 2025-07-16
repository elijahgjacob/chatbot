"""
Price Filter Tool - Filters products by price range and budget constraints.
"""

from langchain.tools import tool
import logging
import re
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def extract_price_constraints(query: str) -> Dict[str, Any]:
    """
    Extract price constraints from a query.
    Returns a dict with 'min_price', 'max_price', 'budget', 'price_range'
    """
    query_lower = query.lower()
    constraints = {
        'min_price': None,
        'max_price': None,
        'budget': None,
        'price_range': None
    }
    
    # Extract numbers followed by currency (KWD, KD, etc.)
    price_patterns = [
        r'(\d+(?:\.\d+)?)\s*(?:kwd|kd|dinar|dinars)',
        r'(\d+(?:\.\d+)?)\s*(?:kwd|kd|dinar|dinars)?',
        r'(\d+(?:\.\d+)?)'
    ]
    
    numbers = []
    for pattern in price_patterns:
        matches = re.findall(pattern, query_lower)
        numbers.extend([float(match) for match in matches])
    
    if not numbers:
        return constraints
    
    # Look for price range indicators
    if any(word in query_lower for word in ['less than', 'under', 'below', 'maximum', 'up to']):
        constraints['max_price'] = max(numbers)
        constraints['budget'] = max(numbers)
    elif any(word in query_lower for word in ['more than', 'over', 'above', 'minimum', 'at least']):
        constraints['min_price'] = min(numbers)
    elif any(word in query_lower for word in ['between', 'from', 'to', 'range']):
        if len(numbers) >= 2:
            constraints['min_price'] = min(numbers)
            constraints['max_price'] = max(numbers)
            constraints['price_range'] = f"{min(numbers)}-{max(numbers)}"
    else:
        # Default: treat as maximum budget
        constraints['max_price'] = max(numbers)
        constraints['budget'] = max(numbers)
    
    return constraints

def filter_products_by_price(products: List[Dict], constraints: Dict[str, Any]) -> List[Dict]:
    """
    Filter products based on price constraints.
    """
    if not constraints.get('min_price') and not constraints.get('max_price'):
        return products
    
    filtered_products = []
    
    for product in products:
        try:
            # Extract price from product
            price_str = str(product.get('price', '0'))
            # Remove currency symbols and convert to float
            price = float(re.sub(r'[^\d.]', '', price_str))
            
            # Apply filters
            include_product = True
            
            if constraints.get('min_price') and price < constraints['min_price']:
                include_product = False
            
            if constraints.get('max_price') and price > constraints['max_price']:
                include_product = False
            
            if include_product:
                filtered_products.append(product)
                
        except (ValueError, TypeError):
            # If price parsing fails, include the product (better to show than hide)
            filtered_products.append(product)
    
    return filtered_products

@tool("price_filter", return_direct=False)
def price_filter_tool(products: List[Dict], query: str) -> dict:
    """
    Filter products by price based on user's budget constraints.
    Use this tool when the user mentions specific prices, budgets, or price ranges.
    """
    logging.info("TOOL | price_filter")
    logger.info(f"PriceFilterTool: Filtering {len(products)} products for query: '{query}'")
    
    try:
        # Extract price constraints from query
        constraints = extract_price_constraints(query)
        logger.info(f"PriceFilterTool: Extracted constraints: {constraints}")
        
        # Filter products
        filtered_products = filter_products_by_price(products, constraints)
        logger.info(f"PriceFilterTool: Filtered to {len(filtered_products)} products")
        
        return {
            "success": True,
            "query": query,
            "constraints": constraints,
            "products": filtered_products,
            "original_count": len(products),
            "filtered_count": len(filtered_products)
        }
        
    except Exception as e:
        logger.error(f"PriceFilterTool error: {e}")
        return {
            "success": False,
            "query": query,
            "error": str(e),
            "products": products,
            "original_count": len(products),
            "filtered_count": len(products)
        }