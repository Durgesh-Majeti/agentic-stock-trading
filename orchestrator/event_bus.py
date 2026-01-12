"""
Event Bus

Event-driven architecture for decoupled communication.
"""

import asyncio
from typing import Dict, Any, Callable, List, Optional
from collections import defaultdict, deque
from loguru import logger


class EventBus:
    """
    Event bus for pub/sub pattern.
    
    Allows agents and components to communicate asynchronously
    without direct dependencies.
    """
    
    def __init__(self, max_history: int = 1000, max_retries: int = 3):
        """
        Initialize event bus.
        
        Args:
            max_history: Maximum number of events to keep in history
            max_retries: Maximum retry attempts for failed handlers
        """
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        # Use deque for O(1) append/popleft operations
        self.event_history: deque = deque(maxlen=max_history)
        self.max_history = max_history
        self.max_retries = max_retries
        self.dead_letter_queue: List[Dict[str, Any]] = []
    
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
        Publish event to all subscribers with retry mechanism.
        
        Args:
            event_type: Type of event
            event_data: Event data
        """
        # Use get_running_loop() instead of deprecated get_event_loop()
        try:
            loop = asyncio.get_running_loop()
            timestamp = loop.time()
        except RuntimeError:
            # Fallback if no running loop
            import time
            timestamp = time.time()
        
        event = {
            "type": event_type,
            "data": event_data,
            "timestamp": timestamp
        }
        
        # Add to history (deque automatically handles maxlen)
        self.event_history.append(event)
        
        # Get subscribers
        handlers = self.subscribers.get(event_type, [])
        
        if not handlers:
            logger.debug(f"No subscribers for event: {event_type}")
            return
        
        # Dispatch to all subscribers with retry logic
        tasks = []
        for handler in handlers:
            handler_name = getattr(handler, '__name__', str(handler))
            
            # Check if handler is async or sync
            is_async = asyncio.iscoroutinefunction(handler)
            
            # Retry logic for failed handlers
            success = False
            last_error = None
            
            for attempt in range(1, self.max_retries + 1):
                try:
                    if is_async:
                        # Async handler
                        await handler(event_data)
                    else:
                        # Sync handler - run in executor to avoid blocking
                        await asyncio.get_event_loop().run_in_executor(
                            None, handler, event_data
                        )
                    success = True
                    break
                except Exception as e:
                    last_error = e
                    if attempt < self.max_retries:
                        logger.warning(
                            f"Handler {handler_name} failed (attempt {attempt}/{self.max_retries}): {e}. Retrying..."
                        )
                        # Exponential backoff
                        await asyncio.sleep(0.1 * (2 ** (attempt - 1)))
                    else:
                        logger.error(
                            f"Handler {handler_name} failed after {self.max_retries} attempts: {e}"
                        )
            
            # If handler failed after all retries, add to dead letter queue
            if not success:
                # Use get_running_loop() instead of deprecated get_event_loop()
                try:
                    loop = asyncio.get_running_loop()
                    dlq_timestamp = loop.time()
                except RuntimeError:
                    import time
                    dlq_timestamp = time.time()
                
                dead_letter_event = {
                    "event": event,
                    "handler": handler_name,
                    "error": str(last_error),
                    "timestamp": dlq_timestamp
                }
                self.dead_letter_queue.append(dead_letter_event)
                logger.error(
                    f"Handler {handler_name} failed permanently. Added to dead letter queue."
                )
        
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
        # Convert deque to list for filtering
        events = list(self.event_history)
        
        if event_type:
            events = [e for e in events if e["type"] == event_type]
        
        return events[-limit:]
    
    def get_dead_letter_queue(self) -> List[Dict[str, Any]]:
        """
        Get dead letter queue (events that failed after all retries).
        
        Returns:
            List of failed events
        """
        return self.dead_letter_queue.copy()
    
    def clear_dead_letter_queue(self):
        """Clear dead letter queue."""
        count = len(self.dead_letter_queue)
        self.dead_letter_queue.clear()
        logger.info(f"Cleared {count} events from dead letter queue")
    
    def clear_history(self):
        """Clear event history."""
        self.event_history.clear()
        logger.info("Event history cleared")
