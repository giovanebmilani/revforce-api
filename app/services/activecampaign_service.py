import requests, os
from typing import Any, Dict, List, Optional

API_URL = os.getenv("ACTIVE_CAMPAIGN_API_URL")
API_KEY = os.getenv("ACTIVE_CAMPAIGN_API_KEY")

headers = {
    "Api-Token": API_KEY,
    "Content-Type": "application/json"
}

def get_campaigns() -> List[Dict[str, Any]]:
        try:
            res = requests.get(f"{API_URL}/api/3/campaigns", headers=headers)
            res.raise_for_status()
            return res.json().get("campaigns", [])
        except Exception as e:
            print(f"Erro ao buscar campanhas: {e}")
            return []

def get_campaign_report(campaign_id: str) -> Optional[Dict[str, Any]]:
    try:
        res = requests.get(f"{API_URL}/api/3/campaigns/{campaign_id}/report", headers=headers)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"Erro ao buscar relatório da campanha {campaign_id}: {e}")
        return {}

def get_campaign_links(campaign_id: str) -> List[Dict[str, Any]]:
    try:
        response = requests.get(
            f"{API_URL}/api/3/campaigns/{campaign_id}/links",
            headers=headers
        )
        response.raise_for_status()
        data = response.json()
        return data.get("links", [])
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar links da campanha {campaign_id}: {e}")
        return []

def get_contacts() -> List[Dict[str, Any]]:
    try:
        res = requests.get(f"{API_URL}/api/3/contacts", headers=headers)
        res.raise_for_status()
        return res.json().get("contacts", [])
    except Exception as e:
        print(f"Erro ao buscar contatos: {e}")
        return []

def get_deals() -> List[Dict[str, Any]]:
    try:
        res = requests.get(f"{API_URL}/api/3/deals", headers=headers)
        res.raise_for_status()
        return res.json().get("deals", [])
    except Exception as e:
        print(f"Erro ao buscar deals: {e}")
        return []

def get_contact_activities() -> List[Dict[str, Any]]:
    try:
        res = requests.get(f"{API_URL}/api/3/activities", headers=headers)
        res.raise_for_status()
        return res.json().get("activity", [])
    except Exception as e:
        print(f"Erro ao buscar atividades: {e}")
        return []
