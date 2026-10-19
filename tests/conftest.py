import os

# Must be set BEFORE the app is imported, so the app uses SQLite, not Postgres
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, engine


@pytest.fixture(autouse=True)
def clean_db():
    # Safety check: never wipe a real database
    assert engine.url.get_backend_name() == "sqlite"
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client():
    return TestClient(app)