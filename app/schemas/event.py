from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class EventRequest(BaseModel):
    chart_id: str
    name: str = Field(min_length=3)
    description: str
    date: datetime
    color: str

class EventUpdateRequest(BaseModel):
    name: str = Field(min_length=3)
    description: str
    date: datetime
    color: str


class EventResponse(BaseModel):
    event_id: str
    chart_id: str
    name: str = Field(min_length=3)
    description: str
    date: datetime
    color: str
