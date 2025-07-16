"""
Enhanced Product Search Tool - Advanced search with semantic matching, filtering, and relevance scoring.
"""

from langchain.tools import tool
import logging
import re
from typing import List, Dict, Any, Optional
from app.core.scraping import get_product_prices_from_search
from app.core.cache import cache_manager
from app.core.llm import llm
from langchain.schema import HumanMessage, SystemMessage
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class EnhancedProductSearch:
    """Enhanced product search with semantic matching and relevance scoring."""
    
    def __init__(self):
        """Initialize the enhanced search."""
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=1000
        )
        
    def _extract_search_intent(self, query: str) -> Dict[str, Any]:
        """Extract search intent and parameters from query."""
        intent_prompt = f"""
        Analyze this search query: "{query}"
        
        Extract the following information:
        1. Product category (medical, appliance, technology, etc.)
        2. Specific product type (wheelchair, air conditioner, etc.)
        3. Brand preferences (if any)
        4. Price range (if mentioned)
        5. Features or specifications (if mentioned)
        6. Urgency level (low, medium, high)
        
        Respond in JSON format:
        {{
            "category": "string",
            "product_type": "string", 
            "brands": ["list"],
            "price_range": {{"min": float, "max": float}},
            "features": ["list"],
            "urgency": "string"
        }}
        """
        
        # Check cache first
        cached_intent = cache_manager.get_llm_cache(intent_prompt)
        if cached_intent:
            try:
                return eval(cached_intent)
            except:
                pass
        
        # Get from LLM
        messages = [
            SystemMessage(content="You are a search intent analyzer. Extract structured information from user queries."),
            HumanMessage(content=intent_prompt)
        ]
        
        response = llm.invoke(messages)
        intent_data = response.content.strip()
        
        # Cache the result
        cache_manager.set_llm_cache(intent_prompt, intent_data)
        
        try:
            return eval(intent_data)
        except:
            # Fallback to basic extraction
            return {
                "category": "general",
                "product_type": query.lower(),
                "brands": [],
                "price_range": {"min": 0, "max": float('inf')},
                "features": [],
                "urgency": "medium"
            }
    
    def _calculate_relevance_score(self, product: Dict[str, Any], intent: Dict[str, Any]) -> float:
        """Calculate relevance score for a product based on search intent."""
        score = 0.0
        
        # Product name relevance
        product_name = product.get('name', '').lower()
        product_type = intent.get('product_type', '').lower()
        
        if product_type in product_name:
            score += 0.4
        
        # Category relevance
        category = intent.get('category', '').lower()
        if category in product_name:
            score += 0.2
        
        # Brand relevance
        brands = intent.get('brands', [])
        for brand in brands:
            if brand.lower() in product_name:
                score += 0.3
                break
        
        # Price relevance
        price_range = intent.get('price_range', {})
        try:
            product_price = float(str(product.get('price', '0')).replace('KWD', '').strip())
            min_price = price_range.get('min', 0)
            max_price = price_range.get('max', float('inf'))
            
            if min_price <= product_price <= max_price:
                score += 0.2
            elif product_price > max_price:
                score -= 0.1  # Penalty for over-budget
        except:
            pass
        
        # Feature relevance
        features = intent.get('features', [])
        for feature in features:
            if feature.lower() in product_name:
                score += 0.1
        
        return max(0.0, min(1.0, score))  # Normalize to 0-1
    
    def _semantic_similarity(self, query: str, products: List[Dict[str, Any]]) -> List[float]:
        """Calculate semantic similarity between query and products."""
        if not products:
            return []
        
        # Prepare text for vectorization
        texts = [query]
        for product in products:
            product_text = f"{product.get('name', '')} {product.get('category', '')}"
            texts.append(product_text)
        
        try:
            # Create TF-IDF vectors
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            
            # Calculate cosine similarity
            similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
            
            return similarities[0].tolist()
        except:
            # Fallback to basic similarity
            return [0.5] * len(products)
    
    def _filter_and_rank_products(self, products: List[Dict[str, Any]], intent: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
        """Filter and rank products based on relevance."""
        if not products:
            return []
        
        # Calculate semantic similarity
        semantic_scores = self._semantic_similarity(query, products)
        
        # Calculate relevance scores and combine with semantic scores
        scored_products = []
        for i, product in enumerate(products):
            relevance_score = self._calculate_relevance_score(product, intent)
            semantic_score = semantic_scores[i] if i < len(semantic_scores) else 0.5
            
            # Combined score (weighted average)
            combined_score = (relevance_score * 0.7) + (semantic_score * 0.3)
            
            scored_products.append({
                **product,
                'relevance_score': combined_score,
                'semantic_score': semantic_score,
                'intent_score': relevance_score
            })
        
        # Sort by combined score (descending)
        scored_products.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Filter by minimum relevance threshold
        threshold = 0.1  # Minimum relevance score
        filtered_products = [p for p in scored_products if p['relevance_score'] >= threshold]
        
        return filtered_products
    
    def search_products(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Enhanced product search with semantic matching and relevance scoring."""
        logger.info(f"Enhanced search for query: {query}")
        
        # Check cache first
        cached_results = cache_manager.get_product_cache(query)
        if cached_results:
            logger.info(f"Using cached results for: {query}")
            return {
                "success": True,
                "query": query,
                "products": cached_results[:max_results],
                "count": len(cached_results),
                "cached": True
            }
        
        # Extract search intent
        intent = self._extract_search_intent(query)
        logger.info(f"Search intent: {intent}")
        
        # Get products from scraping
        try:
            search_result = get_product_prices_from_search(query)
            products = search_result.get('products', [])
        except Exception as e:
            logger.error(f"Error in product search: {e}")
            return {
                "success": False,
                "query": query,
                "error": str(e),
                "products": [],
                "count": 0
            }
        
        # Filter and rank products
        ranked_products = self._filter_and_rank_products(products, intent, query)
        
        # Limit results
        final_products = ranked_products[:max_results]
        
        # Cache the results
        cache_manager.set_product_cache(query, final_products)
        
        return {
            "success": True,
            "query": query,
            "products": final_products,
            "count": len(final_products),
            "intent": intent,
            "cached": False
        }

# Initialize enhanced search
enhanced_search = EnhancedProductSearch()

@tool("enhanced_product_search", return_direct=False)
def enhanced_product_search_tool(query: str, max_results: int = 10) -> dict:
    """
    Enhanced product search with semantic matching, relevance scoring, and intelligent filtering.
    Use this tool for more accurate and relevant product recommendations.
    """
    logging.info("TOOL | enhanced_product_search")
    return enhanced_search.search_products(query, max_results)