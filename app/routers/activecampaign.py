from fastapi import APIRouter
from app.services.activecampaign_service import search_contacts, translate_contacts

router = APIRouter(
    prefix="/activecampaign",
    tags=["ActiveCampaign"]
)

@router.get("/leads")
def get_leads():
    dados = search_contacts()
    if not dados:
        return {"error": "Erro ao buscar dados do ActiveCampaign"}
    leads = translate_contacts(dados)
    return leads
