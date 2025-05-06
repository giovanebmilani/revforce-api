import os;
import requests
from typing import Any, Dict, List, Optional
from app.schemas.activecampaign import LeadSchema

API_URL = os.getenv("ACTIVE_CAMPAIGN_API_URL")
API_KEY = os.getenv("ACTIVE_CAMPAIGN_API_KEY")

headers = {
    "Api-Token": API_KEY,
    "Content-Type": "application/json"
}

def search_contacts() -> Optional[Dict[str, Any]]:
    try:
        response = requests.get(f"{API_URL}/api/3/contacts", headers=headers)
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
            name=contato.get("firstName"),
            email=contato.get("email"),
            phone=contato.get("phone")
        )
        leads.append(lead)

    return leads