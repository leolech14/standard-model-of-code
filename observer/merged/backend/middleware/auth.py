"""Authentication middleware for protected routes."""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from auth.session import session_manager


# Routes that don't require authentication
PUBLIC_ROUTES = {
    "/",
    "/index.html",
    "/health",
    "/auth/status",
    "/auth/biometric",
    "/docs",
    "/openapi.json",
}


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce authentication on protected routes."""

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Allow public routes
        if path in PUBLIC_ROUTES:
            return await call_next(request)

        # Allow WebSocket connections (they handle auth separately)
        if path.startswith("/ws"):
            return await call_next(request)

        # Allow static files
        if path.startswith("/assets") or path.startswith("/static"):
            return await call_next(request)

        # Check for session token
        token = request.cookies.get("session_token")

        if not token:
            return JSONResponse(
                status_code=401,
                content={"detail": "Authentication required"}
            )

        if not session_manager.validate_session(token):
            return JSONResponse(
                status_code=401,
                content={"detail": "Session expired or invalid"}
            )

        # Request is authenticated, continue
        return await call_next(request)


def require_auth(request: Request) -> bool:
    """Dependency to require authentication.

    Usage:
        @router.get("/protected")
        async def protected_route(authenticated: bool = Depends(require_auth)):
            ...
    """
    token = request.cookies.get("session_token")

    if not token or not session_manager.validate_session(token):
        raise HTTPException(status_code=401, detail="Authentication required")

    return True
