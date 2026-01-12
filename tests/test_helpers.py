"""Unit tests for helper functions."""
import pytest
from datetime import datetime, date, timedelta
from pathlib import Path
import tempfile
import json
from utils.helpers import (
    format_currency,
    format_percentage,
    format_datetime,
    format_date,
    is_market_hours,
    calculate_pnl,
    calculate_pnl_percentage,
    calculate_stop_loss_price,
    calculate_target_price,
    get_nifty_500_symbols,
    ensure_directory,
    load_json_file,
    save_json_file,
    get_date_range,
    truncate_string,
    safe_divide,
    round_to_precision,
)


class TestFormatting:
    """Test formatting functions."""
    
    def test_format_currency(self):
        """Test currency formatting."""
        assert format_currency(1000.50) == "₹1,000.50"
        assert format_currency(0) == "₹0.00"
        assert format_currency(None) == "N/A"
    
    def test_format_percentage(self):
        """Test percentage formatting."""
        assert format_percentage(50.5) == "50.50%"
        assert format_percentage(0) == "0.00%"
        assert format_percentage(None) == "N/A"
    
    def test_format_datetime(self):
        """Test datetime formatting."""
        dt = datetime(2024, 1, 15, 10, 30, 0)
        assert format_datetime(dt) == "2024-01-15 10:30:00"
        assert format_datetime(None) == "N/A"
    
    def test_format_date(self):
        """Test date formatting."""
        d = date(2024, 1, 15)
        assert format_date(d) == "2024-01-15"
        assert format_date(None) == "N/A"


class TestMarketHours:
    """Test market hours function."""
    
    def test_market_hours_weekday(self):
        """Test market hours on weekday."""
        # 10:00 AM on Monday
        dt = datetime(2024, 1, 15, 10, 0, 0)  # Monday
        assert is_market_hours(dt) is True
    
    def test_market_hours_before_open(self):
        """Test before market open."""
        # 9:00 AM on Monday
        dt = datetime(2024, 1, 15, 9, 0, 0)
        assert is_market_hours(dt) is False
    
    def test_market_hours_after_close(self):
        """Test after market close."""
        # 4:00 PM on Monday
        dt = datetime(2024, 1, 15, 16, 0, 0)
        assert is_market_hours(dt) is False
    
    def test_market_hours_weekend(self):
        """Test weekend (Saturday)."""
        # Saturday
        dt = datetime(2024, 1, 13, 10, 0, 0)  # Saturday
        assert is_market_hours(dt) is False


class TestCalculations:
    """Test calculation functions."""
    
    def test_calculate_pnl(self):
        """Test P&L calculation."""
        assert calculate_pnl(100.0, 104.0, 10) == 40.0  # +4% * 10
        assert calculate_pnl(100.0, 98.0, 10) == -20.0  # -2% * 10
    
    def test_calculate_pnl_percentage(self):
        """Test P&L percentage."""
        assert calculate_pnl_percentage(100.0, 104.0) == 4.0
        assert calculate_pnl_percentage(100.0, 98.0) == -2.0
    
    def test_calculate_stop_loss_price(self):
        """Test stop loss price calculation."""
        assert calculate_stop_loss_price(100.0, 2.0) == 98.0  # 2% SL
    
    def test_calculate_target_price(self):
        """Test target price calculation."""
        assert calculate_target_price(100.0, 4.0) == 104.0  # 4% target


class TestFileOperations:
    """Test file operation functions."""
    
    def test_ensure_directory(self):
        """Test directory creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            new_dir = Path(tmpdir) / "test" / "nested"
            ensure_directory(new_dir)
            assert new_dir.exists() and new_dir.is_dir()
    
    def test_save_and_load_json(self):
        """Test JSON save and load."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.json"
            data = {"key": "value", "number": 123}
            
            save_json_file(data, file_path)
            assert file_path.exists()
            
            loaded = load_json_file(file_path)
            assert loaded == data


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_get_date_range(self):
        """Test date range generation."""
        start = date(2024, 1, 1)
        end = date(2024, 1, 3)
        dates = get_date_range(start, end)
        
        assert len(dates) == 3
        assert dates[0] == start
        assert dates[-1] == end
    
    def test_truncate_string(self):
        """Test string truncation."""
        long_string = "A" * 100
        truncated = truncate_string(long_string, max_length=50)
        
        assert len(truncated) == 50
        assert truncated.endswith("...")
    
    def test_safe_divide(self):
        """Test safe division."""
        assert safe_divide(10, 2) == 5.0
        assert safe_divide(10, 0) == 0.0
        assert safe_divide(10, 0, default=999) == 999
    
    def test_round_to_precision(self):
        """Test rounding."""
        assert round_to_precision(10.12345, 2) == 10.12
        assert round_to_precision(10.12345, 0) == 10.0
    
    def test_get_nifty_500_symbols(self):
        """Test getting Nifty 500 symbols."""
        symbols = get_nifty_500_symbols()
        assert isinstance(symbols, list)
        assert len(symbols) > 0
        assert "RELIANCE" in symbols
        assert "TCS" in symbols
