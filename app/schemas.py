from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)

class UserOut(BaseModel):
    id: int
    email: EmailStr

    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class BoardCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)

class BoardOut(BaseModel):
    id: int
    title: str
    content: str
    owner_id: int
    created_at: datetime

    model_config = {"from_attributes": True}

class BoardUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    content: str | None = None