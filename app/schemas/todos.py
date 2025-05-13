from pydantic import BaseModel, Field


class TodoRequest(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=100)
    priority: int = Field(gt=0, lt=10, default=0)
    completed: bool = Field(default=False)
