from fastapi import APIRouter, Depends
from starlette import status

from app.repositories.ad import AdRepository

router = APIRouter(
    prefix="/ads",
    tags=["ads"]
)


@router.get("/{account_id}/all", status_code=status.HTTP_200_OK)
async def get_ads(account_id: str, repository: AdRepository = Depends(AdRepository.get_service)):
    return await repository.index(account_id)

