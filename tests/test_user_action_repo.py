"""Unit tests for UserActionRepository."""
import pytest
from database.repositories.user_action_repo import UserActionRepository
from database.models import UserAction


class TestUserActionRepository:
    """Test cases for UserActionRepository."""
    
    @pytest.fixture
    def repo(self, temp_db):
        """Create UserActionRepository instance."""
        return UserActionRepository(temp_db)
    
    def test_log_action(self, repo):
        """Test logging a user action."""
        action = repo.log_action(
            action_type="ORDER_APPROVED",
            details={"order_id": 123, "stock": "TCS", "quantity": 10},
            user_id="telegram_user_123"
        )
        
        assert action.id is not None
        assert action.action_type == "ORDER_APPROVED"
        assert action.user_id == "telegram_user_123"
        assert "order_id" in action.details
    
    def test_log_action_no_user_id(self, repo):
        """Test logging action without user ID."""
        action = repo.log_action(
            action_type="SYSTEM_EVENT",
            details={"event": "market_open"}
        )
        
        assert action.id is not None
        assert action.user_id is None
    
    def test_get_recent_actions(self, repo):
        """Test getting recent actions."""
        repo.log_action("ACTION_1", {"test": "data1"})
        repo.log_action("ACTION_2", {"test": "data2"})
        
        recent = repo.get_recent_actions(limit=10)
        assert len(recent) >= 2
    
    def test_get_recent_actions_limit(self, repo):
        """Test getting recent actions with limit."""
        # Create more actions than limit
        for i in range(5):
            repo.log_action(f"ACTION_{i}", {"index": i})
        
        recent = repo.get_recent_actions(limit=3)
        assert len(recent) == 3
