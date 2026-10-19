import asyncio
import json
import uuid

import redis.asyncio as redis
from fastapi import WebSocket

REDIS_URL = "redis://127.0.0.1:6379"


class ConnectionManager:
    def __init__(self):
        self.rooms: dict[int, list[WebSocket]] = {}
        self.server_id = uuid.uuid4().hex
        self.redis = None
        self.pubsub = None
        self.listener_task = None

    # ---------- lifecycle ----------
    async def start(self):
        self.redis = redis.from_url(REDIS_URL, decode_responses=True)
        self.pubsub = self.redis.pubsub()
        await self.pubsub.psubscribe("board:*")
        self.listener_task = asyncio.create_task(self._listen())

    async def stop(self):
        if self.listener_task:
            self.listener_task.cancel()
            try:
                await self.listener_task
            except asyncio.CancelledError:
                pass
        if self.pubsub:
            await self.pubsub.aclose()
        if self.redis:
            await self.redis.aclose()

    # ---------- local connections ----------
    async def connect(self, board_id: int, websocket: WebSocket):
        await websocket.accept()
        self.rooms.setdefault(board_id, []).append(websocket)

    def disconnect(self, board_id: int, websocket: WebSocket):
        self.rooms[board_id].remove(websocket)
        if not self.rooms[board_id]:
            del self.rooms[board_id]

    # ---------- publishing ----------
    async def broadcast(self, board_id: int, message: str, sender: WebSocket):
        envelope = {
            "origin": self.server_id,
            "sender": id(sender),
            "data": message,
        }
        await self.redis.publish(f"board:{board_id}", json.dumps(envelope))

    # ---------- receiving ----------
    async def _listen(self):
        async for message in self.pubsub.listen():
            if message["type"] != "pmessage":
                continue
            try:
                board_id = int(message["channel"].split(":")[1])
                envelope = json.loads(message["data"])
                await self._deliver(board_id, envelope)
            except Exception as e:
                print("Redis listener error:", e)

    async def _deliver(self, board_id: int, envelope: dict):
        for connection in list(self.rooms.get(board_id, [])):
            is_sender = (
                envelope["origin"] == self.server_id
                and envelope["sender"] == id(connection)
            )
            if is_sender:
                continue
            try:
                await connection.send_text(envelope["data"])
            except Exception:
                pass  # a dead connection is cleaned up by its own receive loop


manager = ConnectionManager()