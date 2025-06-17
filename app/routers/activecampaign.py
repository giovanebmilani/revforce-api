from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import get_db
from app.repositories.contact import ContactRepository
from app.repositories.deal import DealRepository
from app.repositories.message import MessageRepository
from app.repositories.campaign import CampaignRepository
from app.repositories.ad import AdRepository
from app.repositories.ad_metric import AdMetricRepository
from app.services.activecampaign_service import get_campaign_links, get_campaigns, get_campaign_report, get_contacts, get_deals, get_contact_activities
from datetime import datetime, timezone

router = APIRouter(
    prefix="/activecampaign",
    tags=["ActiveCampaign"]
)

@router.post("/sync-campaigns")
async def sync_campaigns(db: AsyncSession = Depends(get_db)):
    campaign_repo = await CampaignRepository.get_service(db)
    ad_repo = await AdRepository.get_service(db)
    ad_metric_repo = await AdMetricRepository.get_service(db)

    api_campaigns = get_campaigns()
    today = datetime.now(timezone.utc)

    for camp in api_campaigns:
        remote_id = camp["id"]
        name = camp.get("name")
        start_date = camp.get("send_date") or camp.get("created_at") or datetime.now(timezone.utc)

        db_campaign = await campaign_repo.get_or_create(remote_id, name, start_date, "activecampaign")

        report = get_campaign_report(remote_id)

        metrics = {
            "ad_id": None,
            "ctr": float(report.get("click_rate", 0)),
            "impressions": int(report.get("total_sent", 0)),
            "views": int(report.get("total_opens", 0)),
            "clicks": int(report.get("total_clicks", 0)),
            "device": "unknown",
            "date": today.date(),
            "hour": today.hour,
            "day": today.day,
            "month": today.month,
            "year": today.year
        }

        await ad_metric_repo.save(db_campaign.id, metrics)

        links = get_campaign_links(remote_id)

        for link in links:
            ad = await ad_repo.get_or_create(link["id"], "activecampaign", db_campaign.id, link["url"])

            metrics_link = {
                "ad_id": ad.id,
                "ctr": 0,  # ou calcular se tiver dado
                "impressions": 0,
                "views": 0,
                "clicks": link.get("clicks", 0),
                "device": "unknown",
                "date": today.date(),
                "hour": today.hour,
                "day": today.day,
                "month": today.month,
                "year": today.year
            }

            await ad_metric_repo.save(db_campaign.id, metrics_link)

    return {"message": "Sincronização concluída!"}

@router.post("/sync-contacts")
async def sync_contacts(db: AsyncSession = Depends(get_db)):
    contact_repo = await ContactRepository.get_service(db)
    contacts = get_contacts()

    for contact in contacts:
        await contact_repo.get_or_create(
            remote_id=contact["id"],
            email=contact.get("email", ""),
            first_name=contact.get("firstName", ""),
            created_at=contact.get("created_timestamp", ""),
            source=contact.get("source", "")
        )

    return {"message": "Contatos sincronizados"}

@router.post("/sync-deals")
async def sync_deals(db: AsyncSession = Depends(get_db)):
    deal_repo = await DealRepository.get_service(db)
    deals = get_deals()

    for deal in deals:
        await deal_repo.get_or_create(
            remote_id=deal["id"],
            data={
                "contact": deal.get("contact", ""),
                "title": deal.get("title", ""),
                "status": deal.get("status", ""),
                "value": deal.get("value", 0),
                "currency": deal.get("currency", "USD"),
                "created_timestamp": deal.get("created_timestamp"),
                "close_date": deal.get("close_date")
            }
        )

    return {"message": "Deals sincronizados"}

@router.post("/sync-messages")
async def sync_messages(db: AsyncSession = Depends(get_db)):
    message_repo = await MessageRepository.get_service(db)
    activities = get_contact_activities()

    for act in activities:
        await message_repo.get_or_create(
            remote_id=act["id"],
            data={
                "contact_id": act.get("contact_id"),
                "activity_type": act.get("activity_type"),
                "campaign_id": act.get("campaign_id"),
                "message_id": act.get("message_id"),
                "timestamp": act.get("timestamp")
            }
        )

    return {"message": "Mensagens sincronizadas"}
