from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.rooms: dict[int, list[WebSocket]] = {}

    async def connect(self, board_id: int, websocket: WebSocket):
        await websocket.accept()
        self.rooms.setdefault(board_id, []).append(websocket)

    def disconnect(self, board_id: int, websocket: WebSocket):
        self.rooms[board_id].remove(websocket)
        if not self.rooms[board_id]:
            del self.rooms[board_id]

    async def broadcast(self, board_id: int, message: str, sender: WebSocket):
        for connection in self.rooms.get(board_id, []):
            if connection is not sender:
                await connection.send_text(message)

manager = ConnectionManager()