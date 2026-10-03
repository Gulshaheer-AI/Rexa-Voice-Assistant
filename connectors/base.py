"""
Base interface for Rexa Business Data Providers.
Allows any data source (Files, SQL Databases, REST APIs, CRM/ERP)
to plug into Rexa without modifying the core assistant logic.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseBusinessConnector(ABC):
    """Abstract Base Class for all Rexa business data connectors."""

    @abstractmethod
    def load_data(self) -> Dict[str, Any]:
        """Load or refresh raw business data from the underlying source."""
        pass

    @abstractmethod
    def get_summary_context(self) -> str:
        """
        Generate a concise, structured textual snapshot of the business's
        current financial metrics, marketing campaigns, and operations.
        This snapshot is injected into the LLM prompt for contextual synthesis.
        """
        pass

    @abstractmethod
    def get_financials(self) -> Dict[str, Any]:
        """Return standardized financial metrics (profit, revenue, expenses, etc.)."""
        pass

    @abstractmethod
    def get_campaigns(self) -> list:
        """Return a list of marketing campaigns with spend, conversions, and ROAS."""
        pass
