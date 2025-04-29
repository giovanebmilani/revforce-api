import requests
from typing import Any, Dict, List, Optional
from app.schemas.activecampaign import LeadSchema

API_URL = "https://SEU_DOMINIO.api-us1.com/api/3"
API_KEY = "SUA_API_KEY"

headers = {
    "Api-Token": API_KEY,
    "Content-Type": "application/json"
}

def search_contacts() -> Optional[Dict[str, Any]]:
    try:
        response = requests.get(f"{API_URL}/contacts", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar contatos: {e}")
        return None

def translate_contacts(dados_api: dict) -> List[LeadSchema]:
    contatos = dados_api.get("contacts", [])
    leads = []

    for contato in contatos:
        lead = LeadSchema(
            nome=contato.get("firstName"),
            email=contato.get("email"),
            telefone=contato.get("phone")
        )
        leads.append(lead)

    return leads