"""Session Manager for per-user session isolation"""
import uuid
import threading
from typing import Dict, Optional
from datetime import datetime, timedelta
import logging

from .login_auth import LoginTokenProvider

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages per-user LoginTokenProvider instances.

    Solves the multi-user session sharing issue by maintaining
    separate session state for each user identified by session_id.
    """

    def __init__(self, session_timeout_minutes: int = 30):
        self._sessions: Dict[str, LoginTokenProvider] = {}
        self._session_metadata: Dict[str, dict] = {}  # created_at, last_accessed
        self._lock = threading.Lock()
        self._session_timeout = timedelta(minutes=session_timeout_minutes)

    def generate_session_id(self) -> str:
        """Generate a new unique session ID"""
        return str(uuid.uuid4())

    def create_session(self, session_id: Optional[str] = None) -> tuple[str, LoginTokenProvider]:
        """
        Create a new session with its own LoginTokenProvider.

        Args:
            session_id: Optional session ID. If not provided, generates a new one.

        Returns:
            Tuple of (session_id, LoginTokenProvider)
        """
        with self._lock:
            if not session_id:
                session_id = self.generate_session_id()

            # Create new provider for this session
            token_provider = LoginTokenProvider()
            self._sessions[session_id] = token_provider
            self._session_metadata[session_id] = {
                "created_at": datetime.now(),
                "last_accessed": datetime.now()
            }

            logger.info(f"Created new session: {session_id[:8]}...")
            return session_id, token_provider

    def get_session(self, session_id: str) -> Optional[LoginTokenProvider]:
        """
        Get the LoginTokenProvider for a given session_id.

        Args:
            session_id: The session identifier

        Returns:
            LoginTokenProvider if session exists and is valid, None otherwise
        """
        with self._lock:
            if session_id not in self._sessions:
                logger.debug(f"Session not found: {session_id[:8] if session_id else 'None'}...")
                return None

            # Check if session expired
            metadata = self._session_metadata.get(session_id, {})
            last_accessed = metadata.get("last_accessed")
            if last_accessed and datetime.now() - last_accessed > self._session_timeout:
                logger.info(f"Session expired: {session_id[:8]}...")
                self._remove_session_internal(session_id)
                return None

            # Update last accessed time
            self._session_metadata[session_id]["last_accessed"] = datetime.now()

            return self._sessions[session_id]

    def get_or_create_session(self, session_id: Optional[str] = None) -> tuple[str, LoginTokenProvider]:
        """
        Get existing session or create a new one.

        Args:
            session_id: Optional session ID. If provided and valid, returns existing session.
                       If not provided or invalid, creates new session.

        Returns:
            Tuple of (session_id, LoginTokenProvider)
        """
        if session_id:
            provider = self.get_session(session_id)
            if provider:
                return session_id, provider

        # Create new session
        return self.create_session(session_id)

    def remove_session(self, session_id: str) -> bool:
        """
        Remove a session (logout).

        Args:
            session_id: The session to remove

        Returns:
            True if session was removed, False if not found
        """
        with self._lock:
            return self._remove_session_internal(session_id)

    def _remove_session_internal(self, session_id: str) -> bool:
        """Internal session removal (must be called with lock held)"""
        if session_id in self._sessions:
            # Clear session data before removing
            self._sessions[session_id].clear_session()
            del self._sessions[session_id]
            if session_id in self._session_metadata:
                del self._session_metadata[session_id]
            logger.info(f"Removed session: {session_id[:8]}...")
            return True
        return False

    def list_sessions(self) -> list[str]:
        """List all active session IDs"""
        with self._lock:
            return list(self._sessions.keys())

    def get_session_count(self) -> int:
        """Get count of active sessions"""
        with self._lock:
            return len(self._sessions)

    def cleanup_expired_sessions(self) -> int:
        """
        Remove all expired sessions.

        Returns:
            Number of sessions cleaned up
        """
        with self._lock:
            now = datetime.now()
            expired = []

            for session_id, metadata in self._session_metadata.items():
                last_accessed = metadata.get("last_accessed")
                if last_accessed and now - last_accessed > self._session_timeout:
                    expired.append(session_id)

            for session_id in expired:
                self._remove_session_internal(session_id)

            if expired:
                logger.info(f"Cleaned up {len(expired)} expired sessions")

            return len(expired)

    def get_session_info(self, session_id: str) -> Optional[dict]:
        """
        Get metadata about a session.

        Returns:
            Dict with session info or None if not found
        """
        with self._lock:
            if session_id not in self._sessions:
                return None

            metadata = self._session_metadata.get(session_id, {})
            provider = self._sessions[session_id]

            return {
                "session_id": session_id,
                "created_at": metadata.get("created_at"),
                "last_accessed": metadata.get("last_accessed"),
                "is_authenticated": provider.is_authenticated(),
                "user_info": provider.get_user_info() if provider.is_authenticated() else None
            }
