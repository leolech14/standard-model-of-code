"""Session management for authenticated users."""

import secrets
import time
from typing import Dict, Optional
from dataclasses import dataclass, field


def generate_token() -> str:
    """Generate a secure random token for session auth."""
    return secrets.token_urlsafe(32)


@dataclass
class Session:
    """User session."""
    token: str
    created_at: float
    last_accessed: float
    user_agent: str = ""
    ip_address: str = ""


class SessionManager:
    """Manages authenticated sessions.

    Sessions expire after 24 hours of inactivity.
    """

    def __init__(self, session_timeout: int = 86400):  # 24 hours
        self._sessions: Dict[str, Session] = {}
        self._session_timeout = session_timeout

    def create_session(self, user_agent: str = "", ip_address: str = "") -> str:
        """Create a new session and return the token."""
        token = generate_token()
        now = time.time()

        self._sessions[token] = Session(
            token=token,
            created_at=now,
            last_accessed=now,
            user_agent=user_agent,
            ip_address=ip_address
        )

        # Clean up expired sessions periodically
        self._cleanup_expired()

        return token

    def validate_session(self, token: str) -> bool:
        """Validate a session token and update last accessed time."""
        if not token or token not in self._sessions:
            return False

        session = self._sessions[token]
        now = time.time()

        # Check if session has expired
        if now - session.last_accessed > self._session_timeout:
            del self._sessions[token]
            return False

        # Update last accessed time
        session.last_accessed = now
        return True

    def invalidate_session(self, token: str) -> bool:
        """Invalidate/logout a session."""
        if token in self._sessions:
            del self._sessions[token]
            return True
        return False

    def get_session(self, token: str) -> Optional[Session]:
        """Get session info if valid."""
        if self.validate_session(token):
            return self._sessions.get(token)
        return None

    def _cleanup_expired(self):
        """Remove expired sessions."""
        now = time.time()
        expired = [
            token for token, session in self._sessions.items()
            if now - session.last_accessed > self._session_timeout
        ]
        for token in expired:
            del self._sessions[token]

    @property
    def active_session_count(self) -> int:
        """Get count of active sessions."""
        self._cleanup_expired()
        return len(self._sessions)


# Global session manager instance
session_manager = SessionManager()
