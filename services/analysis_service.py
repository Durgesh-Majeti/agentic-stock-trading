"""Analysis service for aggregating agent analysis."""
from typing import List, Dict, Any
from database.repositories.analysis_repo import AnalysisRepository
from database.repositories.market_data_repo import MarketDataRepository
from config.constants import SignalType


class AnalysisService:
    """Service for aggregating and managing analysis results."""
    
    def __init__(
        self,
        analysis_repo: AnalysisRepository,
        market_data_repo: MarketDataRepository
    ):
        self.analysis_repo = analysis_repo
        self.market_data_repo = market_data_repo
    
    def get_stock_analysis(self, stock_id: int) -> Dict[str, Any]:
        """Get comprehensive analysis for a stock.
        
        Args:
            stock_id: Stock ID
            
        Returns:
            Dictionary with analysis results
        """
        # Get latest signals
        signals = self.analysis_repo.get_recent_signals(
            stock_id=stock_id,
            limit=5
        )
        
        # Get latest agent decisions
        decisions = self.analysis_repo.get_recent_decisions(
            stock_id=stock_id,
            limit=10
        )
        
        # Get latest market data
        market_data = self.market_data_repo.get_latest_daily_data(stock_id)
        
        return {
            "signals": [self._signal_to_dict(s) for s in signals],
            "decisions": [self._decision_to_dict(d) for d in decisions],
            "market_data": self._market_data_to_dict(market_data) if market_data else None
        }
    
    def _signal_to_dict(self, signal) -> Dict[str, Any]:
        """Convert signal to dictionary."""
        return {
            "id": signal.id,
            "signal_type": signal.signal_type.value,
            "confidence_score": signal.confidence_score,
            "entry_price": signal.entry_price,
            "stop_loss": signal.stop_loss,
            "target_price": signal.target_price,
            "created_at": signal.created_at.isoformat()
        }
    
    def _decision_to_dict(self, decision) -> Dict[str, Any]:
        """Convert decision to dictionary."""
        return {
            "id": decision.id,
            "agent_name": decision.agent_name.value,
            "decision_type": decision.decision_type,
            "confidence_score": decision.confidence_score,
            "created_at": decision.created_at.isoformat()
        }
    
    def _market_data_to_dict(self, market_data) -> Dict[str, Any]:
        """Convert market data to dictionary."""
        return {
            "date": market_data.date.isoformat(),
            "close": market_data.close,
            "rsi": market_data.rsi,
            "macd": market_data.macd,
            "bollinger_upper": market_data.bollinger_upper,
            "bollinger_lower": market_data.bollinger_lower,
        }
