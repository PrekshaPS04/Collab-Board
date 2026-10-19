from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from .database import Base, engine
from . import models
from .manager import manager
from .routers import users, boards, ws

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await manager.start()
    yield
    await manager.stop()


app = FastAPI(title="Collab Board", lifespan=lifespan)
app.include_router(users.router)
app.include_router(boards.router)
app.include_router(ws.router)

FRONTEND = Path(__file__).resolve().parent.parent / "static" / "index.html"


@app.get("/")
def home():
    return {"message": "Collab Board is running"}


@app.get("/app")
def frontend():
    return FileResponse(FRONTEND)