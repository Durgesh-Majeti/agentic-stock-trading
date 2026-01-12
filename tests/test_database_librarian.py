"""Unit tests for Database Librarian agent."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from agents.database_librarian import DatabaseLibrarian
from database.session import engine


class TestDatabaseLibrarian:
    """Test cases for Database Librarian agent."""
    
    @pytest.fixture
    def mock_ollama_service(self):
        """Create mock OllamaService."""
        mock_service = Mock()
        mock_service.is_available = True
        mock_service.get_database_llm = Mock(return_value=Mock())
        return mock_service
    
    @pytest.fixture
    def librarian(self, mock_ollama_service):
        """Create Database Librarian instance."""
        with patch('agents.base_agent.OllamaService', return_value=mock_ollama_service):
            return DatabaseLibrarian()
    
    def test_init(self, librarian):
        """Test initialization."""
        assert librarian.name == "database_librarian"
        assert librarian.model_role == "database"
        assert librarian.schema is not None
        assert len(librarian._forbidden_keywords) > 0
    
    def test_load_schema(self, librarian):
        """Test schema loading."""
        schema = librarian._load_schema()
        assert isinstance(schema, str)
        assert len(schema) > 0
        # Should contain table names
        assert "stocks" in schema.lower() or "Table:" in schema
    
    def test_validate_query_safety_safe(self, librarian):
        """Test query safety validation for safe queries."""
        safe_queries = [
            "SELECT * FROM stocks",
            "SELECT id, symbol FROM stocks WHERE is_active = 1",
            "SELECT s.symbol, m.close FROM stocks s JOIN market_data_daily m ON s.id = m.stock_id"
        ]
        
        for sql in safe_queries:
            assert librarian._validate_query_safety(sql) is True
    
    def test_validate_query_safety_unsafe(self, librarian):
        """Test query safety validation for unsafe queries."""
        unsafe_queries = [
            "DROP TABLE stocks",
            "DELETE FROM stocks",
            "TRUNCATE TABLE market_data_daily",
            "UPDATE stocks SET symbol = 'TEST'",
            "INSERT INTO stocks VALUES (1, 'TEST')",
            "ALTER TABLE stocks ADD COLUMN test INT"
        ]
        
        for sql in unsafe_queries:
            assert librarian._validate_query_safety(sql) is False
    
    def test_validate_query_safety_not_select(self, librarian):
        """Test that non-SELECT queries are rejected."""
        assert librarian._validate_query_safety("UPDATE stocks SET name = 'Test'") is False
        assert librarian._validate_query_safety("CREATE TABLE test (id INT)") is False
    
    @patch('agents.database_librarian.DatabaseLibrarian.is_llm_available')
    def test_translate_to_sql_success(self, mock_available, librarian):
        """Test successful SQL translation."""
        mock_available.return_value = True
        
        # Mock LLM response
        mock_llm = Mock()
        mock_llm.invoke = Mock(return_value="SELECT * FROM stocks LIMIT 15")
        librarian.llm = mock_llm
        
        sql = librarian._translate_to_sql("Show me all stocks")
        
        assert sql == "SELECT * FROM stocks LIMIT 15"
        mock_llm.invoke.assert_called_once()
    
    @patch('agents.database_librarian.DatabaseLibrarian.is_llm_available')
    def test_translate_to_sql_cleans_markdown(self, mock_available, librarian):
        """Test that markdown is cleaned from LLM response."""
        mock_available.return_value = True
        
        mock_llm = Mock()
        # Mock returns SQL with markdown and LIMIT (as LLM would generate)
        mock_llm.invoke = Mock(return_value="```sql\nSELECT * FROM stocks LIMIT 15\n```")
        librarian.llm = mock_llm
        
        sql = librarian._translate_to_sql("Show me all stocks")
        
        assert "```" not in sql
        assert "```sql" not in sql
        # After cleaning, should have the SQL without markdown
        # The SQL should be normalized (single spaces, no newlines)
        assert sql == "SELECT * FROM stocks LIMIT 15"
    
    @patch('agents.database_librarian.DatabaseLibrarian.is_llm_available')
    def test_translate_to_sql_unsafe_rejected(self, mock_available, librarian):
        """Test that unsafe SQL is rejected."""
        mock_available.return_value = True
        
        mock_llm = Mock()
        mock_llm.invoke = Mock(return_value="DROP TABLE stocks")
        librarian.llm = mock_llm
        
        sql = librarian._translate_to_sql("Delete all stocks")
        
        assert sql == ""  # Should return empty string for unsafe query
    
    @patch('agents.database_librarian.DatabaseLibrarian.is_llm_available')
    def test_translate_to_sql_no_llm(self, mock_available, librarian):
        """Test translation when LLM is not available."""
        mock_available.return_value = False
        
        sql = librarian._translate_to_sql("Show me all stocks")
        
        assert sql == ""
    
    @patch('agents.database_librarian.engine')
    def test_execute_query_success(self, mock_engine, librarian):
        """Test successful query execution."""
        # Mock connection and result
        mock_connection = Mock()
        mock_result = Mock()
        mock_result.keys.return_value = ["id", "symbol", "name"]
        mock_result.fetchall.return_value = [
            (1, "NSE|TCS-EQ", "TCS"),
            (2, "NSE|INFY-EQ", "Infosys")
        ]
        
        mock_connection.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_engine.connect.return_value.__exit__.return_value = None
        
        results, exec_time = librarian._execute_query("SELECT * FROM stocks")
        
        assert len(results) == 2
        assert results[0]["id"] == 1
        assert results[0]["symbol"] == "NSE|TCS-EQ"
        assert results[1]["symbol"] == "NSE|INFY-EQ"
        assert exec_time >= 0
    
    @patch('agents.database_librarian.engine')
    def test_execute_query_error(self, mock_engine, librarian):
        """Test query execution error handling."""
        mock_engine.connect.return_value.__enter__.side_effect = Exception("DB Error")
        mock_engine.connect.return_value.__exit__.return_value = None
        
        results, exec_time = librarian._execute_query("SELECT * FROM invalid_table")
        
        assert len(results) == 0
        assert exec_time >= 0
    
    def test_execute_query_empty(self, librarian):
        """Test execution of empty query."""
        results, exec_time = librarian._execute_query("")
        
        assert len(results) == 0
        assert exec_time == 0.0
    
    @patch.object(DatabaseLibrarian, '_translate_to_sql')
    @patch.object(DatabaseLibrarian, '_execute_query')
    @patch.object(DatabaseLibrarian, 'log_decision')
    def test_process_success(
        self,
        mock_log,
        mock_execute,
        mock_translate,
        librarian
    ):
        """Test successful process execution."""
        # Setup mocks
        mock_translate.return_value = "SELECT * FROM stocks LIMIT 15"
        mock_execute.return_value = (
            [{"id": 1, "symbol": "NSE|TCS-EQ"}],
            0.05
        )
        
        input_data = {
            "query": "Show me all stocks",
            "max_results": 15
        }
        
        result = librarian.process(input_data)
        
        assert result["sql"] == "SELECT * FROM stocks LIMIT 15"
        assert len(result["results"]) == 1
        assert result["count"] == 1
        assert result["execution_time"] == 0.05
        assert "error" not in result
        
        mock_translate.assert_called_once_with("Show me all stocks", 15, None)
        mock_execute.assert_called_once()
        mock_log.assert_called_once()
    
    def test_process_missing_query(self, librarian):
        """Test process with missing query."""
        result = librarian.process({})
        
        assert result["count"] == 0
        assert "error" in result
        assert "missing required field" in result["error"]
    
    def test_process_empty_query(self, librarian):
        """Test process with empty query."""
        result = librarian.process({"query": ""})
        
        assert result["count"] == 0
        assert "error" in result
        assert "cannot be empty" in result["error"]
    
    @patch.object(DatabaseLibrarian, '_translate_to_sql')
    def test_process_translation_failed(self, mock_translate, librarian):
        """Test process when translation fails."""
        mock_translate.return_value = ""
        
        result = librarian.process({"query": "Show me stocks"})
        
        assert result["count"] == 0
        assert "error" in result
        assert "Failed to generate SQL" in result["error"]
    
    @patch.object(DatabaseLibrarian, '_translate_to_sql')
    @patch.object(DatabaseLibrarian, '_execute_query')
    def test_process_with_filters(
        self,
        mock_execute,
        mock_translate,
        librarian
    ):
        """Test process with filters."""
        mock_translate.return_value = "SELECT * FROM stocks LIMIT 10"
        mock_execute.return_value = ([], 0.01)
        
        input_data = {
            "query": "Show me IT stocks",
            "max_results": 10,
            "filters": {"sector": "IT"}
        }
        
        result = librarian.process(input_data)
        
        mock_translate.assert_called_once_with(
            "Show me IT stocks",
            10,
            {"sector": "IT"}
        )
        assert result["count"] == 0
    
    def test_process_output_contract_compliance(self, librarian):
        """Test that output matches contract."""
        # Mock successful execution
        with patch.object(librarian, '_translate_to_sql', return_value="SELECT * FROM stocks"):
            with patch.object(librarian, '_execute_query', return_value=([], 0.0)):
                result = librarian.process({"query": "test"})
                
                # Check required fields
                assert "sql" in result
                assert "results" in result
                assert "count" in result
                
                # Check types
                assert isinstance(result["sql"], str)
                assert isinstance(result["results"], list)
                assert isinstance(result["count"], int)
                
                # Check optional field
                if "execution_time" in result:
                    assert isinstance(result["execution_time"], (int, float))
    
    def test_forbidden_keywords(self, librarian):
        """Test that all forbidden keywords are present."""
        assert "DROP" in librarian._forbidden_keywords
        assert "DELETE" in librarian._forbidden_keywords
        assert "TRUNCATE" in librarian._forbidden_keywords
        assert "ALTER" in librarian._forbidden_keywords
        assert "CREATE" in librarian._forbidden_keywords
        assert "INSERT" in librarian._forbidden_keywords
        assert "UPDATE" in librarian._forbidden_keywords
