from pydantic import BaseModel
from datetime import datetime

class EventRequest(BaseModel):
    chart_id: str
    name: str 
    description: str 
    date: datetime
    color: str

class EventResponse(BaseModel):
    id: str
    chart_id: str
    name: str 
    description: str 
    date: datetime
    color: str