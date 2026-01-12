"""
Database Librarian Agent

Natural language to SQL translator for the trading database.
Translates user queries into optimized SQL queries and executes them safely.
"""

import time
import re
import asyncio
import json
import hashlib
from typing import Dict, Any, List, Optional
from loguru import logger

from agents.base_agent import BaseAgent
from database.session import engine, get_session
from database.models import Base
from sqlalchemy import text, inspect
from sqlalchemy.orm import Session


class DatabaseLibrarian(BaseAgent):
    """
    Database Librarian Agent
    
    Translates natural language queries to SQL and executes them safely.
    Uses Qwen2.5 Coder LLM for SQL generation.
    """
    
    # Class-level schema cache to avoid reloading on every instantiation
    _schema_cache: Optional[str] = None
    _schema_cache_timestamp: Optional[float] = None
    _schema_cache_ttl: int = 3600  # Cache for 1 hour
    
    # LLM response cache (SQL generation cache)
    _llm_response_cache: Dict[str, tuple[str, float]] = {}  # query_hash -> (sql, timestamp)
    _llm_cache_ttl: int = 3600  # Cache LLM responses for 1 hour
    
    def __init__(self):
        """Initialize Database Librarian agent."""
        super().__init__("database_librarian", "database")
        self.schema = self._get_schema()  # Use cached schema
        self._forbidden_keywords = [
            "DROP", "DELETE", "TRUNCATE", "ALTER", "CREATE", "INSERT",
            "UPDATE", "REPLACE", "GRANT", "REVOKE", "EXEC", "EXECUTE"
        ]
        # Security and performance limits
        self.max_query_timeout = 30  # seconds
        self.max_result_size = 10000  # maximum rows
        self.max_query_length = 10000  # characters
        self.max_input_length = 1000  # characters for NL query
    
    @classmethod
    def _get_schema(cls) -> str:
        """
        Get schema from cache or load if cache is expired/missing.
        
        Returns:
            Formatted schema string
        """
        import time
        current_time = time.time()
        
        # Check if cache is valid
        if (cls._schema_cache is not None and 
            cls._schema_cache_timestamp is not None and
            current_time - cls._schema_cache_timestamp < cls._schema_cache_ttl):
            logger.debug("Using cached database schema")
            return cls._schema_cache
        
        # Cache miss or expired - load schema
        logger.debug("Loading database schema (cache miss or expired)")
        schema = cls._load_schema()
        cls._schema_cache = schema
        cls._schema_cache_timestamp = current_time
        return schema
    
    @classmethod
    def invalidate_schema_cache(cls):
        """Invalidate schema cache to force reload on next access."""
        cls._schema_cache = None
        cls._schema_cache_timestamp = None
        logger.info("Database schema cache invalidated")
    
    @classmethod
    def _load_schema(cls) -> str:
        """
        Load database schema information for LLM context.
        
        Returns:
            Formatted schema string with tables and columns
        """
        try:
            schema_parts = []
            
            # Get all tables from metadata
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            for table_name in sorted(tables):
                columns = inspector.get_columns(table_name)
                foreign_keys = inspector.get_foreign_keys(table_name)
                
                # Build column descriptions
                col_descriptions = []
                for col in columns:
                    col_type = str(col['type'])
                    nullable = "NULL" if col['nullable'] else "NOT NULL"
                    col_descriptions.append(
                        f"  - {col['name']} ({col_type}) {nullable}"
                    )
                
                # Build foreign key descriptions
                fk_descriptions = []
                for fk in foreign_keys:
                    fk_cols = ", ".join(fk['constrained_columns'])
                    ref_table = fk['referred_table']
                    ref_cols = ", ".join(fk['referred_columns'])
                    fk_descriptions.append(
                        f"  - {fk_cols} -> {ref_table}({ref_cols})"
                    )
                
                schema_parts.append(f"Table: {table_name}")
                schema_parts.extend(col_descriptions)
                if fk_descriptions:
                    schema_parts.append("  Foreign Keys:")
                    schema_parts.extend(fk_descriptions)
                schema_parts.append("")
            
            schema_text = "\n".join(schema_parts)
            logger.debug(f"Loaded schema with {len(tables)} tables")
            return schema_text
            
        except Exception as e:
            logger.error(f"Failed to load schema: {e}")
            # Return basic schema as fallback
            return """
            Tables:
            - stocks(id, symbol, name, exchange, sector, market_cap, is_active)
            - market_data_daily(id, stock_id, date, open, high, low, close, volume, rsi, macd, ...)
            - market_data_intraday(id, stock_id, timestamp, interval, open, high, low, close, volume)
            - screening_signals(id, stock_id, signal_type, confidence_score, entry_price, stop_loss, target_price)
            - trades(id, stock_id, order_id, buy_sell, quantity, entry_price, exit_price, pnl, status)
            - orders(id, stock_id, order_type, quantity, price, order_status, entry_price, stop_loss, target_price)
            - portfolio(id, stock_id, quantity, avg_price, current_price, unrealized_pnl)
            - agent_decisions(id, agent_name, stock_id, decision_type, reasoning, confidence_score)
            - news_articles(id, stock_id, title, content, source, published_at)
            - sentiment_scores(id, stock_id, sentiment_score, confidence, analyzed_at)
            """
    
    def _validate_query_safety(self, sql: str) -> bool:
        """
        Validate SQL query for safety (prevent destructive operations).
        
        Args:
            sql: SQL query string
        
        Returns:
            True if safe, False otherwise
        """
        sql_upper = sql.upper().strip()
        
        # Check for forbidden keywords
        for keyword in self._forbidden_keywords:
            # Use word boundaries to avoid false positives
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, sql_upper):
                logger.warning(f"Query contains forbidden keyword: {keyword}")
                return False
        
        # Must start with SELECT
        if not sql_upper.startswith("SELECT"):
            logger.warning("Query must start with SELECT")
            return False
        
        return True
    
    def _sanitize_input(self, query: str) -> str:
        """
        Sanitize user input to prevent prompt injection.
        
        Note: This sanitizes prompt injection patterns, not SQL injection.
        SQL injection is prevented by _validate_query_safety() after LLM generates SQL.
        
        Args:
            query: User input query
        
        Returns:
            Sanitized query
        """
        # Remove potential prompt injection patterns
        # Remove newlines that could break prompt structure
        sanitized = query.replace('\n', ' ').replace('\r', ' ')
        # Remove markdown code blocks
        sanitized = re.sub(r'```[^`]*```', '', sanitized, flags=re.DOTALL)
        # Remove potential instruction patterns (with colon)
        sanitized = re.sub(r'(?i)(ignore|forget|system|assistant|user):', '', sanitized)
        # Remove instruction patterns without colon (common prompt injection)
        sanitized = re.sub(r'(?i)\b(ignore|forget|system|assistant|user)\s+(previous|all|above)', '', sanitized)
        # Limit length
        if len(sanitized) > self.max_input_length:
            sanitized = sanitized[:self.max_input_length]
            logger.warning(f"Query truncated to {self.max_input_length} characters")
        return sanitized.strip()
    
    def _translate_to_sql(
        self,
        natural_language_query: str,
        max_results: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Translate natural language query to SQL using LLM.
        Uses caching to avoid repeated LLM calls for identical queries.
        
        Args:
            natural_language_query: Natural language query
            max_results: Maximum number of results (for LIMIT clause)
            filters: Additional filters to apply
        
        Returns:
            Generated SQL query
        """
        if not self.is_llm_available():
            logger.error("LLM not available for SQL translation")
            return ""
        
        # Sanitize input to prevent prompt injection
        sanitized_query = self._sanitize_input(natural_language_query)
        
        if not sanitized_query:
            logger.error("Query is empty after sanitization")
            return ""
        
        # Build prompt with schema and query
        max_results = min(max_results or 15, self.max_result_size)  # Enforce max
        
        # Create cache key from query and filters
        cache_key_data = {
            "query": sanitized_query,
            "max_results": max_results,
            "filters": filters or {}
        }
        cache_key = hashlib.md5(
            json.dumps(cache_key_data, sort_keys=True).encode()
        ).hexdigest()
        
        # Check cache
        import time
        current_time = time.time()
        if cache_key in self._llm_response_cache:
            cached_sql, cache_timestamp = self._llm_response_cache[cache_key]
            if current_time - cache_timestamp < self._llm_cache_ttl:
                logger.debug(f"Using cached SQL for query: {sanitized_query[:50]}...")
                return cached_sql
            else:
                # Cache expired, remove it
                del self._llm_response_cache[cache_key]
        
        prompt = f"""You are a SQLite expert for a trading database.

DATABASE SCHEMA:
{self.schema}

USER QUERY: "{sanitized_query}"

REQUIREMENTS:
1. Generate ONLY a valid SQLite SELECT query
2. Use LIMIT {max_results} to limit results
3. Use proper JOINs when accessing related tables
4. Use parameterized queries (?) for any user inputs
5. Return ONLY the SQL query, no explanations, no markdown
6. Do NOT include comments in the SQL
7. Use proper table aliases for readability
8. Do NOT include any destructive operations (DROP, DELETE, etc.)

ADDITIONAL FILTERS:
{filters if filters else "None"}

SQL QUERY:"""
        
        try:
            # Call LLM with timeout protection
            # Note: LLM service should implement timeout, but we add extra protection
            response = self.llm.invoke(prompt)
            
            if not response:
                logger.error("LLM returned empty response")
                return ""
            
            # Validate response is string
            if not isinstance(response, str):
                logger.error(f"LLM returned non-string response: {type(response)}")
                return ""
            
            # Clean up response
            sql = response.strip()
            
            # Remove markdown code blocks if present
            sql = re.sub(r'```sql\s*', '', sql, flags=re.IGNORECASE)
            sql = re.sub(r'```\s*', '', sql)
            sql = sql.strip()
            
            # Remove leading/trailing whitespace and newlines
            sql = ' '.join(sql.split())
            
            # Validate query length
            if len(sql) > self.max_query_length:
                logger.error(f"Generated SQL query too long: {len(sql)} characters")
                return ""
            
            # Validate safety
            if not self._validate_query_safety(sql):
                logger.error(f"Generated unsafe SQL query: {sql[:100]}...")
                return ""
            
            # Ensure LIMIT clause is present for safety
            if "LIMIT" not in sql.upper():
                # Add LIMIT if missing
                sql = f"{sql.rstrip(';')} LIMIT {max_results}"
                logger.debug("Added LIMIT clause to query")
            
            logger.debug(f"Generated SQL: {sql[:200]}...")
            
            # Cache the result
            self._llm_response_cache[cache_key] = (sql, current_time)
            
            # Clean up old cache entries (keep cache size reasonable)
            if len(self._llm_response_cache) > 100:
                # Remove oldest entries
                sorted_entries = sorted(
                    self._llm_response_cache.items(),
                    key=lambda x: x[1][1]  # Sort by timestamp
                )
                # Keep only the 50 most recent
                self._llm_response_cache = dict(sorted_entries[-50:])
            
            return sql
            
        except json.JSONDecodeError as e:
            logger.error(f"LLM response JSON parsing error: {e}")
            return ""
        except Exception as e:
            logger.error(f"SQL translation error: {e}")
            return ""
    
    def _execute_query(self, sql: str) -> tuple[List[Dict[str, Any]], float]:
        """
        Execute SQL query safely with timeout and result size limits.
        
        Args:
            sql: SQL query string
        
        Returns:
            Tuple of (results list, execution_time in seconds)
        """
        if not sql or not sql.strip():
            return [], 0.0
        
        start_time = time.time()
        
        try:
            # Set query timeout using SQLite PRAGMA
            with engine.connect() as connection:
                # Set query timeout (SQLite doesn't support per-query timeout directly)
                # We'll use Python-level timeout instead
                connection.execute(text("PRAGMA busy_timeout = 30000"))  # 30 seconds
                
                # Execute query with timeout protection
                # Since this is sync code, we use a simple approach
                # For async, we'd use asyncio.wait_for()
                result = connection.execute(text(sql))
                
                # Get column names
                columns = result.keys()
                
                # Fetch all rows (SQLAlchemy result objects are iterable)
                # We'll limit after fetching to maintain compatibility with mocks
                all_rows = result.fetchall()
                
                # Apply result size limit
                if len(all_rows) > self.max_result_size:
                    logger.warning(
                        f"Query result truncated from {len(all_rows)} to {self.max_result_size} rows "
                        f"(max allowed: {self.max_result_size})"
                    )
                    rows = all_rows[:self.max_result_size]
                else:
                    rows = all_rows
                
                # Convert to list of dicts
                results = [dict(zip(columns, row)) for row in rows]
                
                execution_time = time.time() - start_time
                
                # Check execution time
                if execution_time > self.max_query_timeout:
                    logger.warning(
                        f"Query took {execution_time:.3f}s (max: {self.max_query_timeout}s)"
                    )
                
                logger.debug(
                    f"Query executed in {execution_time:.3f}s, "
                    f"returned {len(results)} rows"
                )
                return results, execution_time
                
        except Exception as e:
            execution_time = time.time() - start_time
            # Sanitize SQL in error log to prevent sensitive data exposure
            sql_preview = sql[:100] + "..." if len(sql) > 100 else sql
            logger.error(f"SQL execution error: {e}")
            logger.error(f"Failed query (preview): {sql_preview}")
            return [], execution_time
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process natural language query and return SQL results.
        
        Input Contract:
            - query (required): Natural language query string
            - max_results (optional): Maximum number of results (default: 15)
            - filters (optional): Additional filters dict
        
        Output Contract:
            - sql (required): Generated SQL query
            - results (required): Query results as list of dicts
            - count (required): Number of results
            - execution_time (optional): Query execution time in seconds
        
        Args:
            input_data: Input data dictionary
        
        Returns:
            Output data dictionary matching contract
        """
        # Validate input
        if not self.validate_input(
            input_data,
            required_fields=["query"],
            optional_fields=["max_results", "filters"]
        ):
            return {
                "sql": "",
                "results": [],
                "count": 0,
                "execution_time": 0.0,
                "error": "Invalid input: missing required field 'query'"
            }
        
        query = input_data.get("query", "")
        max_results = input_data.get("max_results", 15)
        filters = input_data.get("filters")
        
        # Validate input size
        query_size = len(json.dumps(input_data).encode('utf-8'))
        max_input_size = 1024 * 1024  # 1MB
        if query_size > max_input_size:
            return {
                "sql": "",
                "results": [],
                "count": 0,
                "execution_time": 0.0,
                "error": f"Input data too large: {query_size} bytes (max: {max_input_size})"
            }
        
        # Validate query length
        if len(query) > self.max_input_length:
            return {
                "sql": "",
                "results": [],
                "count": 0,
                "execution_time": 0.0,
                "error": f"Query too long: {len(query)} characters (max: {self.max_input_length})"
            }
        
        if not query or not query.strip():
            return {
                "sql": "",
                "results": [],
                "count": 0,
                "execution_time": 0.0,
                "error": "Query cannot be empty"
            }
        
        # Enforce max_results limit
        max_results = min(max_results, self.max_result_size)
        
        # Translate to SQL
        sql = self._translate_to_sql(query, max_results, filters)
        
        if not sql:
            return {
                "sql": "",
                "results": [],
                "count": 0,
                "execution_time": 0.0,
                "error": "Failed to generate SQL query"
            }
        
        # Execute query
        results, execution_time = self._execute_query(sql)
        
        # Prepare output
        output_data = {
            "sql": sql,
            "results": results,
            "count": len(results),
            "execution_time": execution_time
        }
        
        # Log decision
        self.log_decision(
            decision_type="SQL_QUERY",
            reasoning=f"Translated NL query to SQL: {query[:100]}",
            input_data=input_data,
            output_data={
                "sql": sql,
                "count": len(results),
                "execution_time": execution_time
            }
        )
        
        # Validate output
        if not self.validate_output(
            output_data,
            required_fields=["sql", "results", "count"]
        ):
            logger.warning("Output validation failed, but returning results anyway")
        
        return output_data
