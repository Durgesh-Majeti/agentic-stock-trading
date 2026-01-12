"""Unit tests for CacheManager."""
import pytest
import asyncio
from orchestrator.cache_manager import CacheManager


class TestCacheManager:
    """Test cases for CacheManager."""
    
    @pytest.fixture
    def cache_manager(self):
        """Create cache manager instance."""
        return CacheManager(default_ttl=1, max_size=10)
    
    @pytest.fixture
    def mock_call_func(self):
        """Create mock call function."""
        call_count = 0
        
        async def call_func(input_data):
            nonlocal call_count
            call_count += 1
            return {"result": call_count, "input": input_data}
        
        return call_func
    
    @pytest.mark.asyncio
    async def test_cache_hit(self, cache_manager, mock_call_func):
        """Test cache hit."""
        input_data = {"query": "test"}
        
        # First call - cache miss
        result1 = await cache_manager.get_or_call(
            "test_agent",
            input_data,
            mock_call_func
        )
        
        # Second call - cache hit
        result2 = await cache_manager.get_or_call(
            "test_agent",
            input_data,
            mock_call_func
        )
        
        assert result1 == result2
        assert result1["result"] == 1  # Only called once
    
    @pytest.mark.asyncio
    async def test_cache_expiration(self, cache_manager, mock_call_func):
        """Test cache expiration."""
        input_data = {"query": "test"}
        
        # First call
        await cache_manager.get_or_call(
            "test_agent",
            input_data,
            mock_call_func,
            ttl=0.1
        )
        
        # Wait for expiration
        await asyncio.sleep(0.2)
        
        # Second call - should be cache miss
        result = await cache_manager.get_or_call(
            "test_agent",
            input_data,
            mock_call_func
        )
        
        assert result["result"] == 2  # Called again
    
    @pytest.mark.asyncio
    async def test_cache_eviction(self, cache_manager, mock_call_func):
        """Test LRU cache eviction."""
        # Fill cache beyond max_size
        for i in range(15):
            await cache_manager.get_or_call(
                "test_agent",
                {"value": i},
                mock_call_func
            )
        
        # Cache should have evicted oldest entries
        stats = cache_manager.get_stats()
        assert stats["size"] == 10
    
    def test_get_cache_key(self, cache_manager):
        """Test cache key generation."""
        key1 = cache_manager.get_cache_key("agent", {"a": 1, "b": 2})
        key2 = cache_manager.get_cache_key("agent", {"b": 2, "a": 1})
        
        # Should be same (order-independent)
        assert key1 == key2
    
    def test_get_stats(self, cache_manager):
        """Test cache statistics."""
        stats = cache_manager.get_stats()
        
        assert "size" in stats
        assert "hits" in stats
        assert "misses" in stats
        assert "hit_rate" in stats
    
    def test_clear(self, cache_manager):
        """Test cache clearing."""
        # Add some entries
        cache_manager.cache["key1"] = {"data": {}, "timestamp": 0, "ttl": 10}
        
        cache_manager.clear()
        
        assert len(cache_manager.cache) == 0
        assert cache_manager.hits == 0
        assert cache_manager.misses == 0
