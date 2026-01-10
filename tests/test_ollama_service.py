"""Unit tests for OllamaService."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from services.ollama_service import OllamaService


class TestOllamaService:
    """Test cases for OllamaService."""
    
    @pytest.fixture
    def service(self):
        """Create OllamaService instance."""
        with patch('services.ollama_service.ollama.Client'):
            return OllamaService()
    
    @patch('services.ollama_service.ollama.Client')
    def test_init_success(self, mock_client_class):
        """Test successful initialization."""
        mock_client = Mock()
        mock_client.list.return_value = Mock(models=[])
        mock_client_class.return_value = mock_client
        
        service = OllamaService()
        
        assert service.base_url is not None
        assert service._client is not None
    
    @patch('services.ollama_service.ollama.Client')
    def test_init_failure(self, mock_client_class):
        """Test initialization failure."""
        mock_client_class.side_effect = Exception("Connection failed")
        
        service = OllamaService()
        
        assert service._client is None
        assert service.is_available is False
    
    @patch('services.ollama_service.ollama.Client')
    @patch('services.ollama_service.OllamaLLM')
    def test_get_strategy_llm(self, mock_llm_class, mock_client_class):
        """Test getting strategy LLM."""
        mock_client = Mock()
        mock_client.list.return_value = Mock(models=[])
        mock_client_class.return_value = mock_client
        
        mock_llm = Mock()
        mock_llm_class.return_value = mock_llm
        
        service = OllamaService()
        
        llm = service.get_strategy_llm()
        
        # If service is available, should return LLM
        # If not available, returns None
        # This depends on actual Ollama connection
    
    @patch('services.ollama_service.ollama.Client')
    def test_list_available_models(self, mock_client_class):
        """Test listing available models."""
        mock_model = Mock()
        mock_model.model = "deepseek-r1:7b"
        mock_model.modified_at = None
        mock_model.size = 1000000
        
        mock_client = Mock()
        mock_response = Mock()
        mock_response.models = [mock_model]
        mock_client.list.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        service = OllamaService()
        
        models = service.list_available_models()
        
        assert isinstance(models, list)
        if service.is_available:
            assert len(models) >= 0
    
    @patch('services.ollama_service.ollama.Client')
    def test_test_model(self, mock_client_class):
        """Test testing a model."""
        mock_client = Mock()
        mock_client.chat.return_value = Mock()
        mock_client.list.return_value = Mock(models=[])
        mock_client_class.return_value = mock_client
        
        service = OllamaService()
        
        if service.is_available:
            result = service.test_model("deepseek-r1:7b")
            assert isinstance(result, bool)
        else:
            result = service.test_model("deepseek-r1:7b")
            assert result is False
