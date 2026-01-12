"""Unit tests for CircuitBreaker."""
import pytest
import asyncio
from orchestrator.circuit_breaker import CircuitBreaker, CircuitBreakerOpenError


class TestCircuitBreaker:
    """Test cases for CircuitBreaker."""
    
    @pytest.fixture
    def circuit_breaker(self):
        """Create circuit breaker instance."""
        return CircuitBreaker(failure_threshold=3, timeout=1)
    
    @pytest.mark.asyncio
    async def test_successful_call(self, circuit_breaker):
        """Test successful function call."""
        async def success_func():
            return "success"
        
        result = await circuit_breaker.call(success_func)
        assert result == "success"
        assert circuit_breaker.get_state() == "CLOSED"
    
    @pytest.mark.asyncio
    async def test_failure_accumulation(self, circuit_breaker):
        """Test failure accumulation."""
        async def failing_func():
            raise ValueError("Test error")
        
        # Fail 3 times (threshold)
        for _ in range(3):
            with pytest.raises(ValueError):
                await circuit_breaker.call(failing_func)
        
        # Circuit should be OPEN
        assert circuit_breaker.get_state() == "OPEN"
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_open(self, circuit_breaker):
        """Test circuit breaker rejecting calls when OPEN."""
        async def failing_func():
            raise ValueError("Test error")
        
        # Open circuit
        for _ in range(3):
            with pytest.raises(ValueError):
                await circuit_breaker.call(failing_func)
        
        # Next call should be rejected
        with pytest.raises(CircuitBreakerOpenError):
            await circuit_breaker.call(failing_func)
    
    @pytest.mark.asyncio
    async def test_half_open_recovery(self, circuit_breaker):
        """Test circuit breaker recovery through half-open."""
        async def failing_func():
            raise ValueError("Test error")
        
        async def success_func():
            return "success"
        
        # Open circuit
        for _ in range(3):
            with pytest.raises(ValueError):
                await circuit_breaker.call(failing_func)
        
        # Wait for timeout
        await asyncio.sleep(1.1)
        
        # Should transition to HALF_OPEN and then CLOSED
        for _ in range(3):
            result = await circuit_breaker.call(success_func)
            assert result == "success"
        
        assert circuit_breaker.get_state() == "CLOSED"
    
    def test_reset(self, circuit_breaker):
        """Test manual reset."""
        circuit_breaker.failure_count = 5
        circuit_breaker.state = "OPEN"
        
        circuit_breaker.reset()
        
        assert circuit_breaker.get_state() == "CLOSED"
        assert circuit_breaker.failure_count == 0
    
    @pytest.mark.asyncio
    async def test_sync_function_call(self, circuit_breaker):
        """Test circuit breaker with synchronous function."""
        def sync_func(x, y):
            return x + y
        
        result = await circuit_breaker.call(sync_func, 2, 3)
        assert result == 5
        assert circuit_breaker.get_state() == "CLOSED"
    
    @pytest.mark.asyncio
    async def test_async_function_call(self, circuit_breaker):
        """Test circuit breaker with asynchronous function."""
        async def async_func(x, y):
            return x * y
        
        result = await circuit_breaker.call(async_func, 2, 3)
        assert result == 6
        assert circuit_breaker.get_state() == "CLOSED"
    
    @pytest.mark.asyncio
    async def test_sync_function_failure(self, circuit_breaker):
        """Test circuit breaker with failing synchronous function."""
        def sync_failing_func():
            raise ValueError("Sync error")
        
        with pytest.raises(ValueError):
            await circuit_breaker.call(sync_failing_func)
        
        assert circuit_breaker.failure_count == 1
