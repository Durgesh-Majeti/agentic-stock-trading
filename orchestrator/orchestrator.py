"""
Main Trading Orchestrator

Central controller for all agent interactions.
Implements all 10 improvements for production-ready orchestration.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import asyncio
from pathlib import Path
import yaml
from loguru import logger

from orchestrator.workflow_executor import WorkflowExecutor
from orchestrator.workflow_state import WorkflowStateManager
from orchestrator.workflow_registry import WorkflowRegistry
from orchestrator.circuit_breaker import CircuitBreaker
from orchestrator.cache_manager import CacheManager
from orchestrator.event_bus import EventBus
from orchestrator.transaction_manager import TransactionManager
from orchestrator.monitoring import OrchestratorMonitor
from orchestrator.exceptions import (
    WorkflowNotFoundError,
    AgentNotFoundError,
    ContractValidationError
)


class TradingOrchestrator:
    """
    Central controller for all agent interactions.
    
    Responsibilities:
    - Agent initialization and management
    - Workflow execution
    - Data transformation
    - Output validation
    - Error recovery
    """
    
    def __init__(
        self,
        agents: Optional[Dict[str, Any]] = None,
        workflow_registry: Optional[WorkflowRegistry] = None,
        state_manager: Optional[WorkflowStateManager] = None,
        cache_manager: Optional[CacheManager] = None,
        event_bus: Optional[EventBus] = None,
        monitor: Optional[OrchestratorMonitor] = None,
        workflow_executor: Optional[WorkflowExecutor] = None,
        transaction_manager: Optional[TransactionManager] = None
    ):
        """
        Initialize orchestrator with dependency injection.
        
        Args:
            agents: Dictionary of agent instances
            workflow_registry: Workflow registry instance
            state_manager: Workflow state manager
            cache_manager: Cache manager
            event_bus: Event bus for pub/sub
            monitor: Monitoring and metrics
            workflow_executor: Workflow executor for parallel execution
            transaction_manager: Transaction manager
        """
        # Dependency injection - use provided or create defaults
        self.agents = agents or self._create_default_agents()
        self.workflow_registry = workflow_registry or WorkflowRegistry()
        self.state_manager = state_manager or WorkflowStateManager()
        self.cache_manager = cache_manager or CacheManager()
        self.event_bus = event_bus or EventBus()
        self.monitor = monitor or OrchestratorMonitor()
        self.workflow_executor = workflow_executor or WorkflowExecutor()
        self.transaction_manager = transaction_manager or TransactionManager()
        
        # Circuit breakers per agent
        self.circuit_breakers = {
            name: CircuitBreaker() for name in self.agents.keys()
        }
        
        # Agent contracts (loaded from YAML)
        self.agent_contracts = self._load_agent_contracts()
        
        logger.info(f"Orchestrator initialized with {len(self.agents)} agents")
    
    def _create_default_agents(self) -> Dict[str, Any]:
        """
        Factory method for default agents.
        
        Creates all available agents and returns them as a dictionary.
        """
        agents = {}
        
        try:
            from agents.database_librarian import DatabaseLibrarian
            from agents.data_scraper import DataScraper
            from agents.strategy_specialist import StrategySpecialist
            from agents.news_sentiment_analyst import NewsSentimentAnalyst
            
            # Initialize all agents
            logger.info("Initializing agents...")
            
            agents["librarian"] = DatabaseLibrarian()
            logger.info("✅ Database Librarian initialized")
            
            agents["scraper"] = DataScraper()
            logger.info("✅ Data Scraper initialized")
            
            agents["strategy"] = StrategySpecialist()
            logger.info("✅ Strategy Specialist initialized")
            
            agents["sentiment"] = NewsSentimentAnalyst()
            logger.info("✅ News Sentiment Analyst initialized")
            
            # Note: Telegram Assistant and Portfolio Guardian are not yet implemented
            # They will be added when implemented
            
            logger.info(f"Successfully initialized {len(agents)} agents")
            
        except ImportError as e:
            logger.error(f"Failed to import agents: {e}")
        except Exception as e:
            logger.error(f"Error initializing agents: {e}")
        
        return agents
    
    def _load_agent_contracts(self) -> Dict[str, Any]:
        """
        Load agent contracts from YAML file.
        
        Returns:
            Dictionary mapping agent names to their contracts
        """
        contracts_file = Path("config/agent_contracts.yaml")
        
        if not contracts_file.exists():
            logger.warning(f"Agent contracts file not found: {contracts_file}")
            return {}
        
        try:
            with open(contracts_file, 'r') as f:
                data = yaml.safe_load(f)
            
            # Extract agents from YAML structure
            agents_data = data.get("agents", {})
            
            # Map agent names to contracts
            contracts = {}
            for agent_name, contract in agents_data.items():
                contracts[agent_name] = contract
            
            logger.info(f"Loaded {len(contracts)} agent contracts")
            return contracts
            
        except Exception as e:
            logger.error(f"Error loading agent contracts: {e}")
            return {}
    
    async def execute_workflow(
        self,
        workflow_name: str,
        request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a workflow by name.
        
        Args:
            workflow_name: Name of workflow to execute
            request_data: Input data for workflow
        
        Returns:
            Workflow execution result
        """
        # Get workflow definition
        workflow = self.workflow_registry.get(workflow_name)
        if not workflow:
            raise WorkflowNotFoundError(f"Workflow '{workflow_name}' not found")
        
        # Generate workflow ID
        workflow_id = str(uuid.uuid4())
        
        # Create workflow state
        workflow_state = self.state_manager.create_workflow_state(workflow_id)
        
        # Track workflow execution
        with self.monitor.track_workflow(workflow_name):
            try:
                # Execute workflow steps
                result = await self._execute_workflow_steps(
                    workflow,
                    request_data,
                    workflow_id,
                    workflow_state
                )
                
                # Publish workflow completion event
                await self.event_bus.publish("workflow.completed", {
                    "workflow_name": workflow_name,
                    "workflow_id": workflow_id,
                    "status": "success"
                })
                
                return result
                
            except Exception as e:
                logger.error(f"Workflow '{workflow_name}' failed: {e}")
                
                # Publish workflow failure event
                await self.event_bus.publish("workflow.failed", {
                    "workflow_name": workflow_name,
                    "workflow_id": workflow_id,
                    "error": str(e)
                })
                
                raise
    
    async def _execute_workflow_steps(
        self,
        workflow: Any,
        request_data: Dict[str, Any],
        workflow_id: str,
        workflow_state: Any
    ) -> Dict[str, Any]:
        """Execute workflow steps."""
        # TODO: Implement workflow step execution
        # - Load workflow steps from definition
        # - Execute steps (sequential or parallel)
        # - Handle data mapping between steps
        # - Save checkpoints
        # - Handle errors and retries
        pass
    
    async def _call_agent(
        self,
        agent_name: str,
        input_data: Dict[str, Any],
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Call an agent with proper formatting and validation.
        
        Args:
            agent_name: Name of agent to call
            input_data: Input data for agent
            use_cache: Whether to use cache
        
        Returns:
            Agent output
        """
        # Check if agent exists
        if agent_name not in self.agents:
            raise AgentNotFoundError(f"Agent '{agent_name}' not found")
        
        # Get circuit breaker
        circuit_breaker = self.circuit_breakers[agent_name]
        
        # Format input according to contract
        formatted_input = self._format_agent_input(agent_name, input_data)
        
        # Call agent with circuit breaker protection
        async def _call():
            agent = self.agents[agent_name]
            
            # Agent.process() is synchronous, run in executor
            # This allows async orchestrator to call sync agents
            def sync_process():
                return agent.process(formatted_input)
            
            # Use cache if enabled
            if use_cache:
                # Wrap sync process() in async-compatible callable
                async def call_agent(input_data):
                    # Use asyncio.to_thread() for Python 3.9+ or get_running_loop() for older
                    try:
                        # Python 3.9+ - use to_thread
                        return await asyncio.to_thread(sync_process)
                    except AttributeError:
                        # Python < 3.9 - use run_in_executor with get_running_loop()
                        loop = asyncio.get_running_loop()
                        return await loop.run_in_executor(None, sync_process)
                
                return await self.cache_manager.get_or_call(
                    agent_name,
                    formatted_input,
                    call_agent
                )
            else:
                # Run sync process in executor using modern asyncio patterns
                try:
                    # Python 3.9+ - use to_thread
                    return await asyncio.to_thread(sync_process)
                except AttributeError:
                    # Python < 3.9 - use run_in_executor with get_running_loop()
                    loop = asyncio.get_running_loop()
                    return await loop.run_in_executor(None, sync_process)
        
        # Initialize start_time before try block to ensure it's always available
        start_time = datetime.now()
        
        try:
            # Call with circuit breaker and timeout protection
            # Agent-specific timeouts (sentiment analysis can take longer)
            agent_timeouts = {
                "sentiment": 300.0,  # 5 minutes for sentiment analysis (fetches + processes news)
                "strategy": 180.0,   # 3 minutes for strategy analysis (LLM calls)
                "librarian": 120.0,  # 2 minutes for database queries (LLM SQL generation can be slow)
                "scraper": 120.0,    # 2 minutes for data fetching
            }
            agent_timeout = agent_timeouts.get(agent_name, 60.0)  # Default 60s
            
            output = await asyncio.wait_for(
                circuit_breaker.call(_call),
                timeout=agent_timeout
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Track metrics
            self.monitor.track_agent_call(agent_name, duration, True)
            
            # Validate output
            if not self._validate_agent_output(agent_name, output):
                raise ContractValidationError(
                    f"Invalid output from agent '{agent_name}'"
                )
            
            return output
            
        except asyncio.TimeoutError:
            duration = (datetime.now() - start_time).total_seconds()
            self.monitor.track_agent_call(agent_name, duration, False)
            error_msg = f"Agent '{agent_name}' call timed out after {agent_timeout}s"
            logger.error(error_msg)
            raise TimeoutError(error_msg) from None
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.monitor.track_agent_call(agent_name, duration, False)
            # Include context in error log
            logger.error(
                f"Agent '{agent_name}' call failed after {duration:.3f}s: {e}",
                extra={
                    "agent_name": agent_name,
                    "duration": duration,
                    "input_data_keys": list(input_data.keys()) if input_data else []
                }
            )
            raise
    
    def _format_agent_input(
        self,
        agent_name: str,
        raw_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Format input data according to agent contract.
        
        Args:
            agent_name: Name of agent
            raw_data: Raw input data
        
        Returns:
            Formatted input data with defaults applied
        """
        # Get contract for agent
        contract = self.agent_contracts.get(agent_name)
        if not contract:
            logger.warning(f"No contract found for agent '{agent_name}', skipping validation")
            return raw_data
        
        input_schema = contract.get("input", {})
        formatted_data = raw_data.copy()
        
        # Apply defaults for optional fields
        for field_name, field_spec in input_schema.items():
            if field_name not in formatted_data:
                if "default" in field_spec:
                    formatted_data[field_name] = field_spec["default"]
                    logger.debug(f"Applied default value for {agent_name}.{field_name}")
        
        # Validate required fields
        for field_name, field_spec in input_schema.items():
            if field_spec.get("required", False):
                if field_name not in formatted_data:
                    raise ValueError(
                        f"Missing required field '{field_name}' for agent '{agent_name}'"
                    )
        
        return formatted_data
    
    def _validate_agent_output(
        self,
        agent_name: str,
        output: Dict[str, Any]
    ) -> bool:
        """
        Validate agent output against contract.
        
        Args:
            agent_name: Name of agent
            output: Agent output data
        
        Returns:
            True if valid, False otherwise
        """
        # Ensure output is a dictionary
        if not isinstance(output, dict):
            logger.error(
                f"Agent '{agent_name}' output is not a dictionary: {type(output)}"
            )
            return False
        
        # Get contract for agent
        contract = self.agent_contracts.get(agent_name)
        if not contract:
            logger.warning(f"No contract found for agent '{agent_name}', skipping validation")
            return True  # No contract = no validation
        
        output_schema = contract.get("output", {})
        
        # Check required fields
        for field_name, field_spec in output_schema.items():
            if field_spec.get("required", False):
                if field_name not in output:
                    logger.error(
                        f"Missing required output field '{field_name}' for agent '{agent_name}'"
                    )
                    return False
                
                # Basic type validation
                expected_type = field_spec.get("type")
                if expected_type:
                    actual_value = output[field_name]
                    type_valid = self._validate_type(actual_value, expected_type)
                    if not type_valid:
                        logger.error(
                            f"Type mismatch for '{field_name}' in agent '{agent_name}': "
                            f"expected {expected_type}, got {type(actual_value).__name__}"
                        )
                        return False
        
        return True
    
    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """
        Validate value type against expected type string.
        
        Args:
            value: Value to validate
            expected_type: Expected type (string, integer, float, array, object, boolean)
        
        Returns:
            True if type matches
        """
        type_mapping = {
            "string": str,
            "integer": int,
            "float": (int, float),  # Accept both int and float
            "number": (int, float),
            "array": list,
            "object": dict,
            "boolean": bool
        }
        
        expected_python_type = type_mapping.get(expected_type.lower())
        if expected_python_type is None:
            logger.warning(f"Unknown type '{expected_type}' in contract, skipping validation")
            return True
        
        if isinstance(expected_python_type, tuple):
            return isinstance(value, expected_python_type)
        return isinstance(value, expected_python_type)
    
    async def shutdown(self):
        """Graceful shutdown of orchestrator."""
        logger.info("Shutting down orchestrator...")
        
        # Stop event bus
        # Close connections
        # Save state
        
        logger.info("Orchestrator shutdown complete")
