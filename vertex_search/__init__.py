"""
Vertex AI Search Python Integration

A comprehensive Python client for Google Cloud Vertex AI Search API.
Supports search queries, answer generation, and conversational search with sessions.
"""

from .client import VertexSearchClient
from .session import SessionManager
from .models import SearchResult, AnswerResponse, SessionInfo

__version__ = "1.0.0"
__all__ = ["VertexSearchClient", "SessionManager", "SearchResult", "AnswerResponse", "SessionInfo"]
