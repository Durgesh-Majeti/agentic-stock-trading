"""Unit tests for EventBus."""
import pytest
import asyncio
from unittest.mock import AsyncMock, Mock
from orchestrator.event_bus import EventBus


class TestEventBus:
    """Test cases for EventBus."""
    
    @pytest.fixture
    def event_bus(self):
        """Create event bus instance."""
        return EventBus()
    
    @pytest.mark.asyncio
    async def test_subscribe_and_publish(self, event_bus):
        """Test subscribing and publishing events."""
        handler_called = []
        
        async def handler(data):
            handler_called.append(data)
        
        event_bus.subscribe("test.event", handler)
        await event_bus.publish("test.event", {"value": "test"})
        
        assert len(handler_called) == 1
        assert handler_called[0]["value"] == "test"
    
    @pytest.mark.asyncio
    async def test_multiple_subscribers(self, event_bus):
        """Test multiple subscribers for same event."""
        calls = []
        
        async def handler1(data):
            calls.append("handler1")
        
        async def handler2(data):
            calls.append("handler2")
        
        event_bus.subscribe("test.event", handler1)
        event_bus.subscribe("test.event", handler2)
        
        await event_bus.publish("test.event", {})
        
        assert len(calls) == 2
        assert "handler1" in calls
        assert "handler2" in calls
    
    @pytest.mark.asyncio
    async def test_no_subscribers(self, event_bus):
        """Test publishing with no subscribers."""
        # Should not raise error
        await event_bus.publish("test.event", {})
    
    @pytest.mark.asyncio
    async def test_sync_handler(self, event_bus):
        """Test synchronous handler."""
        handler_called = []
        
        def sync_handler(data):
            handler_called.append(data)
        
        event_bus.subscribe("test.event", sync_handler)
        await event_bus.publish("test.event", {"value": "test"})
        
        assert len(handler_called) == 1
    
    @pytest.mark.asyncio
    async def test_handler_error(self, event_bus):
        """Test handler error handling."""
        async def failing_handler(data):
            raise ValueError("Test error")
        
        async def success_handler(data):
            return "success"
        
        event_bus.subscribe("test.event", failing_handler)
        event_bus.subscribe("test.event", success_handler)
        
        # Should not raise error
        await event_bus.publish("test.event", {})
    
    def test_unsubscribe(self, event_bus):
        """Test unsubscribing."""
        handler = Mock()
        
        event_bus.subscribe("test.event", handler)
        assert len(event_bus.get_subscribers("test.event")) == 1
        
        event_bus.unsubscribe("test.event", handler)
        assert len(event_bus.get_subscribers("test.event")) == 0
    
    def test_get_event_history(self, event_bus):
        """Test getting event history."""
        # Publish some events
        asyncio.run(event_bus.publish("event1", {"data": 1}))
        asyncio.run(event_bus.publish("event2", {"data": 2}))
        asyncio.run(event_bus.publish("event1", {"data": 3}))
        
        history = event_bus.get_event_history()
        assert len(history) >= 3
        
        filtered = event_bus.get_event_history("event1")
        assert len(filtered) >= 2
    
    def test_clear_history(self, event_bus):
        """Test clearing event history."""
        asyncio.run(event_bus.publish("test.event", {}))
        assert len(event_bus.event_history) > 0
        
        event_bus.clear_history()
        assert len(event_bus.event_history) == 0
