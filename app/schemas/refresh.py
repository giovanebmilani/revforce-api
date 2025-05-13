from pydantic import BaseModel, Field


class RefreshRequest(BaseModel):
    account_id: str = Field(min_length=1)


class RefreshResponse(BaseModel):
    next_refresh_time: str
