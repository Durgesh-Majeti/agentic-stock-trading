"""Ollama local service with multi-model support."""
import ollama
from typing import Optional, Dict, Any
from langchain_ollama import OllamaLLM
from config.settings import settings
from config.ollama_config import OllamaModelConfig, ModelRole
from loguru import logger


class OllamaService:
    """Multi-model local Ollama service for different agent roles."""
    
    def __init__(self):
        self.base_url = OllamaModelConfig.get_base_url()
        
        # Initialize Ollama client for local server
        try:
            self._client = ollama.Client(host=self.base_url)
            logger.info(f"✅ Ollama client initialized, connecting to: {self.base_url}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Ollama client: {e}")
            logger.info("💡 Tip: Make sure Ollama is running locally (ollama serve)")
            self._client = None
        
        # Initialize LLM instances for each role
        self._strategy_llm: Optional[OllamaLLM] = None
        self._database_llm: Optional[OllamaLLM] = None
        self._chatbot_llm: Optional[OllamaLLM] = None
        self._guardian_llm: Optional[OllamaLLM] = None
        
        # Health check
        self._is_available = self._check_availability()
    
    def _check_availability(self) -> bool:
        """Check if local Ollama server is available."""
        if self._client is None:
            return False
            
        try:
            # Try to list models to check connection
            response = self._client.list()
            logger.info("✅ Local Ollama server connection successful")
            return True
        except ollama.ResponseError as e:
            logger.error(f"❌ Ollama server returned error: {e.status_code} - {e.error}")
            return False
        except ollama.RequestError as e:
            logger.error(f"❌ Connection error: {e}")
            logger.info("💡 Tip: Make sure Ollama is running: 'ollama serve'")
            return False
        except Exception as e:
            logger.error(f"❌ Ollama server unavailable: {e}")
            logger.info("💡 Tip: Start Ollama server with 'ollama serve'")
            return False
    
    @property
    def is_available(self) -> bool:
        """Check if Ollama service is available."""
        return self._is_available
    
    def get_strategy_llm(self, use_fallback: bool = False) -> Optional[OllamaLLM]:
        """Get LLM for strategy specialist agent.
        
        Args:
            use_fallback: Whether to use fallback model
            
        Returns:
            OllamaLLM instance or None if unavailable
        """
        if not self._is_available:
            return None
        
        if self._strategy_llm is None:
            model_name = OllamaModelConfig.get_model_for_role(
                ModelRole.STRATEGY,
                use_fallback
            )
            try:
                # For local Ollama, use base_url directly
                self._strategy_llm = OllamaLLM(
                    model=model_name,
                    base_url=self.base_url,
                    temperature=0.3,  # Lower temperature for consistent reasoning
                )
                logger.info(f"✅ Strategy LLM initialized: {model_name}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize strategy LLM: {e}")
                logger.info(f"💡 Tip: Make sure model '{model_name}' is pulled: 'ollama pull {model_name}'")
                return None
        
        return self._strategy_llm
    
    def get_database_llm(self, use_fallback: bool = False) -> Optional[OllamaLLM]:
        """Get LLM for database librarian agent.
        
        Args:
            use_fallback: Whether to use fallback model
            
        Returns:
            OllamaLLM instance or None if unavailable
        """
        if not self._is_available:
            return None
        
        if self._database_llm is None:
            model_name = OllamaModelConfig.get_model_for_role(
                ModelRole.DATABASE,
                use_fallback
            )
            try:
                # For local Ollama, use base_url directly
                self._database_llm = OllamaLLM(
                    model=model_name,
                    base_url=self.base_url,
                    temperature=0.1,  # Very low temperature for precise SQL generation
                )
                logger.info(f"✅ Database LLM initialized: {model_name}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize database LLM: {e}")
                logger.info(f"💡 Tip: Make sure model '{model_name}' is pulled: 'ollama pull {model_name}'")
                return None
        
        return self._database_llm
    
    def get_chatbot_llm(self, use_fallback: bool = False) -> Optional[OllamaLLM]:
        """Get LLM for telegram assistant agent.
        
        Args:
            use_fallback: Whether to use fallback model
            
        Returns:
            OllamaLLM instance or None if unavailable
        """
        if not self._is_available:
            return None
        
        if self._chatbot_llm is None:
            model_name = OllamaModelConfig.get_model_for_role(
                ModelRole.CHATBOT,
                use_fallback
            )
            try:
                # For local Ollama, use base_url directly
                self._chatbot_llm = OllamaLLM(
                    model=model_name,
                    base_url=self.base_url,
                    temperature=0.7,  # Higher temperature for natural conversation
                )
                logger.info(f"✅ Chatbot LLM initialized: {model_name}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize chatbot LLM: {e}")
                logger.info(f"💡 Tip: Make sure model '{model_name}' is pulled: 'ollama pull {model_name}'")
                return None
        
        return self._chatbot_llm
    
    def get_guardian_llm(self, use_fallback: bool = False) -> Optional[OllamaLLM]:
        """Get LLM for portfolio guardian agent.
        
        Args:
            use_fallback: Whether to use fallback model
            
        Returns:
            OllamaLLM instance or None if unavailable
        """
        if not self._is_available:
            return None
        
        if self._guardian_llm is None:
            model_name = OllamaModelConfig.get_model_for_role(
                ModelRole.GUARDIAN,
                use_fallback
            )
            try:
                # For local Ollama, use base_url directly
                self._guardian_llm = OllamaLLM(
                    model=model_name,
                    base_url=self.base_url,
                    temperature=0.2,  # Low temperature for consistent monitoring decisions
                )
                logger.info(f"✅ Guardian LLM initialized: {model_name}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize guardian LLM: {e}")
                logger.info(f"💡 Tip: Make sure model '{model_name}' is pulled: 'ollama pull {model_name}'")
                return None
        
        return self._guardian_llm
    
    def list_available_models(self) -> list[Dict[str, Any]]:
        """List available models from local Ollama server.
        
        Returns:
            List of available models (ollama library format)
        """
        if not self._client:
            return []
            
        try:
            response = self._client.list()
            # The ollama library returns a ListResponse object with a models attribute
            # Convert Model objects to dictionaries
            models_list = []
            if hasattr(response, 'models'):
                for model in response.models:
                    models_list.append({
                        'id': model.model,
                        'name': model.model,
                        'modified_at': model.modified_at.isoformat() if model.modified_at else None,
                        'size': model.size,
                    })
            return models_list
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []
    
    def test_model(self, model_name: str) -> bool:
        """Test if a specific model is available.
        
        Args:
            model_name: Name of the model to test
            
        Returns:
            True if model is available, False otherwise
        """
        if not self._client:
            return False
            
        try:
            # Try a simple chat request to test the model
            response = self._client.chat(
                model=model_name,
                messages=[{"role": "user", "content": "test"}],
            )
            return response is not None
        except ollama.ResponseError as e:
            if e.status_code == 404:
                logger.debug(f"Model {model_name} not found")
            else:
                logger.debug(f"Error testing model {model_name}: {e.error}")
            return False
        except Exception as e:
            logger.debug(f"Error testing model {model_name}: {e}")
            return False
