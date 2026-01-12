"""
Rate Limiter Implementation

Token bucket algorithm for rate limiting agent calls.
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
        self.tokens = self.capacity
        self.last_update = time.time()
        self._lock = asyncio.Lock()
    
    async def acquire(self, tokens: int = 1):
        """
        Acquire tokens, waiting if necessary.
        
        Args:
            tokens: Number of tokens to acquire (default: 1)
        """
        async with self._lock:
            # Refill tokens based on elapsed time
            now = time.time()
            elapsed = now - self.last_update
            self.tokens = min(
                self.capacity,
                self.tokens + elapsed * self.rate
            )
            self.last_update = now
            
            # Wait if not enough tokens
            if self.tokens < tokens:
                wait_time = (tokens - self.tokens) / self.rate
                logger.debug(f"Rate limit: waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= tokens
