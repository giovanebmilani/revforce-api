import time

import openai

from app.config.application import settings
from app.schemas.chat import AssistantIntegration

openai.api_key = settings.OPENAI_KEY


class OpenAIService:
    async def chat_gpt(self, assist: AssistantIntegration):
        response = openai.responses.create(
            model=assist.model,
            input=assist.messages
        )

        return response.output_text

    async def assistant_chat(self, assist: AssistantIntegration):
        # 1. Cria um novo thread
        thread = openai.beta.threads.create()

        # 2. Envia as mensagens para a thread
        for history in assist.messages:
            openai.beta.threads.messages.create(
                thread_id=thread.id,
                role=history.role.lower(),
                content=history.content,
            )

        # 3. Executa o assistant
        run = openai.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=settings.ASSISTANT_ID
        )

        # 4. Aguarda a conclusão da execução
        while True:
            run_status = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            if run_status.status == "completed":
                break
            elif run_status.status in ("failed", "cancelled", "expired"):
                return {"error": f"Run failed: {run_status.status}"}
            time.sleep(1)

        # 5. Busca a resposta
        messages = openai.beta.threads.messages.list(thread_id=thread.id)
        last_message = messages.data[0]  # a última resposta do assistant

        return last_message.content[0].text.value

    @classmethod
    async def get_service(cls):
        return cls()
