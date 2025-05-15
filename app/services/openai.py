from openai import OpenAI
import json

from app.config.application import settings
from app.schemas.chat import AssistantIntegration

client = OpenAI(api_key=settings.OPENAI_KEY)

class OpenAIService:
    async def chat_gpt(self, assist: AssistantIntegration):
        response = client.responses.create(
            model=assist.model,
            input=assist.messages
        )

        return response.output_text

    @classmethod
    async def get_service(cls):
        return cls()
