from typing import Optional

from pydantic import BaseModel, Field


class ProcessEventCreate(BaseModel):
    host: str = Field(default="localhost", max_length=255)
    event_type: str = Field(default="exec", max_length=32)
    pid: int = Field(ge=0)
    ppid: int = Field(ge=0)
    uid: int = Field(ge=0)
    comm: str = Field(max_length=255)
    filename: Optional[str] = None
    exit_code: Optional[int] = None


class ProcessEvent(ProcessEventCreate):
    id: int
    created_at: str
