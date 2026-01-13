"""
Cache Manager

Multi-level caching for agent outputs with TTL.
"""

import time
import json
import hashlib
import asyncio
from typing import Dict, Any, Callable, Optional
from collections import OrderedDict
from loguru import logger

# Maximum input size in bytes (1MB)
MAX_INPUT_SIZE = 1024 * 1024


class CacheManager:
    """
    Manages caching for agent outputs.
    
    Features:
    - TTL-based expiration
    - LRU eviction for size limits
    - Cache key generation from inputs
    """
    
    def __init__(self, default_ttl: int = 300, max_size: int = 1000):
        """
        Initialize cache manager.
        
        Args:
            default_ttl: Default TTL in seconds
            max_size: Maximum cache entries
        """
        self.cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self.default_ttl = default_ttl
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
        self._lock = asyncio.Lock()  # Thread safety for async operations
    
    def get_cache_key(self, agent_name: str, input_data: Dict[str, Any]) -> str:
        """
        Generate cache key from agent name and input.
        
        Args:
            agent_name: Name of agent
            input_data: Input data dictionary
        
        Returns:
            Cache key (MD5 hash)
        """
        # Sort keys for consistent hashing
        sorted_data = json.dumps(input_data, sort_keys=True)
        key_data = f"{agent_name}:{sorted_data}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def get_or_call(
        self,
        agent_name: str,
        input_data: Dict[str, Any],
        call_func: Callable,
        ttl: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get from cache or call agent.
        
        Args:
            agent_name: Name of agent
            input_data: Input data
            call_func: Function to call if cache miss (can be sync or async)
            ttl: TTL in seconds (uses default if None)
        
        Returns:
            Agent output
        
        Raises:
            ValueError: If input_data exceeds maximum size
        """
        # Validate input size
        input_size = len(json.dumps(input_data).encode('utf-8'))
        if input_size > MAX_INPUT_SIZE:
            raise ValueError(
                f"Input data size ({input_size} bytes) exceeds maximum "
                f"allowed size ({MAX_INPUT_SIZE} bytes)"
            )
        
        cache_key = self.get_cache_key(agent_name, input_data)
        ttl = ttl or self.default_ttl
        
        # Thread-safe cache access
        cache_miss = False
        async with self._lock:
            # Check cache
            if cache_key in self.cache:
                cached = self.cache[cache_key]
                age = time.time() - cached["timestamp"]
                # Use stored TTL for expiration check
                stored_ttl = cached.get("ttl", self.default_ttl)
                
                if age < stored_ttl:
                    # Cache hit
                    self.hits += 1
                    logger.debug(f"Cache hit for {agent_name}")
                    # Move to end (LRU)
                    self.cache.move_to_end(cache_key)
                    return cached["data"]
                else:
                    # Expired - remove
                    logger.debug(f"Cache expired for {agent_name}")
                    del self.cache[cache_key]
                    cache_miss = True
            else:
                # Key not in cache
                cache_miss = True
            
            # Increment miss counter inside lock for thread safety
            if cache_miss:
                self.misses += 1
                logger.debug(f"Cache miss for {agent_name}")
        
        # Cache miss - call agent (outside lock to avoid blocking)
        
        # Handle both sync and async call_func
        if asyncio.iscoroutinefunction(call_func):
            result = await call_func(input_data)
        else:
            # Sync function - run in executor
            result = await asyncio.get_event_loop().run_in_executor(
                None, call_func, input_data
            )
        
        # Thread-safe cache storage
        async with self._lock:
            # Store in cache
            self._store_in_cache(cache_key, result, ttl, agent_name)
        
        return result
    
    def _store_in_cache(self, cache_key: str, data: Dict[str, Any], ttl: int, agent_name: str):
        """Store data in cache with size limit."""
        # Remove oldest if at capacity
        if len(self.cache) >= self.max_size:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            logger.debug(f"Evicted cache entry: {oldest_key}")
        
        # Store new entry with agent_name for invalidation
        self.cache[cache_key] = {
            "data": data,
            "timestamp": time.time(),
            "ttl": ttl,
            "agent_name": agent_name
        }
        # Move to end (LRU)
        self.cache.move_to_end(cache_key)
    
    def clear(self):
        """Clear all cache entries."""
        # Note: This is a sync method, but cache operations should be thread-safe
        # In async context, use async with lock if needed
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "total_requests": total_requests
        }
    
    def invalidate(self, agent_name: Optional[str] = None):
        """
        Invalidate cache entries.
        
        Args:
            agent_name: If provided, invalidate only this agent's entries
        """
        if agent_name:
            # Remove entries for specific agent
            # Now that agent_name is stored in cache entries, this will work correctly
            keys_to_remove = [
                key for key, entry in self.cache.items()
                if entry.get("agent_name") == agent_name
            ]
            for key in keys_to_remove:
                del self.cache[key]
            logger.info(f"Invalidated {len(keys_to_remove)} cache entries for {agent_name}")
        else:
            # Clear all
            self.clear()