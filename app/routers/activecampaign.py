from fastapi import APIRouter
from app.services.activecampaign_service import buscar_contatos, traduzir_contatos

router = APIRouter(
    prefix="/activecampaign",
    tags=["ActiveCampaign"]
)

@router.get("/leads")
def get_leads():
    dados = buscar_contatos()
    if not dados:
        return {"error": "Erro ao buscar dados do ActiveCampaign"}
    leads = traduzir_contatos(dados)
    return leads
