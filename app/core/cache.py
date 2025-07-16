"""
Caching system for Al Essa Kuwait chatbot to improve performance and reduce API calls.
"""

import json
import time
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging
import os

logger = logging.getLogger(__name__)

class CacheManager:
    """Manages caching for product searches, LLM responses, and user sessions."""
    
    def __init__(self, cache_dir: str = "cache"):
        """Initialize cache manager."""
        self.cache_dir = cache_dir
        self.product_cache_file = os.path.join(cache_dir, "product_cache.json")
        self.llm_cache_file = os.path.join(cache_dir, "llm_cache.json")
        self.session_cache_file = os.path.join(cache_dir, "session_cache.json")
        
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
        
        # Load existing caches
        self.product_cache = self._load_cache(self.product_cache_file)
        self.llm_cache = self._load_cache(self.llm_cache_file)
        self.session_cache = self._load_cache(self.session_cache_file)
        
        # Cache expiration times (in seconds)
        self.PRODUCT_CACHE_TTL = 3600  # 1 hour for product data
        self.LLM_CACHE_TTL = 1800      # 30 minutes for LLM responses
        self.SESSION_CACHE_TTL = 7200  # 2 hours for session data
        
    def _load_cache(self, cache_file: str) -> Dict[str, Any]:
        """Load cache from file."""
        try:
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load cache from {cache_file}: {e}")
        return {}
    
    def _save_cache(self, cache_file: str, cache_data: Dict[str, Any]) -> None:
        """Save cache to file."""
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save cache to {cache_file}: {e}")
    
    def _generate_key(self, *args) -> str:
        """Generate a cache key from arguments."""
        key_string = "|".join(str(arg) for arg in args)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _is_expired(self, timestamp: float, ttl: int) -> bool:
        """Check if cache entry is expired."""
        return time.time() - timestamp > ttl
    
    def get_product_cache(self, query: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached product search results."""
        key = self._generate_key("product", query)
        if key in self.product_cache:
            entry = self.product_cache[key]
            if not self._is_expired(entry["timestamp"], self.PRODUCT_CACHE_TTL):
                logger.info(f"Cache hit for product query: {query}")
                return entry["data"]
            else:
                # Remove expired entry
                del self.product_cache[key]
        return None
    
    def set_product_cache(self, query: str, products: List[Dict[str, Any]]) -> None:
        """Cache product search results."""
        key = self._generate_key("product", query)
        self.product_cache[key] = {
            "timestamp": time.time(),
            "data": products
        }
        self._save_cache(self.product_cache_file, self.product_cache)
        logger.info(f"Cached product results for query: {query}")
    
    def get_llm_cache(self, prompt: str, model: str = "gpt-4o-mini") -> Optional[str]:
        """Get cached LLM response."""
        key = self._generate_key("llm", prompt, model)
        if key in self.llm_cache:
            entry = self.llm_cache[key]
            if not self._is_expired(entry["timestamp"], self.LLM_CACHE_TTL):
                logger.info(f"Cache hit for LLM response")
                return entry["data"]
            else:
                del self.llm_cache[key]
        return None
    
    def set_llm_cache(self, prompt: str, response: str, model: str = "gpt-4o-mini") -> None:
        """Cache LLM response."""
        key = self._generate_key("llm", prompt, model)
        self.llm_cache[key] = {
            "timestamp": time.time(),
            "data": response
        }
        self._save_cache(self.llm_cache_file, self.llm_cache)
        logger.info(f"Cached LLM response")
    
    def get_session_cache(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get cached session data."""
        if session_id in self.session_cache:
            entry = self.session_cache[session_id]
            if not self._is_expired(entry["timestamp"], self.SESSION_CACHE_TTL):
                return entry["data"]
            else:
                del self.session_cache[session_id]
        return None
    
    def set_session_cache(self, session_id: str, data: Dict[str, Any]) -> None:
        """Cache session data."""
        self.session_cache[session_id] = {
            "timestamp": time.time(),
            "data": data
        }
        self._save_cache(self.session_cache_file, self.session_cache)
    
    def clear_expired_entries(self) -> None:
        """Clear all expired cache entries."""
        current_time = time.time()
        
        # Clear expired product cache entries
        expired_keys = [
            key for key, entry in self.product_cache.items()
            if self._is_expired(entry["timestamp"], self.PRODUCT_CACHE_TTL)
        ]
        for key in expired_keys:
            del self.product_cache[key]
        
        # Clear expired LLM cache entries
        expired_keys = [
            key for key, entry in self.llm_cache.items()
            if self._is_expired(entry["timestamp"], self.LLM_CACHE_TTL)
        ]
        for key in expired_keys:
            del self.llm_cache[key]
        
        # Clear expired session cache entries
        expired_keys = [
            key for key, entry in self.session_cache.items()
            if self._is_expired(entry["timestamp"], self.SESSION_CACHE_TTL)
        ]
        for key in expired_keys:
            del self.session_cache[key]
        
        # Save updated caches
        self._save_cache(self.product_cache_file, self.product_cache)
        self._save_cache(self.llm_cache_file, self.llm_cache)
        self._save_cache(self.session_cache_file, self.session_cache)
        
        logger.info(f"Cleared {len(expired_keys)} expired cache entries")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "product_cache_size": len(self.product_cache),
            "llm_cache_size": len(self.llm_cache),
            "session_cache_size": len(self.session_cache),
            "total_cache_size": len(self.product_cache) + len(self.llm_cache) + len(self.session_cache)
        }

# Initialize global cache manager
cache_manager = CacheManager()