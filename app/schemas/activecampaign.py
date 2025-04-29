from pydantic import BaseModel
from typing import Optional

class LeadSchema(BaseModel):
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
