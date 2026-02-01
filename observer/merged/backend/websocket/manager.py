"""WebSocket connection manager for real-time updates."""

from fastapi import WebSocket
from typing import Dict, Set


class WebSocketManager:
    """Manages WebSocket connections with room-based channels."""

    def __init__(self):
        self.connections: Dict[WebSocket, str] = {}
        self.rooms: Dict[str, Set[WebSocket]] = {}

    async def register(self, websocket: WebSocket, room: str):
        """Register a new WebSocket connection to a room."""
        await websocket.accept()

        if room not in self.rooms:
            self.rooms[room] = set()

        self.rooms[room].add(websocket)
        self.connections[websocket] = room

        # Notify room of new connection
        await self.broadcast(room, {
            "type": "connection",
            "event": "joined",
            "room": room
        })

    async def unregister(self, websocket: WebSocket):
        """Unregister a WebSocket connection."""
        if websocket in self.connections:
            room = self.connections[websocket]
            self.rooms[room].discard(websocket)
            del self.connections[websocket]

            # Clean up empty rooms
            if not self.rooms[room]:
                del self.rooms[room]

    async def broadcast(self, room: str, message: dict):
        """Broadcast a message to all connections in a room."""
        if room in self.rooms:
            dead_connections = []
            for connection in self.rooms[room]:
                try:
                    await connection.send_json(message)
                except Exception:
                    dead_connections.append(connection)

            # Clean up dead connections
            for conn in dead_connections:
                await self.unregister(conn)

    async def send_to_all(self, message: dict):
        """Broadcast to all rooms."""
        for room in list(self.rooms.keys()):
            await self.broadcast(room, message)

    def get_room_count(self, room: str) -> int:
        """Get number of connections in a room."""
        return len(self.rooms.get(room, set()))

    def get_total_connections(self) -> int:
        """Get total number of connections."""
        return len(self.connections)
