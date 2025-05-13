from openai import OpenAI
import json

from app.config.application import settings

client = OpenAI(api_key=settings.OPENAI_KEY)

class OpenAIService:
    async def chat_gpt(self, assist: AssistantIntegration):
        history=assist.messages 

        response = client.responses.create(
            model=assist.model,
            input=assist.messages
        )

        new_message=History(role=Role.assistant, content=response.output_text)
        history.append(new_message)
        return history

    @classmethod
    async def get_service(cls):
        return cls()
