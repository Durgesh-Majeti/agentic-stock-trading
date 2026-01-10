"""Unit tests for validators."""
import pytest
from datetime import date, datetime
from utils.validators import (
    validate_price,
    validate_symbol,
    validate_quantity,
    validate_confidence_score,
    validate_percentage,
    validate_date,
    validate_datetime,
    validate_email,
    validate_api_key,
    validate_stop_loss_target,
)


class TestPriceValidation:
    """Test price validation."""
    
    def test_valid_price(self):
        """Test valid price."""
        assert validate_price(100.0) is True
        assert validate_price(0.01) is True
    
    def test_invalid_price_zero(self):
        """Test zero price."""
        assert validate_price(0.0) is False
        assert validate_price(-10.0) is False
    
    def test_invalid_price_type(self):
        """Test invalid price type."""
        assert validate_price("100") is False
        assert validate_price(None) is False
    
    def test_price_deviation_valid(self):
        """Test valid price deviation."""
        assert validate_price(105.0, previous_price=100.0, max_deviation=0.05) is True
        assert validate_price(95.0, previous_price=100.0, max_deviation=0.05) is True
    
    def test_price_deviation_invalid(self):
        """Test invalid price deviation."""
        assert validate_price(110.0, previous_price=100.0, max_deviation=0.05) is False
        assert validate_price(90.0, previous_price=100.0, max_deviation=0.05) is False


class TestSymbolValidation:
    """Test symbol validation."""
    
    def test_valid_symbols(self):
        """Test valid symbols."""
        assert validate_symbol("RELIANCE") is True
        assert validate_symbol("TCS") is True
        assert validate_symbol("INFY-EQ") is True
    
    def test_invalid_symbols(self):
        """Test invalid symbols."""
        assert validate_symbol("") is False
        assert validate_symbol("A") is False  # Too short
        assert validate_symbol("A" * 21) is False  # Too long
        assert validate_symbol("TEST@SYMBOL") is False  # Invalid chars
        assert validate_symbol(None) is False


class TestQuantityValidation:
    """Test quantity validation."""
    
    def test_valid_quantity(self):
        """Test valid quantity."""
        assert validate_quantity(1) is True
        assert validate_quantity(100) is True
    
    def test_invalid_quantity(self):
        """Test invalid quantity."""
        assert validate_quantity(0) is False
        assert validate_quantity(-1) is False
        assert validate_quantity("100") is False


class TestConfidenceScoreValidation:
    """Test confidence score validation."""
    
    def test_valid_scores(self):
        """Test valid confidence scores."""
        assert validate_confidence_score(0) is True
        assert validate_confidence_score(50) is True
        assert validate_confidence_score(100) is True
    
    def test_invalid_scores(self):
        """Test invalid confidence scores."""
        assert validate_confidence_score(-1) is False
        assert validate_confidence_score(101) is False
        assert validate_confidence_score("50") is False


class TestPercentageValidation:
    """Test percentage validation."""
    
    def test_valid_percentage(self):
        """Test valid percentage."""
        assert validate_percentage(0.0) is True
        assert validate_percentage(50.0) is True
        assert validate_percentage(100.0) is True
    
    def test_invalid_percentage(self):
        """Test invalid percentage."""
        assert validate_percentage(-1.0) is False
        assert validate_percentage(101.0) is False


class TestDateValidation:
    """Test date validation."""
    
    def test_valid_date(self):
        """Test valid date."""
        assert validate_date(date.today()) is True
        assert validate_date(date(2020, 1, 1)) is True
    
    def test_invalid_date(self):
        """Test invalid date."""
        assert validate_date(date.today().replace(year=date.today().year + 1)) is False
        assert validate_date("2020-01-01") is False


class TestDatetimeValidation:
    """Test datetime validation."""
    
    def test_valid_datetime(self):
        """Test valid datetime."""
        assert validate_datetime(datetime.now()) is True
    
    def test_invalid_datetime(self):
        """Test invalid datetime."""
        future = datetime.now().replace(year=datetime.now().year + 1)
        assert validate_datetime(future) is False
        assert validate_datetime("2020-01-01") is False


class TestEmailValidation:
    """Test email validation."""
    
    def test_valid_emails(self):
        """Test valid emails."""
        assert validate_email("test@example.com") is True
        assert validate_email("user.name@domain.co.uk") is True
    
    def test_invalid_emails(self):
        """Test invalid emails."""
        assert validate_email("invalid") is False
        assert validate_email("@domain.com") is False
        assert validate_email("user@") is False


class TestAPIKeyValidation:
    """Test API key validation."""
    
    def test_valid_api_keys(self):
        """Test valid API keys."""
        assert validate_api_key("1234567890abcdef") is True
        assert validate_api_key("key-with-dashes-123") is True
    
    def test_invalid_api_keys(self):
        """Test invalid API keys."""
        assert validate_api_key("short") is False
        assert validate_api_key("") is False


class TestStopLossTargetValidation:
    """Test stop loss and target validation."""
    
    def test_valid_stop_loss_target(self):
        """Test valid stop loss and target."""
        assert validate_stop_loss_target(100.0, 98.0, 104.0) is True  # 2% SL, 4% Target
    
    def test_invalid_stop_loss_above_entry(self):
        """Test stop loss above entry."""
        assert validate_stop_loss_target(100.0, 101.0, 104.0) is False
    
    def test_invalid_target_below_entry(self):
        """Test target below entry."""
        assert validate_stop_loss_target(100.0, 98.0, 99.0) is False
    
    def test_invalid_risk_reward_ratio(self):
        """Test invalid risk:reward ratio."""
        assert validate_stop_loss_target(100.0, 99.0, 101.0) is False  # 1:1 ratio
