"""
Control Room - FastAPI Backend

Merged from:
- File Explorer (tools/file_explorer.py)
- Refinery Dashboard API requirements
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import sys
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from routes import files, operations, history, search, auth
from websocket.manager import WebSocketManager
from middleware.auth import AuthMiddleware

# WebSocket manager instance
ws_manager = WebSocketManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    print("Control Room starting...")
    print(f"  API: http://localhost:8000")
    print(f"  Docs: http://localhost:8000/docs")
    yield
    print("Control Room shutting down...")


app = FastAPI(
    title="Control Room",
    description="Unified file operations + pipeline monitoring",
    version="1.0.0",
    lifespan=lifespan
)

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth middleware (uncomment to enable)
# app.add_middleware(AuthMiddleware)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(files.router, prefix="/api", tags=["files"])
app.include_router(operations.router, prefix="/api", tags=["operations"])
app.include_router(history.router, prefix="/api", tags=["history"])
app.include_router(search.router, prefix="/api", tags=["search"])


@app.get("/")
async def root():
    """Root endpoint - redirect to docs or serve frontend."""
    return {
        "name": "Control Room",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "auth": "/auth",
            "files": "/api/list",
            "search": "/api/search",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    from services.history import history_service

    return {
        "status": "healthy",
        "service": "observer",
        "websocket_connections": ws_manager.get_total_connections(),
        "history_state": {
            "can_undo": history_service.can_undo,
            "can_redo": history_service.can_redo
        }
    }


@app.websocket("/ws/{room}")
async def websocket_endpoint(websocket: WebSocket, room: str):
    """WebSocket endpoint for real-time updates."""
    await ws_manager.register(websocket, room)
    try:
        while True:
            data = await websocket.receive_json()

            # Handle different message types
            msg_type = data.get('type', 'broadcast')

            if msg_type == 'ping':
                await websocket.send_json({'type': 'pong'})
            else:
                # Broadcast to room
                await ws_manager.broadcast(room, data)

    except WebSocketDisconnect:
        await ws_manager.unregister(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
