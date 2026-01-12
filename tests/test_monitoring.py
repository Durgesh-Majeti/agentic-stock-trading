"""Unit tests for OrchestratorMonitor."""
import pytest
import time
from orchestrator.monitoring import OrchestratorMonitor


class TestOrchestratorMonitor:
    """Test cases for OrchestratorMonitor."""
    
    @pytest.fixture
    def monitor(self):
        """Create monitor instance."""
        return OrchestratorMonitor()
    
    def test_track_agent_call_success(self, monitor):
        """Test tracking successful agent call."""
        monitor.track_agent_call("test_agent", 0.5, True)
        
        metrics = monitor.get_metrics()
        assert metrics["agent_calls"]["total"] == 1
        assert metrics["errors"]["total"] == 0
    
    def test_track_agent_call_failure(self, monitor):
        """Test tracking failed agent call."""
        monitor.track_agent_call("test_agent", 0.5, False)
        
        metrics = monitor.get_metrics()
        assert metrics["agent_calls"]["total"] == 1
        assert metrics["errors"]["total"] == 1
    
    def test_track_workflow(self, monitor):
        """Test tracking workflow execution."""
        with monitor.track_workflow("test_workflow"):
            time.sleep(0.01)
        
        metrics = monitor.get_metrics()
        assert metrics["workflow_executions"]["total"] == 1
    
    def test_track_cache(self, monitor):
        """Test tracking cache hits/misses."""
        monitor.track_cache_hit("test_agent")
        monitor.track_cache_miss("test_agent")
        monitor.track_cache_hit("test_agent")
        
        metrics = monitor.get_metrics()
        assert metrics["cache"]["hits"] == 2
        assert metrics["cache"]["misses"] == 1
        assert metrics["cache"]["hit_rate"] == pytest.approx(66.67, abs=0.01)
    
    def test_get_metrics(self, monitor):
        """Test getting metrics."""
        monitor.track_agent_call("agent1", 0.1, True)
        monitor.track_agent_call("agent2", 0.2, True)
        
        metrics = monitor.get_metrics()
        
        assert "workflow_executions" in metrics
        assert "agent_calls" in metrics
        assert "errors" in metrics
        assert "avg_durations" in metrics
        assert "cache" in metrics
    
    def test_reset(self, monitor):
        """Test resetting metrics."""
        monitor.track_agent_call("test_agent", 0.5, True)
        monitor.track_cache_hit("test_agent")
        
        monitor.reset()
        
        metrics = monitor.get_metrics()
        assert metrics["agent_calls"]["total"] == 0
        assert metrics["cache"]["hits"] == 0
