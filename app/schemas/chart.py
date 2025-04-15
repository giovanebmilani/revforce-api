from pydantic import BaseModel,Field,ValidationError,field_validator

from app.models.chart import ChartMetric, ChartSegment, ChartType

class ChartRequest(BaseModel):
    id: str
    account_id: str
    name: str = Field(min_length=3)
    type: ChartType
    metric: ChartMetric
    period: str
    granularity: str
    source: str
    segment: ChartSegment

    @field_validator('account_id')
    @classmethod
    def check_account_id(cls, v: str) -> str:
        if v is None:
            raise ValueError('Account id não deve ser nulo')
        elif v == "":
            raise ValueError('Account id não deve ser vazio')
        elif not v.isdigit():
            raise ValueError('Account id deve ser um número inteiro positivo')
        v_int = int(v)
        if v_int<1:
            raise ValueError('Account id deve ser valor inteiro maior que zero')
        return v
        
    @field_validator('type')
    @classmethod
    def check_type(cls, v: ChartType) -> ChartType:
        if v not in ChartType:
            raise ValueError('O tipo de gráfico não é válido')
        return v
        
    @field_validator('metric')
    @classmethod
    def check_type(cls, v: ChartMetric) -> ChartMetric:
        if v not in ChartMetric:
            raise ValueError('A métrica do gráfico não é válida')
        return v
    
    @field_validator('period')
    @classmethod
    def check_period(cls, v: str) -> str:
        if v is None:
            raise ValueError('Período não deve ser nulo')
        elif v == "":
            raise ValueError('Período não deve ser vazio')
        elif not v.isdigit():
            raise ValueError('Período deve ser um número inteiro positivo')
        v_int = int(v)
        if v_int<1:
            raise ValueError('Período deve ser um valor inteiro maior que zero')
        return v

    @field_validator('source')
    @classmethod
    def check_source(cls, v: str) -> str:
        if v is None:
            raise ValueError('Source não deve ser nulo')
        elif v == "":
            raise ValueError('Source não deve ser vazio')
        elif not v.isdigit():
            raise ValueError('Source deve ser um número inteiro positivo')
        v_int = int(v)
        if v_int<1:
            raise ValueError('Source deve ser um valor inteiro maior que zero')
        return v
    
    @field_validator('segment')
    @classmethod
    def check_segment(cls, v: ChartSegment) -> ChartSegment:
        if v not in ChartSegment:
            raise ValueError('O segmento do gráfico não é válido')
        return v
