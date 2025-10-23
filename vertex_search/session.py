"""
Session management for conversational search with Vertex AI Search.
"""

import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime
from .models import SessionInfo


class SessionManager:
    """Manages sessions for conversational search with follow-up questions."""
    
    def __init__(self):
        self._active_sessions: Dict[str, SessionInfo] = {}
        self._session_history: Dict[str, List[Dict[str, Any]]] = {}
    
    def create_session(self, user_pseudo_id: Optional[str] = None) -> str:
        """
        Create a new session for conversational search.
        
        Args:
            user_pseudo_id: Optional user identifier for personalization
            
        Returns:
            Session ID (ends with '-' to indicate new session)
        """
        session_id = f"{uuid.uuid4().hex}-"
        
        session_info = SessionInfo(
            session_id=session_id,
            user_pseudo_id=user_pseudo_id,
            start_time=datetime.now(),
            state="IN_PROGRESS"
        )
        
        self._active_sessions[session_id] = session_info
        self._session_history[session_id] = []
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """
        Get session information by ID.
        
        Args:
            session_id: The session ID
            
        Returns:
            SessionInfo if found, None otherwise
        """
        return self._active_sessions.get(session_id)
    
    def update_session(self, session_id: str, query: str, query_id: str, answer_id: str) -> None:
        """
        Update session with new query and answer information.
        
        Args:
            session_id: The session ID
            query: The search query
            query_id: The query ID from the search response
            answer_id: The answer ID from the answer response
        """
        if session_id in self._active_sessions:
            turn = {
                "query": {
                    "queryId": query_id,
                    "text": query
                },
                "answer": answer_id,
                "timestamp": datetime.now().isoformat()
            }
            
            self._session_history[session_id].append(turn)
            self._active_sessions[session_id].turns = self._session_history[session_id]
    
    def end_session(self, session_id: str) -> None:
        """
        End a session.
        
        Args:
            session_id: The session ID to end
        """
        if session_id in self._active_sessions:
            self._active_sessions[session_id].end_time = datetime.now()
            self._active_sessions[session_id].state = "COMPLETED"
    
    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get the conversation history for a session.
        
        Args:
            session_id: The session ID
            
        Returns:
            List of conversation turns
        """
        return self._session_history.get(session_id, [])
    
    def list_active_sessions(self) -> List[SessionInfo]:
        """
        List all active sessions.
        
        Returns:
            List of active SessionInfo objects
        """
        return [
            session for session in self._active_sessions.values()
            if session.state == "IN_PROGRESS"
        ]
    
    def list_sessions_for_user(self, user_pseudo_id: str) -> List[SessionInfo]:
        """
        List sessions for a specific user.
        
        Args:
            user_pseudo_id: The user pseudo ID
            
        Returns:
            List of SessionInfo objects for the user
        """
        return [
            session for session in self._active_sessions.values()
            if session.user_pseudo_id == user_pseudo_id
        ]
    
    def is_new_session(self, session_id: str) -> bool:
        """
        Check if a session ID indicates a new session (ends with '-').
        
        Args:
            session_id: The session ID to check
            
        Returns:
            True if this is a new session, False otherwise
        """
        return session_id.endswith('-')
    
    def get_clean_session_id(self, session_id: str) -> str:
        """
        Get the clean session ID (remove trailing '-' if present).
        
        Args:
            session_id: The session ID
            
        Returns:
            Clean session ID without trailing '-'
        """
        return session_id.rstrip('-')
    
    def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """
        Clean up old sessions.
        
        Args:
            max_age_hours: Maximum age of sessions to keep (in hours)
            
        Returns:
            Number of sessions cleaned up
        """
        now = datetime.now()
        cutoff_time = now.timestamp() - (max_age_hours * 3600)
        
        sessions_to_remove = []
        for session_id, session in self._active_sessions.items():
            if session.start_time and session.start_time.timestamp() < cutoff_time:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del self._active_sessions[session_id]
            if session_id in self._session_history:
                del self._session_history[session_id]
        
        return len(sessions_to_remove)
