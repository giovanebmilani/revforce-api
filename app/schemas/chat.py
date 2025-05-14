import enum

from pydantic import BaseModel, Field

class Role(str, enum.Enum):
    assistant = "assistant"
    user = "user"
    system = "system"

class History(BaseModel):
    role: Role
    content: str

class ChatRequest(BaseModel):
    history: list[History] = Field(default_factory=list)
    question: str
    chart_id: str

class ChatResponse(BaseModel):
    history: list[History]
    response: str

class AssistantIntegration(BaseModel):
    model: str
    messages: list[History]
