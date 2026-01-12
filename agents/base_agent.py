"""
Base Agent Framework

Provides foundation for all agents with orchestrator integration.
All agents must inherit from this class and implement the process() method.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json
from loguru import logger

from services.ollama_service import OllamaService
from database.repositories.analysis_repo import AnalysisRepository
from database.session import get_session
from config.constants import AgentName
from config.ollama_config import ModelRole


class BaseAgent(ABC):
    """
    Base class for all agents.
    
    Provides common functionality:
    - LLM initialization based on role
    - Decision logging to database
    - Error handling patterns
    - Input/output validation helpers
    
    All agents must:
    1. Inherit from BaseAgent
    2. Implement process(input_data: Dict) -> Dict method
    3. Follow input/output contracts defined in agent_contracts.yaml
    """
    
    def __init__(self, name: str, model_role: Optional[str] = None):
        """
        Initialize base agent.
        
        Args:
            name: Agent name (must match AgentName enum or be mappable)
            model_role: Model role for LLM ("strategy", "database", "chatbot", etc.)
                       If None, agent doesn't use LLM
        """
        self.name = name
        self.model_role = model_role
        self.ollama_service = OllamaService()
        self.llm = None
        
        # Initialize LLM if model_role is provided
        if model_role:
            self._initialize_llm()
        else:
            logger.debug(f"Agent {name} initialized without LLM (model_role=None)")
    
    def _initialize_llm(self):
        """
        Initialize LLM for this agent based on role.
        
        Different agents use different models optimized for their tasks:
        - Strategy agents need reasoning capabilities (DeepSeek R1 7B)
        - Database agents need code generation (Qwen2.5 Coder)
        - Chatbot agents need natural language understanding (Gemma2)
        """
        try:
            if self.model_role == "strategy":
                self.llm = self.ollama_service.get_strategy_llm()
            elif self.model_role == "database":
                self.llm = self.ollama_service.get_database_llm()
            elif self.model_role == "chatbot":
                self.llm = self.ollama_service.get_chatbot_llm()
            elif self.model_role == "news_sentiment":
                # News sentiment uses strategy model (DeepSeek R1 7B)
                self.llm = self.ollama_service.get_strategy_llm()
            elif self.model_role == "guardian":
                # Guardian uses strategy model for risk assessment
                self.llm = self.ollama_service.get_strategy_llm()
            else:
                logger.warning(f"Unknown model_role: {self.model_role}, no LLM initialized")
                self.llm = None
            
            if self.llm:
                logger.info(f"✅ LLM initialized for {self.name} (role: {self.model_role})")
            else:
                logger.warning(f"⚠️ LLM not available for {self.name}")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize LLM for {self.name}: {e}")
            self.llm = None
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input and return output.
        
        This is the main entry point for all agents. Each agent
        implements this method with its specific logic.
        
        Args:
            input_data: Input data dictionary (must match agent contract)
        
        Returns:
            Output data dictionary (must match agent contract)
        
        Raises:
            Should handle errors gracefully and return error dict
        """
        pass
    
    def log_decision(
        self,
        decision_type: str,
        reasoning: Optional[str] = None,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        confidence_score: Optional[float] = None,
        stock_id: Optional[int] = None
    ):
        """
        Log agent decision to database for audit trail.
        
        This method automatically logs all agent decisions, including:
        - What decision was made (decision_type)
        - Why it was made (reasoning)
        - Input data that led to the decision
        - Output data from the decision
        - Confidence score (if applicable)
        
        This is critical for debugging, compliance, and performance analysis.
        
        Args:
            decision_type: Type of decision (e.g., "SQL_QUERY", "TRADE_SIGNAL")
            reasoning: Reasoning/explanation for the decision
            input_data: Input data dictionary (will be JSON serialized)
            output_data: Output data dictionary (will be JSON serialized)
            confidence_score: Confidence score (0-100) if applicable
            stock_id: Stock ID if decision is stock-specific
        """
        try:
            # Convert agent name to AgentName enum
            agent_name = self._get_agent_name_enum()
            
            # Serialize input/output data to JSON strings
            input_data_str = json.dumps(input_data) if input_data else None
            output_data_str = json.dumps(output_data) if output_data else None
            
            # Get database session
            with get_session() as session:
                repo = AnalysisRepository(session)
                repo.save_agent_decision(
                    agent_name=agent_name,
                    decision_type=decision_type,
                    reasoning=reasoning,
                    confidence_score=confidence_score,
                    stock_id=stock_id,
                    input_data=input_data_str,
                    output_data=output_data_str
                )
                logger.debug(f"✅ Decision logged for {self.name}: {decision_type}")
                
        except Exception as e:
            # Don't fail agent execution if logging fails
            logger.error(f"❌ Failed to log decision for {self.name}: {e}")
    
    def _get_agent_name_enum(self) -> AgentName:
        """
        Convert agent name string to AgentName enum.
        
        Returns:
            AgentName enum value
        
        Raises:
            ValueError: If agent name doesn't match any enum value
        """
        # Map common agent names to enum values
        name_mapping = {
            "database_librarian": AgentName.DATABASE_LIBRARIAN,
            "librarian": AgentName.DATABASE_LIBRARIAN,
            "strategy_specialist": AgentName.STRATEGY_SPECIALIST,
            "strategy": AgentName.STRATEGY_SPECIALIST,
            "data_scraper": AgentName.DATA_SCRAPER,
            "scraper": AgentName.DATA_SCRAPER,
            "telegram_assistant": AgentName.TELEGRAM_ASSISTANT,
            "telegram": AgentName.TELEGRAM_ASSISTANT,
            "news_sentiment_analyst": AgentName.NEWS_SENTIMENT_ANALYST,
            "sentiment": AgentName.NEWS_SENTIMENT_ANALYST,
            "portfolio_guardian": AgentName.PORTFOLIO_GUARDIAN,
            "guardian": AgentName.PORTFOLIO_GUARDIAN,
        }
        
        # Try direct mapping first
        if self.name in name_mapping:
            return name_mapping[self.name]
        
        # Try case-insensitive match
        name_lower = self.name.lower()
        for key, value in name_mapping.items():
            if key.lower() == name_lower:
                return value
        
        # If not found, try to match enum value directly
        try:
            return AgentName(self.name)
        except ValueError:
            # Default to STRATEGY_SPECIALIST if can't determine
            logger.warning(
                f"Unknown agent name '{self.name}', defaulting to STRATEGY_SPECIALIST"
            )
            return AgentName.STRATEGY_SPECIALIST
    
    def safe_process(
        self,
        input_data: Dict[str, Any],
        log_decision: bool = True
    ) -> Dict[str, Any]:
        """
        Safe wrapper around process() with error handling.
        
        This method:
        - Wraps process() in try/except
        - Logs errors
        - Returns error dict on failure
        - Optionally logs decision
        
        Args:
            input_data: Input data dictionary
            log_decision: Whether to log the decision
        
        Returns:
            Output data dictionary or error dict
        """
        try:
            # Call agent's process method
            output_data = self.process(input_data)
            
            # Log decision if requested
            if log_decision:
                self.log_decision(
                    decision_type="PROCESS",
                    reasoning=f"Processed input for {self.name}",
                    input_data=input_data,
                    output_data=output_data
                )
            
            return output_data
            
        except Exception as e:
            logger.error(f"❌ Agent {self.name} process failed: {e}")
            
            # Return error dict (still matches contract structure)
            error_output = {
                "error": str(e),
                "status": "failed",
                "agent": self.name
            }
            
            # Log error decision
            if log_decision:
                try:
                    self.log_decision(
                        decision_type="ERROR",
                        reasoning=f"Error in {self.name}: {str(e)}",
                        input_data=input_data,
                        output_data=error_output
                    )
                except Exception as log_error:
                    logger.error(f"Failed to log error decision: {log_error}")
            
            return error_output
    
    def validate_input(
        self,
        input_data: Dict[str, Any],
        required_fields: list,
        optional_fields: Optional[list] = None
    ) -> bool:
        """
        Validate input data against required fields.
        
        Args:
            input_data: Input data dictionary
            required_fields: List of required field names
            optional_fields: List of optional field names
        
        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        for field in required_fields:
            if field not in input_data:
                logger.error(f"Missing required field: {field}")
                return False
        
        # Warn about unknown fields (but don't fail)
        if optional_fields:
            known_fields = set(required_fields + optional_fields)
            unknown_fields = set(input_data.keys()) - known_fields
            if unknown_fields:
                logger.warning(
                    f"Unknown fields in input: {unknown_fields}. "
                    f"Known fields: {known_fields}"
                )
        
        return True
    
    def validate_output(
        self,
        output_data: Dict[str, Any],
        required_fields: list
    ) -> bool:
        """
        Validate output data against required fields.
        
        Args:
            output_data: Output data dictionary
            required_fields: List of required field names
        
        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        for field in required_fields:
            if field not in output_data:
                logger.error(f"Missing required output field: {field}")
                return False
        
        return True
    
    def get_llm(self):
        """
        Get LLM instance for this agent.
        
        Returns:
            LLM instance or None if not available
        """
        return self.llm
    
    def is_llm_available(self) -> bool:
        """
        Check if LLM is available for this agent.
        
        Returns:
            True if LLM is available, False otherwise
        """
        return self.llm is not None and self.ollama_service.is_available
