from pydantic import BaseModel

class AccountRequest(BaseModel):
    name: str
    
