"""Authentication routes - Touch ID bridge."""

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel
from typing import Optional

from auth.biometric import request_biometric_auth, is_biometric_available
from auth.session import session_manager

router = APIRouter()


class AuthResponse(BaseModel):
    authenticated: bool
    token: Optional[str] = None
    error: Optional[str] = None


class BiometricStatus(BaseModel):
    available: bool
    reason: str


@router.get("/status")
async def get_auth_status() -> BiometricStatus:
    """Check if biometric authentication is available."""
    available, reason = is_biometric_available()
    return BiometricStatus(available=available, reason=reason)


@router.post("/biometric")
async def biometric_auth(request: Request, response: Response) -> AuthResponse:
    """Trigger Touch ID / Face ID authentication."""
    # Check if already authenticated
    existing_token = request.cookies.get("session_token")
    if existing_token and session_manager.validate_session(existing_token):
        return AuthResponse(authenticated=True, token=existing_token)

    # Request biometric auth
    success, error = request_biometric_auth("Control Room requires authentication")

    if success:
        # Create session
        user_agent = request.headers.get("user-agent", "")
        ip_address = request.client.host if request.client else ""
        token = session_manager.create_session(user_agent, ip_address)

        # Set httpOnly cookie
        response.set_cookie(
            key="session_token",
            value=token,
            httponly=True,
            secure=False,  # Set True in production with HTTPS
            samesite="lax",
            max_age=86400  # 24 hours
        )

        return AuthResponse(authenticated=True, token=token)
    else:
        return AuthResponse(authenticated=False, error=error)


@router.get("/verify")
async def verify_session(request: Request) -> AuthResponse:
    """Verify current session token."""
    token = request.cookies.get("session_token")

    if not token:
        return AuthResponse(authenticated=False, error="No session token")

    if session_manager.validate_session(token):
        return AuthResponse(authenticated=True, token=token)
    else:
        return AuthResponse(authenticated=False, error="Session expired or invalid")


@router.post("/logout")
async def logout(request: Request, response: Response) -> dict:
    """Clear session and logout."""
    token = request.cookies.get("session_token")

    if token:
        session_manager.invalidate_session(token)

    # Clear cookie
    response.delete_cookie("session_token")

    return {"success": True, "message": "Logged out successfully"}
