import httpx
from fastapi import HTTPException, Depends
from httpx import AsyncClient
from starlette import status

from app.config.application import settings, get_http_client


class InsightsService:
    def __init__(self, http_client: AsyncClient):
        self.http_client = http_client

    async def get_insights(self, prompt: str):
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 150
        }

        try:
            response = await self.http_client.post(url, json=data, headers=headers)
            response.raise_for_status()
            result = response.json()
            return {"response": result["choices"][0]["message"]["content"].strip()}
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    @classmethod
    async def get_service(cls, http_client: AsyncClient = Depends(get_http_client)):
        """ Dependency to inject the service into routes """
        return cls(http_client)
