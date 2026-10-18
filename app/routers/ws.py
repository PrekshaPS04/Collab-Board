import json
import jwt
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from .. import models, auth
from ..database import SessionLocal
from ..manager import manager

router = APIRouter(tags=["websocket"])


def save_content(board_id: int, content: str) -> None:
    with SessionLocal() as db:
        board = db.get(models.Board, board_id)
        if board:
            board.content = content
            db.commit()


@router.websocket("/ws/echo")
async def echo(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_text()
            await websocket.send_text(f"You said: {message}")
    except WebSocketDisconnect:
        print("Client disconnected")


@router.websocket("/ws/boards/{board_id}")
async def board_socket(websocket: WebSocket, board_id: int, token: str = Query(...)):
    # 1. Verify the token
    try:
        user_id = auth.decode_token(token)
    except jwt.PyJWTError:
        await websocket.close(code=1008)
        return

    # 2. Check that the user and board exist, and grab the current content
    with SessionLocal() as db:
        user = db.get(models.User, user_id)
        board = db.get(models.Board, board_id)
        current_content = board.content if board else None
    if not user or current_content is None:
        await websocket.close(code=1008)
        return

    # 3. Let them in and send the saved content
    await manager.connect(board_id, websocket)
    await websocket.send_text(json.dumps({"type": "init", "content": current_content}))

    # 4. Listen for edits
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                continue

            if data.get("type") == "update" and isinstance(data.get("content"), str):
                save_content(board_id, data["content"])
                await manager.broadcast(board_id, raw, sender=websocket)
    except WebSocketDisconnect:
        manager.disconnect(board_id, websocket)