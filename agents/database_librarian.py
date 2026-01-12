"""
Database Librarian Agent

Natural language to SQL translator for the trading database.
Translates user queries into optimized SQL queries and executes them safely.
"""

import time
import re
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
    
    def __init__(self):
        """Initialize Database Librarian agent."""
        super().__init__("database_librarian", "database")
        self.schema = self._load_schema()
        self._forbidden_keywords = [
            "DROP", "DELETE", "TRUNCATE", "ALTER", "CREATE", "INSERT",
            "UPDATE", "REPLACE", "GRANT", "REVOKE", "EXEC", "EXECUTE"
        ]
    
    def _load_schema(self) -> str:
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
    
    def _translate_to_sql(
        self,
        natural_language_query: str,
        max_results: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Translate natural language query to SQL using LLM.
        
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
        
        # Build prompt with schema and query
        max_results = max_results or 15
        
        prompt = f"""You are a SQLite expert for a trading database.

DATABASE SCHEMA:
{self.schema}

USER QUERY: "{natural_language_query}"

REQUIREMENTS:
1. Generate ONLY a valid SQLite SELECT query
2. Use LIMIT {max_results} to limit results
3. Use proper JOINs when accessing related tables
4. Use parameterized queries (?) for any user inputs
5. Return ONLY the SQL query, no explanations, no markdown
6. Do NOT include comments in the SQL
7. Use proper table aliases for readability

ADDITIONAL FILTERS:
{filters if filters else "None"}

SQL QUERY:"""
        
        try:
            # Call LLM
            response = self.llm.invoke(prompt)
            
            # Clean up response
            sql = response.strip()
            
            # Remove markdown code blocks if present
            sql = re.sub(r'```sql\s*', '', sql, flags=re.IGNORECASE)
            sql = re.sub(r'```\s*', '', sql)
            sql = sql.strip()
            
            # Remove leading/trailing whitespace and newlines
            sql = ' '.join(sql.split())
            
            # Validate safety
            if not self._validate_query_safety(sql):
                logger.error(f"Generated unsafe SQL query: {sql}")
                return ""
            
            logger.debug(f"Generated SQL: {sql}")
            return sql
            
        except Exception as e:
            logger.error(f"SQL translation error: {e}")
            return ""
    
    def _execute_query(self, sql: str) -> tuple[List[Dict[str, Any]], float]:
        """
        Execute SQL query safely and return results.
        
        Args:
            sql: SQL query string
        
        Returns:
            Tuple of (results list, execution_time in seconds)
        """
        if not sql or not sql.strip():
            return [], 0.0
        
        start_time = time.time()
        
        try:
            with engine.connect() as connection:
                # Execute query
                result = connection.execute(text(sql))
                
                # Get column names
                columns = result.keys()
                
                # Fetch all rows
                rows = result.fetchall()
                
                # Convert to list of dicts
                results = [dict(zip(columns, row)) for row in rows]
                
                execution_time = time.time() - start_time
                
                logger.debug(f"Query executed in {execution_time:.3f}s, returned {len(results)} rows")
                return results, execution_time
                
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"SQL execution error: {e}")
            logger.error(f"Failed query: {sql}")
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
        
        if not query or not query.strip():
            return {
                "sql": "",
                "results": [],
                "count": 0,
                "execution_time": 0.0,
                "error": "Query cannot be empty"
            }
        
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
