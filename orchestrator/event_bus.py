"""
Event Bus

Event-driven architecture for decoupled communication.
"""

import asyncio
from typing import Dict, Any, Callable, List, Optional
from collections import defaultdict
from loguru import logger


class EventBus:
    """
    Event bus for pub/sub pattern.
    
    Allows agents and components to communicate asynchronously
    without direct dependencies.
    """
    
    def __init__(self):
        """Initialize event bus."""
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.event_history: List[Dict[str, Any]] = []
        self.max_history = 1000
    
    def subscribe(self, event_type: str, handler: Callable):
        """
        Subscribe to event type.
        
        Args:
            event_type: Type of event (e.g., "trade.executed")
            handler: Async function to handle event
        """
        if handler not in self.subscribers[event_type]:
            self.subscribers[event_type].append(handler)
            handler_name = getattr(handler, '__name__', str(handler))
            logger.info(f"Subscribed {handler_name} to {event_type}")
    
    def unsubscribe(self, event_type: str, handler: Callable):
        """
        Unsubscribe from event type.
        
        Args:
            event_type: Type of event
            handler: Handler to remove
        """
        if handler in self.subscribers[event_type]:
            self.subscribers[event_type].remove(handler)
            handler_name = getattr(handler, '__name__', str(handler))
            logger.info(f"Unsubscribed {handler_name} from {event_type}")
    
    async def publish(self, event_type: str, event_data: Dict[str, Any]):
        """
        Publish event to all subscribers.
        
        Args:
            event_type: Type of event
            event_data: Event data
        """
        event = {
            "type": event_type,
            "data": event_data,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        # Add to history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)
        
        # Get subscribers
        handlers = self.subscribers.get(event_type, [])
        
        if not handlers:
            logger.debug(f"No subscribers for event: {event_type}")
            return
        
        # Dispatch to all subscribers
        tasks = []
        for handler in handlers:
            try:
                task = handler(event_data)
                if asyncio.iscoroutine(task):
                    tasks.append(task)
                # Synchronous handler - already called above, don't call again
            except Exception as e:
                handler_name = getattr(handler, '__name__', str(handler))
                logger.error(f"Error in event handler {handler_name}: {e}")
        
        # Wait for async handlers
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.debug(
            f"Published event {event_type} to {len(handlers)} subscribers"
        )
    
    def get_subscribers(self, event_type: str) -> List[Callable]:
        """Get all subscribers for event type."""
        return self.subscribers.get(event_type, [])
    
    def get_event_history(
        self,
        event_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get event history.
        
        Args:
            event_type: Optional filter by event type
            limit: Maximum number of events
        
        Returns:
            List of events
        """
        events = self.event_history
        
        if event_type:
            events = [e for e in events if e["type"] == event_type]
        
        return events[-limit:]
    
    def clear_history(self):
        """Clear event history."""
        self.event_history.clear()
        logger.info("Event history cleared")
