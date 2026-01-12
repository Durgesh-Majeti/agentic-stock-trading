"""
Orchestrator Monitoring

Observability and metrics collection.
"""

import time
from typing import Dict, Any, Optional
from contextlib import contextmanager
from collections import defaultdict
from loguru import logger


class Counter:
    """Simple counter for metrics."""
    
    def __init__(self):
        self.value = 0
        self.labels: Dict[str, int] = defaultdict(int)
    
    def inc(self, labels: Optional[Dict[str, str]] = None):
        """Increment counter."""
        self.value += 1
        if labels:
            key = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
            self.labels[key] += 1
    
    def get(self, labels: Optional[Dict[str, str]] = None) -> int:
        """Get counter value."""
        if labels:
            key = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
            return self.labels.get(key, 0)
        return self.value


class Histogram:
    """Simple histogram for metrics."""
    
    def __init__(self):
        self.values: Dict[str, list] = defaultdict(list)
    
    def observe(self, value: float, labels: Optional[Dict[str, str]] = None):
        """Record a value."""
        key = ",".join(f"{k}={v}" for k, v in sorted(labels.items())) if labels else "default"
        self.values[key].append(value)
    
    def mean(self, labels: Optional[Dict[str, str]] = None) -> float:
        """Get mean value."""
        key = ",".join(f"{k}={v}" for k, v in sorted(labels.items())) if labels else "default"
        values = self.values.get(key, [])
        return sum(values) / len(values) if values else 0.0


class WorkflowTracker:
    """Context manager for tracking workflow execution."""
    
    def __init__(self, workflow_name: str, metrics: Dict[str, Any]):
        self.workflow_name = workflow_name
        self.metrics = metrics
        self.start_time: Optional[float] = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.metrics["workflow_executions"].inc({"workflow": self.workflow_name})
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            self.metrics["durations"].observe(
                duration,
                {"workflow": self.workflow_name}
            )
            if exc_type:
                self.metrics["errors"].inc({"workflow": self.workflow_name})


class OrchestratorMonitor:
    """
    Tracks orchestrator performance and health.
    
    Collects metrics for:
    - Workflow executions
    - Agent calls
    - Errors
    - Durations
    - Cache performance
    """
    
    def __init__(self):
        """Initialize monitor."""
        self.metrics = {
            "workflow_executions": Counter(),
            "agent_calls": Counter(),
            "errors": Counter(),
            "durations": Histogram(),
            "cache_hits": Counter(),
            "cache_misses": Counter()
        }
        self.start_times: Dict[str, float] = {}
    
    def track_workflow(self, workflow_name: str):
        """
        Track workflow execution.
        
        Args:
            workflow_name: Name of workflow
        
        Returns:
            WorkflowTracker context manager
        """
        return WorkflowTracker(workflow_name, self.metrics)
    
    def track_agent_call(
        self,
        agent_name: str,
        duration: float,
        success: bool
    ):
        """
        Track agent call metrics.
        
        Args:
            agent_name: Name of agent
            duration: Call duration in seconds
            success: Whether call succeeded
        """
        self.metrics["agent_calls"].inc({"agent": agent_name})
        self.metrics["durations"].observe(
            duration,
            {"agent": agent_name}
        )
        if not success:
            self.metrics["errors"].inc({"agent": agent_name})
    
    def track_cache_hit(self, agent_name: str):
        """Track cache hit."""
        self.metrics["cache_hits"].inc({"agent": agent_name})
    
    def track_cache_miss(self, agent_name: str):
        """Track cache miss."""
        self.metrics["cache_misses"].inc({"agent": agent_name})
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current metrics snapshot.
        
        Returns:
            Dictionary of metrics
        """
        return {
            "workflow_executions": {
                "total": self.metrics["workflow_executions"].value,
                "by_workflow": dict(self.metrics["workflow_executions"].labels)
            },
            "agent_calls": {
                "total": self.metrics["agent_calls"].value,
                "by_agent": dict(self.metrics["agent_calls"].labels)
            },
            "errors": {
                "total": self.metrics["errors"].value,
                "by_agent": dict(self.metrics["errors"].labels)
            },
            "avg_durations": {
                agent: self.metrics["durations"].mean({"agent": agent})
                for agent in set(
                    k.split(",")[0].split("=")[1]
                    for k in self.metrics["durations"].values.keys()
                    if "agent=" in k
                )
            },
            "cache": {
                "hits": self.metrics["cache_hits"].value,
                "misses": self.metrics["cache_misses"].value,
                "hit_rate": (
                    self.metrics["cache_hits"].value /
                    (self.metrics["cache_hits"].value + self.metrics["cache_misses"].value) * 100
                    if (self.metrics["cache_hits"].value + self.metrics["cache_misses"].value) > 0
                    else 0
                )
            }
        }
    
    def reset(self):
        """Reset all metrics."""
        for metric in self.metrics.values():
            if isinstance(metric, Counter):
                metric.value = 0
                metric.labels.clear()
            elif isinstance(metric, Histogram):
                metric.values.clear()
        logger.info("Metrics reset")
