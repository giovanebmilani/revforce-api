import logging

from fastapi import Depends, HTTPException
from starlette import status

from app.schemas.chart import ChartDataPointToAnalyze, ChartToAnalyze
from app.schemas.chat import ChatRequest, History, Role, ChatResponse, AssistantIntegration
from app.schemas.event import EventToAnalyze
from app.services.charts import ChartService
from app.services.event import EventService
from app.services.openai_module import OpenAIService


class ChatService:
    def __init__(self, chart_service: ChartService, openai_service: OpenAIService, event_service: EventService):
        self.__chart_service = chart_service
        self.__openai_service = openai_service
        self.__event_service = event_service

    async def chat(self, chat_data: ChatRequest):
        logger = logging.getLogger(__name__)

        chart_data = await self.__chart_service.get_chart(chat_data.chart_id)

        event_data = await self.__event_service.list_events(chart_data.chart.id)

        history = chat_data.history

        if not history:
            data_to_analyze = []

            for data in chart_data.data:
                data_to_analyze.append(
                    ChartDataPointToAnalyze(
                        source_table=data.source_table,
                        value=data.value,
                        date=data.date,
                        device=data.device
                    )
                )

            events_to_analyze = []

            for event in event_data:
                events_to_analyze.append(
                    EventToAnalyze(
                        name=event.name,
                        description=event.description,
                        date=event.date
                    )
                )

            chart_to_analyze = ChartToAnalyze(
                name=chart_data.chart.name,
                type=chart_data.chart.type,
                metric=chart_data.chart.metric,
                period=chart_data.chart.period,
                granularity=chart_data.chart.granularity,
                segment=chart_data.chart.segment,
                data=data_to_analyze,
                events=events_to_analyze
            )


            system_instructions = History(
                role=Role.system,
                content="Você é um assistente especializado em análise de dados de marketing digital. "
                        "O usuário verá um gráfico interativo ao lado deste chat, e poderá fazer perguntas sobre esse gráfico. "
                        "Sempre responda com base nos dados em json fornecidos a seguir: \n" + chart_to_analyze.json()

            )

            history.append(system_instructions)

        question = History(role=Role.user, content=chat_data.question)

        history.append(question)

        assistant_integration_data = AssistantIntegration(
            model="gpt-4.1",
            messages=history
        )

        print(assistant_integration_data)

        try:
            assistant_response = await self.__openai_service.chat_gpt(assistant_integration_data)
        except Exception as e:
            logger.error(f"error communicating with ai service: {str(e)}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="error communicating with ai service")

        history.append(History(role=Role.assistant, content=assistant_response))

        return ChatResponse(history=history, response=assistant_response)

    async def chat_assistant(self, chat_data: ChatRequest):
        logger = logging.getLogger(__name__)

        chart_data = await self.__chart_service.get_chart(chat_data.chart_id)

        history = chat_data.history

        if not history:
            data_to_analyze = []

            for data in chart_data.data:
                data_to_analyze.append(
                    ChartDataPointToAnalyze(
                        source_table=data.source_table,
                        value=data.value,
                        date=data.date,
                        device=data.device
                    )
                )

            chart_to_analyze = ChartToAnalyze(
                name=chart_data.chart.name,
                type=chart_data.chart.type,
                metric=chart_data.chart.metric,
                period=chart_data.chart.period,
                granularity=chart_data.chart.granularity,
                segment=chart_data.chart.segment,
                data=data_to_analyze
            )

            system_instructions = History(
                role=Role.system,
                content="Você é um assistente especializado em análise de dados de marketing digital. "
                        "O usuário verá um gráfico interativo ao lado deste chat, e poderá fazer perguntas sobre esse gráfico. "
                        "Sempre responda com base nos dados fornecidos a seguir: \n" + chart_to_analyze.json()

            )

            history.append(system_instructions)

        question = History(role=Role.user, content=chat_data.question)

        history.append(question)

        assistant_integration_data = AssistantIntegration(
            model="gpt-4.1",
            messages=history
        )

        try:
            assistant_response = await self.__openai_service.assistant_chat(assistant_integration_data)
        except Exception as e:
            logger.error(f"error communicating with ai service: {str(e)}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="error communicating with ai service")

        history.append(History(role=Role.assistant, content=assistant_response))

        return ChatResponse(history=history, response=assistant_response)

    @classmethod
    async def get_service(cls,
                          chart_service: ChartService = Depends(ChartService.get_service),
                          openai_service: OpenAIService = Depends(OpenAIService.get_service),
                          event_service: EventService = Depends(EventService.get_service)
                          ):
        return cls(chart_service, openai_service, event_service)
