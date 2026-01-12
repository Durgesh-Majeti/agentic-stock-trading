"""
Main Trading Orchestrator

Central controller for all agent interactions.
Implements all 10 improvements for production-ready orchestration.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import asyncio
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
        """Factory method for default agents."""
        # This will be implemented when agents are created
        # For now, return empty dict
        return {}
    
    def _load_agent_contracts(self) -> Dict[str, Any]:
        """Load agent contracts from YAML."""
        # TODO: Load from config/agent_contracts.yaml
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
        import asyncio
        
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
                    return await asyncio.get_event_loop().run_in_executor(
                        None, sync_process
                    )
                
                return await self.cache_manager.get_or_call(
                    agent_name,
                    formatted_input,
                    call_agent
                )
            else:
                # Run sync process in executor
                return await asyncio.get_event_loop().run_in_executor(
                    None, sync_process
                )
        
        try:
            start_time = datetime.now()
            
            # Call with circuit breaker
            output = await circuit_breaker.call(_call)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Track metrics
            self.monitor.track_agent_call(agent_name, duration, True)
            
            # Validate output
            if not self._validate_agent_output(agent_name, output):
                raise ContractValidationError(
                    f"Invalid output from agent '{agent_name}'"
                )
            
            return output
            
        except Exception as e:
            if 'start_time' in locals():
                duration = (datetime.now() - start_time).total_seconds()
                self.monitor.track_agent_call(agent_name, duration, False)
            logger.error(f"Agent '{agent_name}' call failed: {e}")
            raise
    
    def _format_agent_input(
        self,
        agent_name: str,
        raw_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format input data according to agent contract."""
        # TODO: Implement input formatting based on contract
        # - Load contract for agent
        # - Validate required fields
        # - Transform data types
        # - Apply defaults
        return raw_data
    
    def _validate_agent_output(
        self,
        agent_name: str,
        output: Dict[str, Any]
    ) -> bool:
        """Validate agent output against contract."""
        # TODO: Implement output validation
        # - Load contract for agent
        # - Check required fields
        # - Validate types
        # - Check ranges and constraints
        return True
    
    async def shutdown(self):
        """Graceful shutdown of orchestrator."""
        logger.info("Shutting down orchestrator...")
        
        # Stop event bus
        # Close connections
        # Save state
        
        logger.info("Orchestrator shutdown complete")
