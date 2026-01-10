"""Analysis repository for agent decisions and signals."""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
from database.models import AgentDecision, ScreeningSignal, Stock
from config.constants import AgentName, SignalType


class AnalysisRepository:
    """Repository for analysis and agent decision operations."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def save_agent_decision(
        self,
        agent_name: AgentName,
        decision_type: str,
        reasoning: Optional[str],
        confidence_score: Optional[float],
        stock_id: Optional[int] = None,
        input_data: Optional[str] = None,
        output_data: Optional[str] = None
    ) -> AgentDecision:
        """Save agent decision for audit trail."""
        decision = AgentDecision(
            agent_name=agent_name,
            stock_id=stock_id,
            decision_type=decision_type,
            reasoning=reasoning,
            confidence_score=confidence_score,
            input_data=input_data,
            output_data=output_data
        )
        self.session.add(decision)
        self.session.commit()
        self.session.refresh(decision)
        return decision
    
    def get_recent_decisions(
        self,
        agent_name: Optional[AgentName] = None,
        limit: int = 50
    ) -> List[AgentDecision]:
        """Get recent agent decisions."""
        query = self.session.query(AgentDecision)
        if agent_name:
            query = query.filter(AgentDecision.agent_name == agent_name)
        return query.order_by(desc(AgentDecision.created_at)).limit(limit).all()
    
    def create_screening_signal(
        self,
        stock_id: int,
        signal_type: SignalType,
        confidence_score: float,
        entry_price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        target_price: Optional[float] = None
    ) -> ScreeningSignal:
        """Create a screening signal."""
        signal = ScreeningSignal(
            stock_id=stock_id,
            signal_type=signal_type,
            confidence_score=confidence_score,
            entry_price=entry_price,
            stop_loss=stop_loss,
            target_price=target_price
        )
        self.session.add(signal)
        self.session.commit()
        self.session.refresh(signal)
        return signal
    
    def get_recent_signals(
        self,
        signal_type: Optional[SignalType] = None,
        min_confidence: float = 0.0,
        limit: int = 50
    ) -> List[ScreeningSignal]:
        """Get recent screening signals."""
        query = self.session.query(ScreeningSignal).filter(
            ScreeningSignal.confidence_score >= min_confidence
        )
        if signal_type:
            query = query.filter(ScreeningSignal.signal_type == signal_type)
        return query.order_by(desc(ScreeningSignal.created_at)).limit(limit).all()
