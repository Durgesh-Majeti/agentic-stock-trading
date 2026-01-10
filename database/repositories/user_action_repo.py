"""User action repository."""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from database.models import UserAction


class UserActionRepository:
    """Repository for user action operations."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def log_action(
        self,
        action_type: str,
        details: dict,
        user_id: Optional[str] = None
    ) -> UserAction:
        """Log a user action.
        
        Args:
            action_type: Type of action
            details: Action details as dictionary
            user_id: User ID (e.g., Telegram user ID)
            
        Returns:
            Created UserAction record
        """
        import json
        action = UserAction(
            action_type=action_type,
            details=json.dumps(details),
            user_id=user_id
        )
        self.session.add(action)
        self.session.commit()
        self.session.refresh(action)
        return action
    
    def get_recent_actions(self, limit: int = 100) -> List[UserAction]:
        """Get recent user actions."""
        return self.session.query(UserAction).order_by(
            desc(UserAction.timestamp)
        ).limit(limit).all()
