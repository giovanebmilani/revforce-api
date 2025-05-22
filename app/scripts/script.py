from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, delete
import random
import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Union

from app.config.database import get_db

from app.models.ad import Ad
from app.models.ad_metric import AdMetric, DeviceType
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


def random_date(start: Union[str, datetime], end: Union[str, datetime], date_format="%Y-%m-%d") -> datetime:
    if isinstance(start, str):
        start = datetime.strptime(start, date_format)
    if isinstance(end, str):
        end = datetime.strptime(end, date_format)

    delta = end - start
    random_days = random.randint(0, delta.days)
    return start + timedelta(days=random_days)


async def populate_db(
    db: AsyncSession = Depends(get_db),
    campaign_count: int = 10,
    min_campaign_start: str = "2024-01-01",
    max_campaign_start: str = "2025-04-01",
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
            api_secret="invalid secret test only",
            last_refresh=datetime.now()
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
            api_secret="invalid secret test only",
            last_refresh=datetime.now()
        )
        db.add(google)

    # Clean up existing campaigns and ads
    await db.execute(delete(AdMetric))
    await db.execute(delete(Ad))
    await db.execute(delete(Campaign))


    # Insert campaigns
    integrations = [meta.id, google.id]

    for _ in range(campaign_count):
        start = random_date(min_campaign_start, max_campaign_start)
        end = random_date(start, datetime.now())

        campaign = Campaign(
            id=str(uuid.uuid4()),
            remote_id="random remote id for test",
            integration_id=random.choice(integrations),
            name=generate_campaign_name(),
            start_date=start,
            end_date=end,
            daily_budget=random.randint(10, 500),
            monthly_budget=random.randint(100, 1000),
        )
        db.add(campaign)

    await db.commit()

    campaigns = await db.scalars(select(Campaign))

    # Insert ads

    ads_created = 0

    for campaign in campaigns:
        num_ads = random.randint(min_ad_per_campaign, max_ad_per_campaign)

        for _ in range(num_ads):
            ads_created += 1
            ad = Ad(
                id=str(uuid.uuid4()),
                remote_id="random ad remote id",
                integration_id=campaign.integration_id,
                campaign_id=campaign.id,
                name=generate_ad_name(),
                created_at=random_date(campaign.start_date, campaign.end_date),
            )
            db.add(ad)

    await db.commit()

    # Insert ad metrics
    ads = await db.scalars(select(Ad).join(Ad.campaign))

    metrics_created = 0

    for ad in ads:
        start = ad.created_at
        end = ad.campaign.end_date

        curr = start

        while curr < end:
            curr += timedelta(hours=4) # 6 every day

            metrics_created += 1
            ad_metric = AdMetric(
                id=str(uuid.uuid4()),
                ad_id=ad.id,
                ctr=random.randint(1, 100),
                impressions=random.randint(50, 10000),
                views=random.randint(10, 5000),
                spend=random.randint(10, 50),
                device=random.choice(list(DeviceType)),
                date=curr,
                hour=curr.hour,
                day=curr.day,
                month=curr.month,
                year=curr.year,
            )
            db.add(ad_metric)

    await db.commit()

    print(f"Created {metrics_created} metrics for {ads_created} ads between {campaign_count} campaings")


async def main():
    async for db in get_db():
        await populate_db(db)


if __name__ == "__main__":
    asyncio.run(main())