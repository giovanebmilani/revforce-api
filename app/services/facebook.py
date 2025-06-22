import traceback
from logging import info, error

from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.api import FacebookAdsApi
from fastapi import Depends

from app.models.ad import Ad as AdModel
from app.models.ad_metric import AdMetric
from app.models.campaign import Campaign as CampaignModel
from app.repositories.account_config import AccountConfigRepository
from app.repositories.ad import AdRepository
from app.repositories.ad_metric import AdMetricRepository
from app.repositories.campaign import CampaignRepository


class MetaAdsService:
    def __init__(self,
                 campaign_repository: CampaignRepository,
                 account_config_repository: AccountConfigRepository,
                 ad_repository: AdRepository,
                 ad_metrics_repository: AdMetricRepository):
        self.__campaign_repository = campaign_repository
        self.__account_config_repository = account_config_repository
        self.__ad_repository = ad_repository
        self.__ad_metrics_repository = ad_metrics_repository

    async def refresh_data(self):
        facebookConfigs = await self.__account_config_repository.get_by_type('facebook_ads')
        FacebookAdsApi.init(facebookConfigs.api_id, facebookConfigs.api_secret, facebookConfigs.access_token)

        info('MetaAdsService refreh_data starting')
        campaign_fields = [Campaign.Field.id,
                           Campaign.Field.name,
                           Campaign.Field.start_time,
                           Campaign.Field.stop_time,
                           Campaign.Field.daily_budget]

        try:
            for campaign in AdAccount(facebookConfigs.account_id).get_campaigns(fields=campaign_fields):
                campaign_aux = campaign.export_all_data()
                campaign_model = CampaignModel(
                    remote_id=campaign_aux.get('id'),
                    integration_id=facebookConfigs.id,
                    name=campaign_aux.get('name'),
                    start_date=campaign_aux.get('start_time'),
                    end_date=campaign_aux.get('stop_time'),
                    daily_budget=campaign_aux.get('daily_budget'),
                    monthly_budget=None)

                campaign_model = await self.__campaign_repository.create_or_update(campaign_model)
                await self.get_ads(campaign_model)
        except Exception as e:
            error(f"MetaAdsService exception: {traceback.format_exc()}")

        info('MetaAdsService refreh_data finished')

    async def get_ads(self, campaign):
        info('MetaAdsService get_ads starting')
        campaign_obj = Campaign(campaign.remote_id)
        ad_fields = [
            Ad.Field.id,
            Ad.Field.name,
            Ad.Field.created_time
        ]
        for ad in campaign_obj.get_ads(fields=ad_fields):
            ad_aux = ad.export_all_data()
            ad_model = AdModel(remote_id=ad_aux.get('id'),
                               integration_id=campaign.integration_id,
                               campaign_id=campaign.id,
                               name=ad_aux.get('name'),
                               created_at=ad_aux.get('created_time'),
                               campaign=campaign)

            ad_model = await self.__ad_repository.create_or_update(ad_model)
            await self.get_insights(ad_model)

        info('MetaAdsService get_ads finished')

    async def get_insights(self, ad):
        info('MetaAdsService get_insights starting')
        ad_obj = Ad(ad.remote_id)
        fields = [
            'impressions',
            'reach',
            'clicks',
            'ctr',
            'date_stop'
        ]
        params = {
            'breakdowns': ['device_platform'],
            'date_preset': 'last_year',
            'time_increment': 1
        }
        insights = ad_obj.get_insights(fields=fields, params=params)

        for insight in insights:
            ad_metrics_model = AdMetric.from_raw(ad_id=ad.id,
                                                 ctr=insight.get('ctr'),
                                                 impressions=insight.get('impressions'),
                                                 views=insight.get('reach'),
                                                 clicks=insight.get('clicks'),
                                                 device=insight.get('device_platform'),
                                                 date_raw=insight.get('date_stop')
                                                 )
            await self.__ad_metrics_repository.create_or_update(ad_metrics_model)

        info('MetaAdsService get_insights finished')

    @classmethod
    async def get_service(cls,
                          campaign_repository: CampaignRepository = Depends(CampaignRepository.get_service),
                          account_config_repository: AccountConfigRepository = Depends(
                              AccountConfigRepository.get_service),
                          ad_repository: AdRepository = Depends(AdRepository.get_service),
                          ad_metrics_repository: AdMetricRepository = Depends(AdMetricRepository.get_service)):
        return cls(campaign_repository, account_config_repository, ad_repository, ad_metrics_repository)
