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
    
    @pytest.mark.asyncio
    async def test_token_recalculation_after_wait(self, rate_limiter):
        """Test that tokens are properly recalculated after waiting."""
        # Use all tokens
        for _ in range(10):
            await rate_limiter.acquire()
        
        # Verify we're at 0 tokens
        assert rate_limiter.tokens == 0
        
        # Record last_update before waiting
        last_update_before = rate_limiter.last_update
        
        # Try to acquire - should wait and then recalculate
        await rate_limiter.acquire()
        
        # After waiting and acquiring, last_update should be updated
        assert rate_limiter.last_update > last_update_before
        
        # Tokens should be properly deducted (should be 0 after acquiring 1 token from empty bucket)
        # Since we waited for 1 token (0.1s at rate 10), we should have 0 tokens left
        assert rate_limiter.tokens == 0
        
        # Wait a bit for tokens to refill
        await asyncio.sleep(0.15)
        
        # Next acquire should be fast (tokens refilled)
        start = asyncio.get_event_loop().time()
        await rate_limiter.acquire()
        elapsed = asyncio.get_event_loop().time() - start
        
        # Should be fast because tokens were refilled
        assert elapsed < 0.05
