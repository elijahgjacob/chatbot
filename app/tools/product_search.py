from langchain.tools import tool
import logging
from app.core.scraping import get_product_prices_from_search
import re

logger = logging.getLogger(__name__)

def extract_keywords(query: str) -> list:
    """Extract meaningful keywords from a query."""
    # Remove common words that don't help with product search
    stop_words = {
        'what', 'products', 'do', 'you', 'have', 'for', 'this', 'that', 'the', 'a', 'an',
        'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are',
        'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
        'will', 'would', 'could', 'should', 'may', 'might', 'can', 'show', 'me', 'tell',
        'about', 'like', 'similar', 'same', 'other', 'more', 'less', 'cheap', 'expensive',
        'good', 'best', 'worst', 'new', 'old', 'used', 'available', 'price', 'cost'
    }
    
    # Clean and split the query
    words = re.findall(r'\b\w+\b', query.lower())
    
    # Filter out stop words and short words
    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    
    return keywords

def get_alternative_search_terms(query: str) -> list:
    """Get alternative search terms for better product discovery."""
    query_lower = query.lower()
    alternatives = []
    
    # Common product variations
    if 'icepack' in query_lower or 'ice pack' in query_lower:
        alternatives.extend(['ice', 'cold', 'gel', 'pack', 'therapy'])
    elif 'wheelchair' in query_lower:
        alternatives.extend(['chair', 'mobility', 'transport'])
    elif 'walker' in query_lower:
        alternatives.extend(['mobility', 'support', 'assist'])
    elif 'crutch' in query_lower:
        alternatives.extend(['support', 'mobility', 'assist'])
    elif 'brace' in query_lower:
        alternatives.extend(['support', 'orthopedic', 'medical'])
    
    # Add the original query as first option
    return [query] + alternatives

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
        # Get alternative search terms
        search_terms = get_alternative_search_terms(query)
        logger.info(f"ProductSearchTool: Will try search terms: {search_terms}")
        
        all_products = []
        best_result = None
        
        # Try each search term until we find good results
        for search_term in search_terms:
            result = get_product_prices_from_search(search_term)
            products = result.get('products', [])
            
            # Skip if we only got placeholder products
            valid_products = [p for p in products if p.get('price', 0) > 0 and 'downloadable' not in p.get('name', '').lower()]
            
            if valid_products:
                logger.info(f"ProductSearchTool: Found {len(valid_products)} valid products with search term '{search_term}'")
                all_products.extend(valid_products)
                if not best_result:
                    best_result = result
            else:
                logger.info(f"ProductSearchTool: No valid products found with search term '{search_term}'")
        
        # Remove duplicates based on product name
        seen_names = set()
        unique_products = []
        for product in all_products:
            name = product.get('name', '').lower()
            if name not in seen_names and name:
                seen_names.add(name)
                unique_products.append(product)
        
        # Extract meaningful keywords from the original query
        keywords = extract_keywords(query)
        logger.info(f"ProductSearchTool: Extracted keywords: {keywords}")
        
        # If no meaningful keywords found, return all products (for general queries)
        if not keywords:
            logger.info(f"ProductSearchTool: No keywords found, returning all {len(unique_products)} products")
            return {
                "success": True,
                "query": query,
                "products": unique_products[:10],  # Limit to 10 for general queries
                "count": len(unique_products),
                "formatted_response": best_result.get('formatted_reply', '') if best_result else ''
            }
        
        # Filter products based on keywords
        filtered_products = []
        for product in unique_products:
            product_name = product.get('name', '').lower()
            product_category = product.get('category', '').lower()
            
            # Check if any keyword matches the product name or category
            for keyword in keywords:
                if keyword in product_name or keyword in product_category:
                    filtered_products.append(product)
                    break  # Found a match, no need to check other keywords for this product
        
        logger.info(f"ProductSearchTool: Found {len(filtered_products)} relevant products for '{query}'")
        
        # If no products match keywords but we have products, return some popular ones
        if not filtered_products and unique_products:
            logger.info(f"ProductSearchTool: No keyword matches, returning first 5 products")
            filtered_products = unique_products[:5]
        
        return {
            "success": True,
            "query": query,
            "products": filtered_products,
            "count": len(filtered_products),
            "formatted_response": best_result.get('formatted_reply', '') if best_result else ''
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