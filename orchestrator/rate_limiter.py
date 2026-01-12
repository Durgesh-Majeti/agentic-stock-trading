"""
Rate Limiter Implementation

Token bucket algorithm for rate limiting agent calls.
Uses integer-based token counting to avoid floating point precision issues.
"""

import asyncio
import time
from typing import Optional
from loguru import logger


class RateLimiter:
    """
    Token bucket rate limiter.
    
    Allows a certain number of requests per second.
    """
    
    def __init__(self, rate: int = 10, capacity: Optional[int] = None):
        """
        Initialize rate limiter.
        
        Args:
            rate: Number of requests per second
            capacity: Maximum tokens (defaults to rate)
        """
        self.rate = rate
        self.capacity = capacity or rate
        # Use integer-based token counting to avoid floating point precision issues
        self.tokens: int = self.capacity
        # Use monotonic clock for elapsed time calculations (immune to clock adjustments)
        self.last_update: float = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def acquire(self, tokens: int = 1):
        """
        Acquire tokens, waiting if necessary.
        
        Args:
            tokens: Number of tokens to acquire (default: 1)
        """
        async with self._lock:
            # Refill tokens based on elapsed time using integer arithmetic
            now = time.monotonic()
            elapsed = now - self.last_update
            
            # Calculate tokens to add (using integer division to avoid precision issues)
            # Convert elapsed time to milliseconds for integer math
            elapsed_ms = int(elapsed * 1000)
            tokens_to_add = (elapsed_ms * self.rate) // 1000
            
            # Refill tokens (ensure we don't exceed capacity)
            self.tokens = min(
                self.capacity,
                self.tokens + tokens_to_add
            )
            self.last_update = now
            
            # Ensure tokens is non-negative (bounds checking)
            if self.tokens < 0:
                self.tokens = 0
            
            # Wait if not enough tokens
            if self.tokens < tokens:
                # Calculate wait time in seconds
                tokens_needed = tokens - self.tokens
                wait_time = tokens_needed / self.rate
                logger.debug(f"Rate limit: waiting {wait_time:.2f}s for {tokens_needed} tokens")
                await asyncio.sleep(wait_time)
                # After waiting, we should have enough tokens
                self.tokens = 0
            else:
                # Deduct tokens
                self.tokens -= tokens
                # Ensure non-negative
                if self.tokens < 0:
                    self.tokens = 0
