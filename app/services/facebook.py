from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign



FacebookAdsApi.init(APP_ID, APP_SECRET, ACCESS_TOKEN)

class MetaAdsService:

    async def get_campaigns(self):
        account = AdAccount(AD_ACCOUNT_ID)
        campaigns = account.get_campaigns(fields=[
            Campaign.Field.id,
            Campaign.Field.name,
            Campaign.Field.status,
        ])
        return [campaign.export_all_data() for campaign in campaigns]
    
    @classmethod
    async def get_service(cls):
        return cls()