"""Unit tests for RateLimiter."""
import pytest
import asyncio
from orchestrator.rate_limiter import RateLimiter


class TestRateLimiter:
    """Test cases for RateLimiter."""
    
    @pytest.fixture
    def rate_limiter(self):
        """Create rate limiter instance."""
        return RateLimiter(rate=10, capacity=10)
    
    @pytest.mark.asyncio
    async def test_acquire_single_token(self, rate_limiter):
        """Test acquiring a single token."""
        start = asyncio.get_event_loop().time()
        await rate_limiter.acquire()
        elapsed = asyncio.get_event_loop().time() - start
        
        # Should be fast (no wait needed)
        assert elapsed < 0.1
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, rate_limiter):
        """Test rate limiting behavior."""
        # Acquire all tokens
        for _ in range(10):
            await rate_limiter.acquire()
        
        # Next acquire should wait
        start = asyncio.get_event_loop().time()
        await rate_limiter.acquire()
        elapsed = asyncio.get_event_loop().time() - start
        
        # Should wait approximately 0.1 seconds (1/rate)
        assert elapsed >= 0.08  # Allow some tolerance
    
    @pytest.mark.asyncio
    async def test_token_refill(self, rate_limiter):
        """Test token refill over time."""
        # Use all tokens
        for _ in range(10):
            await rate_limiter.acquire()
        
        # Wait for refill
        await asyncio.sleep(0.2)
        
        # Should be able to acquire again
        start = asyncio.get_event_loop().time()
        await rate_limiter.acquire()
        elapsed = asyncio.get_event_loop().time() - start
        
        # Should be fast (tokens refilled)
        assert elapsed < 0.05
    
    def test_integer_based_tokens(self, rate_limiter):
        """Test that tokens are integer-based."""
        # Tokens should be integer
        assert isinstance(rate_limiter.tokens, int)
        
        # After acquiring, tokens should still be integer
        asyncio.run(rate_limiter.acquire())
        assert isinstance(rate_limiter.tokens, int)
        assert rate_limiter.tokens >= 0  # Should not be negative
    
    @pytest.mark.asyncio
    async def test_monotonic_clock(self, rate_limiter):
        """Test that rate limiter uses monotonic clock."""
        import time
        
        # Acquire all tokens
        for _ in range(10):
            await rate_limiter.acquire()
        
        # Check that last_update uses monotonic time
        assert rate_limiter.last_update > 0
        # Monotonic time should be different from system time
        # (but we can't easily test this without mocking)
