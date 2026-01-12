"""
Workflow Executor

Handles parallel execution of workflow steps with rate limiting.
"""

import asyncio
from typing import Dict, Any, List, Callable, Optional
from loguru import logger

from orchestrator.rate_limiter import RateLimiter
from orchestrator.exceptions import RateLimitExceededError


class WorkflowExecutor:
    """
    Executes workflow steps with parallelization and rate limiting.
    """
    
    def __init__(self):
        """Initialize workflow executor."""
        self.rate_limiters = {}  # Per-agent rate limiters
    
    def _get_rate_limiter(self, agent_name: str, rate_limit: int = 10) -> RateLimiter:
        """Get or create rate limiter for agent."""
        if agent_name not in self.rate_limiters:
            self.rate_limiters[agent_name] = RateLimiter(rate=rate_limit)
        return self.rate_limiters[agent_name]
    
    async def execute_parallel(
        self,
        agent_name: str,
        inputs: List[Dict[str, Any]],
        call_func: Callable,
        max_concurrent: int = 5,
        rate_limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Execute agent calls in parallel with rate limiting.
        
        Args:
            agent_name: Name of agent
            inputs: List of input dictionaries
            call_func: Function to call for each input
            max_concurrent: Maximum concurrent executions
            rate_limit: Rate limit per second
        
        Returns:
            List of results (or error dicts)
        """
        if not inputs:
            return []
        
        semaphore = asyncio.Semaphore(max_concurrent)
        rate_limiter = self._get_rate_limiter(agent_name, rate_limit)
        
        async def bounded_call(input_data: Dict[str, Any]) -> Dict[str, Any]:
            """Execute call with concurrency and rate limiting."""
            async with semaphore:
                try:
                    await rate_limiter.acquire()
                    result = await call_func(input_data)
                    return result
                except Exception as e:
                    logger.error(f"Agent call failed for {agent_name}: {e}")
                    return {"error": str(e), "input": input_data}
        
        # Execute all calls in parallel
        tasks = [bounded_call(inp) for inp in inputs]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Task {i} failed: {result}")
                processed_results.append({
                    "error": str(result),
                    "input": inputs[i]
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def execute_sequential(
        self,
        agent_name: str,
        inputs: List[Dict[str, Any]],
        call_func: Callable,
        rate_limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Execute agent calls sequentially with rate limiting.
        
        Args:
            agent_name: Name of agent
            inputs: List of input dictionaries
            call_func: Function to call for each input
            rate_limit: Rate limit per second
        
        Returns:
            List of results
        """
        results = []
        rate_limiter = self._get_rate_limiter(agent_name, rate_limit)
        
        for input_data in inputs:
            try:
                await rate_limiter.acquire()
                result = await call_func(input_data)
                results.append(result)
            except Exception as e:
                logger.error(f"Agent call failed for {agent_name}: {e}")
                results.append({"error": str(e), "input": input_data})
        
        return results
