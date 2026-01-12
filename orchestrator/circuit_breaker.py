"""
Circuit Breaker Pattern

Prevents cascading failures by stopping calls to failing agents.
"""

import time
import asyncio
from typing import Callable, Any, Optional
from loguru import logger

from orchestrator.exceptions import CircuitBreakerOpenError


class CircuitBreaker:
    """
    Circuit breaker pattern for agent calls.
    
    Three states:
    - CLOSED: Normal operation
    - OPEN: Failing, reject calls
    - HALF_OPEN: Testing if service recovered
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        half_open_max_calls: int = 3
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening
            timeout: Seconds before trying half-open
            half_open_max_calls: Successful calls needed to close
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.half_open_max_calls = half_open_max_calls
        
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.half_open_calls = 0
        self.success_count = 0
        self._lock = asyncio.Lock()  # Thread safety for state updates
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Function to call (can be sync or async)
            *args: Function arguments
            **kwargs: Function keyword arguments
        
        Returns:
            Function result
        
        Raises:
            CircuitBreakerOpenError: If circuit is open
        """
        # Thread-safe state check
        async with self._lock:
            # Check if circuit is open
            if self.state == "OPEN":
                if self.last_failure_time and \
                   time.time() - self.last_failure_time > self.timeout:
                    # Try half-open
                    self.state = "HALF_OPEN"
                    self.half_open_calls = 0
                    self.success_count = 0
                    logger.info("Circuit breaker transitioning to HALF_OPEN")
                else:
                    raise CircuitBreakerOpenError(
                        f"Circuit breaker is OPEN. "
                        f"Retry after {self.timeout} seconds"
                    )
        
        # Execute function with proper async/sync detection
        try:
            # Use asyncio.iscoroutinefunction to properly detect async functions
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                # Sync function - run in executor to avoid blocking event loop
                result = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: func(*args, **kwargs)
                )
            
            # Thread-safe state update on success
            async with self._lock:
                if self.state == "HALF_OPEN":
                    self.half_open_calls += 1
                    self.success_count += 1
                    if self.half_open_calls >= self.half_open_max_calls:
                        self.state = "CLOSED"
                        self.failure_count = 0
                        logger.info("Circuit breaker CLOSED after recovery")
                elif self.state == "CLOSED":
                    self.failure_count = 0
            
            return result
            
        except Exception as e:
            # Thread-safe state update on failure
            async with self._lock:
                self.failure_count += 1
                self.last_failure_time = time.time()
                
                if self.state == "HALF_OPEN":
                    # Failed during half-open - go back to open
                    self.state = "OPEN"
                    logger.warning("Circuit breaker OPEN after half-open failure")
                elif self.failure_count >= self.failure_threshold:
                    self.state = "OPEN"
                    logger.warning(
                        f"Circuit breaker OPEN after {self.failure_count} failures"
                    )
            
            raise
    
    def reset(self):
        """Manually reset circuit breaker to CLOSED."""
        self.state = "CLOSED"
        self.failure_count = 0
        self.last_failure_time = None
        self.half_open_calls = 0
        self.success_count = 0
        logger.info("Circuit breaker manually reset")
    
    def get_state(self) -> str:
        """Get current circuit breaker state."""
        return self.state