from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, delete
import random
import asyncio
import uuid
from datetime import datetime, timedelta

from app.config.database import get_db

from app.models.ad import Ad
from app.models.account_config import AccountConfig, AccountType
from app.models.account import Account
from app.models.campaign import Campaign


adjectives = [
    "Smart", "NextGen", "Ultimate", "Eco", "Dynamic", "Incredible", "Modern",
    "Effortless", "Pro", "Essential", "Bold", "Instant", "Premium", "Viral"
]

products = [
    "Shoes", "Coffee", "Fitness Plan", "Travel Deal", "Phone Case", "Diet Hack",
    "Skincare Routine", "SaaS Tool", "Meal Box", "Bike", "Headphones", "VPN"
]

goals = [
    "Boost Sales", "Get Clicks", "Convert Now", "Win Customers", "Go Viral",
    "Scale Up", "Dominate Market", "Engage Users", "Drive Traffic", "Generate Leads"
]

emojis = ["🔥", "🚀", "💡", "✨", "💰", "📈", "🛍️", "🎯", "🏆", "💎"]

def generate_campaign_name():
    template = random.choice([
        "{adj} {prod} - {goal}",
        "{goal} with {adj} {prod}",
        "{adj} {prod} Campaign {emoji}",
        "{prod}: {goal} {emoji}"
    ])
    return template.format(
        adj=random.choice(adjectives),
        prod=random.choice(products),
        goal=random.choice(goals),
        emoji=random.choice(emojis)
    )

def generate_ad_name():
    formats = [
        "{adj} Ad #{num}",
        "{adj} {emoji} Creative",
        "Ad Blast {emoji} {num}",
        "{emoji} {adj} Conversion Ad",
        "Ad #{num} - {adj} Impact"
    ]

    num = random.randint(1000, 9999)

    return random.choice(formats).format(
        adj=random.choice(adjectives),
        emoji=random.choice(emojis),
        num=num
    )

def random_date(start: str, end: str, date_format="%Y-%m-%d") -> datetime:
    start_date = datetime.strptime(start, date_format)
    end_date = datetime.strptime(end, date_format)
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    result_date = start_date + timedelta(days=random_days)
    return result_date


async def populate_db(
    db: AsyncSession = Depends(get_db),
    campaign_count: int = 10,
    min_ad_per_campaign: int = 3,
    max_ad_per_campaign: int = 10
):
    acc = await db.scalar(select(Account))

    if acc is None:
        acc = Account(
            id=str(uuid.uuid4()),
            name="Test Account"
        )
        db.add(acc)
        await db.flush()

    # Fetch or create Facebook Ads config
    meta = await db.scalar(
        select(AccountConfig)
        .where(AccountConfig.account_id == acc.id)
        .where(AccountConfig.type == AccountType.facebook_ads)
    )

    if meta is None:
        meta = AccountConfig(
            id=str(uuid.uuid4()),
            account_id=acc.id,
            type=AccountType.facebook_ads,
            api_secret="invalid secret test only"
        )
        db.add(meta)

    # Fetch or create Google Ads config
    google = await db.scalar(
        select(AccountConfig)
        .where(AccountConfig.account_id == acc.id)
        .where(AccountConfig.type == AccountType.google_ads)
    )

    if google is None:
        google = AccountConfig(
            id=str(uuid.uuid4()),
            account_id=acc.id,
            type=AccountType.google_ads,
            api_secret="invalid secret test only"
        )
        db.add(google)

    # Clean up existing campaigns and ads
    await db.execute(delete(Ad))
    await db.execute(delete(Campaign))


    # Insert campaigns
    integrations = [meta.id, google.id]

    for _ in range(campaign_count):
        campaign = Campaign(
            id=str(uuid.uuid4()),
            remote_id="random remote id for test",
            integration_id=random.choice(integrations),
            name=generate_campaign_name(),
            start_date=random_date("2024-01-01", "2025-04-01"),
            end_date=random_date("2024-01-01", "2025-04-01"),
            daily_budget=random.randint(10, 500),
            monthly_budget=random.randint(100, 1000),
        )
        db.add(campaign)

    await db.commit()

    campaigns = await db.scalars(select(Campaign))

    # Insert ads
    for campaign in campaigns:
        num_ads = random.randint(min_ad_per_campaign, max_ad_per_campaign)

        for _ in range(num_ads):
            ad = Ad(
                id=str(uuid.uuid4()),
                remote_id="random ad remote id",
                integration_id=campaign.integration_id,
                campaign_id=campaign.id,
                name=generate_ad_name(),
                created_at=random_date("2024-01-01", "2025-04-01"),
            )
            db.add(ad)

    await db.commit()


async def main():
    async for db in get_db():
        await populate_db(db)


if __name__ == "__main__":
    asyncio.run(main())