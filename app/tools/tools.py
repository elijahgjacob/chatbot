"""
Tools for the chatbot application.
"""

from typing import Dict, List, Any
from app.core.scraping import get_product_prices_from_search

class ProductSearchTool:
    def __init__(self):
        self.name = "product_search"
        self.description = "Search for products based on user queries"
    def _run(self, query: str) -> Dict[str, Any]:
        # Use the real scraper
        result = get_product_prices_from_search(query)
        products = result.get('products', [])
        return {"success": True, "products": products, "count": len(products)}

class ResponseFilterTool:
    def __init__(self):
        self.name = "response_filter"
        self.description = "Filter and sort products based on user requirements"
    def _run(self, products: List[Dict], query: str) -> Dict[str, Any]:
        query_lower = query.lower()
        if "cheapest" in query_lower or "lowest" in query_lower:
            sorted_products = sorted(products, key=lambda x: float(x["price"].split()[0]))
            filter_type = "cheapest"
        elif "most expensive" in query_lower or "highest" in query_lower:
            sorted_products = sorted(products, key=lambda x: float(x["price"].split()[0]), reverse=True)
            filter_type = "most_expensive"
        elif "best" in query_lower:
            sorted_products = sorted(products, key=lambda x: float(x["price"].split()[0]))
            filter_type = "best"
        else:
            sorted_products = products
            filter_type = "none"
        filtered_products = sorted_products[:1] if filter_type != "none" else products
        return {"success": True, "filtered_products": filtered_products, "filter_type": filter_type, "count": len(filtered_products)}

class QueryRefinementTool:
    def __init__(self):
        self.name = "query_refinement"
        self.description = "Refine and clarify user queries for better product search"
    def _run(self, query: str) -> Dict[str, Any]:
        query_lower = query.lower()
        product_keywords = ["wheelchair", "crutches", "walker", "cane", "medical"]
        product = None
        for keyword in product_keywords:
            if keyword in query_lower:
                product = keyword
                break
        requirements = []
        if "cheapest" in query_lower or "lowest" in query_lower:
            requirements.append("cheapest")
        if "best" in query_lower:
            requirements.append("best")
        if "most expensive" in query_lower or "highest" in query_lower:
            requirements.append("most_expensive")
        search_query = product if product else "medical equipment"
        return {"success": True, "search_query": search_query, "product": product, "requirements": " ".join(requirements) if requirements else "general"}

def get_product_prices_from_search(query: str, max_pages: int = 1) -> Dict[str, Any]:
    from app.core.scraping import get_product_prices_from_search as real_scraper
    return real_scraper(query, max_pages=max_pages) 