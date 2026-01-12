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
        cache_manager.cache["key1"] = {"data": {}, "timestamp": 0, "ttl": 10, "agent_name": "test_agent"}
        
        cache_manager.clear()
        
        assert len(cache_manager.cache) == 0
        assert cache_manager.hits == 0
        assert cache_manager.misses == 0
    
    @pytest.mark.asyncio
    async def test_invalidate_by_agent(self, cache_manager, mock_call_func):
        """Test invalidating cache entries for specific agent."""
        # Add entries for different agents
        await cache_manager.get_or_call("agent1", {"query": "test1"}, mock_call_func)
        await cache_manager.get_or_call("agent2", {"query": "test2"}, mock_call_func)
        await cache_manager.get_or_call("agent1", {"query": "test3"}, mock_call_func)
        
        # Should have 3 entries
        assert len(cache_manager.cache) == 3
        
        # Verify all entries have agent_name stored
        for entry in cache_manager.cache.values():
            assert "agent_name" in entry
            assert entry["agent_name"] in ["agent1", "agent2"]
        
        # Invalidate agent1 entries
        cache_manager.invalidate("agent1")
        
        # Should only have agent2 entry left
        assert len(cache_manager.cache) == 1
        # Verify remaining entry is for agent2
        remaining_entry = next(iter(cache_manager.cache.values()))
        assert remaining_entry["agent_name"] == "agent2"
    
    @pytest.mark.asyncio
    async def test_cache_entry_has_agent_name(self, cache_manager, mock_call_func):
        """Test that cache entries store agent_name."""
        input_data = {"query": "test"}
        
        await cache_manager.get_or_call("test_agent", input_data, mock_call_func)
        
        # Verify cache entry has agent_name
        cache_key = cache_manager.get_cache_key("test_agent", input_data)
        cached_entry = cache_manager.cache[cache_key]
        
        assert "agent_name" in cached_entry
        assert cached_entry["agent_name"] == "test_agent"
        assert "data" in cached_entry
        assert "timestamp" in cached_entry
        assert "ttl" in cached_entry
    
    @pytest.mark.asyncio
    async def test_invalidate_all(self, cache_manager, mock_call_func):
        """Test invalidating all cache entries."""
        # Add some entries
        await cache_manager.get_or_call("agent1", {"query": "test1"}, mock_call_func)
        await cache_manager.get_or_call("agent2", {"query": "test2"}, mock_call_func)
        
        assert len(cache_manager.cache) == 2
        
        # Invalidate all
        cache_manager.invalidate()
        
        assert len(cache_manager.cache) == 0
    
    @pytest.mark.asyncio
    async def test_concurrent_cache_misses_thread_safety(self, cache_manager):
        """Test that concurrent cache misses are properly counted (thread-safety)."""
        async def call_func(input_data):
            await asyncio.sleep(0.01)  # Small delay to allow concurrency
            return {"result": input_data["value"]}
        
        # Create multiple concurrent cache misses with different keys
        num_concurrent = 20
        tasks = [
            cache_manager.get_or_call(
                "test_agent",
                {"value": i},
                call_func
            )
            for i in range(num_concurrent)
        ]
        
        # Execute all concurrently
        await asyncio.gather(*tasks)
        
        # Verify all misses were counted correctly
        stats = cache_manager.get_stats()
        assert stats["misses"] == num_concurrent, \
            f"Expected {num_concurrent} misses, got {stats['misses']}"
        assert stats["hits"] == 0
        assert stats["total_requests"] == num_concurrent
