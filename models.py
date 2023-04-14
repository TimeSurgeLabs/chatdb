from typing import Optional
from datetime import datetime

from pydantic import BaseModel
from sqlmodel import SQLModel, Field


class Entry(SQLModel, table=True):
    __tablename__ = "entries"
    id: Optional[int] = Field(default=None, primary_key=True)
    data: str
    user_id: str
    created_at: Optional[datetime] = Field(default_factory=datetime.now)


class EntryReq(BaseModel):
    data: str


class SearchReq(BaseModel):
    query: str
