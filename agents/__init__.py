"""
Agents Module

All agents inherit from BaseAgent and implement the process() method.
Agents are designed to work with the orchestrator.
"""

from agents.base_agent import BaseAgent
from agents.database_librarian import DatabaseLibrarian

__all__ = [
    "BaseAgent",
    "DatabaseLibrarian",
]

__version__ = "1.2.0"
