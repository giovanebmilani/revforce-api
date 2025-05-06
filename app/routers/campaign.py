from fastapi import APIRouter, Depends
from starlette import status

from app.repositories.campaign import CampaignRepository

router = APIRouter(
    prefix="/campaigns",
    tags=["campaigns"]
)


@router.get("/{account_id}/all", status_code=status.HTTP_200_OK)
async def get_campaigns(account_id: str, repository: CampaignRepository = Depends(CampaignRepository.get_service)):
    return await repository.index(account_id)
