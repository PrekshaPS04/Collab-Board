# Collab Board

A real-time collaborative notes app. Multiple users open the same board and see each other's edits live. Built with FastAPI, PostgreSQL, WebSockets, and Redis.

![CI](https://github.com/PrekshaPS04/Collab-Board/actions/workflows/ci.yml/badge.svg)

## Features

- User registration and login with JWT authentication (bcrypt password hashing)
- Boards API: create, list, read, update, and delete, with ownership checks
- Real-time editing over WebSockets; each board is its own room
- Edits are saved to PostgreSQL before they are broadcast
- Redis pub/sub so live updates work across multiple server instances
- Simple browser frontend served by the app
- 16 automated tests (pytest) and CI with GitHub Actions

## Architecture

```
 Browser A ──┐                          ┌── Browser C
             │  WebSocket / REST        │
 Browser B ──┼────────► FastAPI ◄───────┤
             │          server(s)       │
             │           │      │       │
             │           ▼      ▼       │
             │      PostgreSQL  Redis   │
             │      (saved data) (live  │
             │                   sync)  │
```

1. A user logs in and receives a JWT.
2. The browser opens a WebSocket to `/ws/boards/{id}?token=...`.
3. The server verifies the token, then sends the saved board content.
4. When a user edits, the server saves the text to PostgreSQL and publishes it to Redis.
5. Every server instance receives the message from Redis and forwards it to its own connected users, skipping the sender.

## Tech stack

Python, FastAPI, SQLAlchemy, PostgreSQL, Redis, WebSockets, PyJWT, bcrypt, pytest, Docker, GitHub Actions

## Run locally

Requires Python 3.11+ and Docker.

```bash
# 1. Start PostgreSQL and Redis
docker run --name board-db -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=board -p 5433:5432 -d postgres:16
docker run --name board-redis -p 6379:6379 -d redis:7

# 2. Install dependencies
python -m venv venv
venv\Scripts\activate          # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt

# 3. Run the app
uvicorn app.main:app --reload
```

Open http://localhost:8000/app, register, create a board, and open the same board in a second window to see live sync. API docs are at http://localhost:8000/docs.

## Run the tests

```bash
python -m pytest -v
```

Tests use a temporary SQLite database, so they need no Postgres or Redis.

## Design decisions and limitations

- **Save, then broadcast.** The database is the source of truth, so users never see text that was not stored.
- **Redis carries only live updates.** If a message is lost, refreshing restores the saved board.
- **404 instead of 403** for boards you do not own, so board ids are not revealed.
- **Last write wins.** Each edit sends the full text, so simultaneous edits to the same board can overwrite each other. A production editor would use CRDTs or operational transforms.
- **Token in the WebSocket URL**, because browsers cannot set headers on WebSockets. This can appear in server logs.

## Possible improvements

- Per-board member permissions and sharing
- CRDT-based merging of simultaneous edits
- Presence indicators ("2 users online")
- Dockerfile and cloud deployment