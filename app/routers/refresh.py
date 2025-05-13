from fastapi import APIRouter, Depends
from starlette import status

from app.schemas.refresh import RefreshRequest
from app.services.refresh import RefreshService

router = APIRouter(
    prefix="/refresh",
    tags=["refresh"]
)


@router.get("/{account_id}", status_code=status.HTTP_200_OK)
async def get_refresh_time(account_id: str, service: RefreshService = Depends(RefreshService.get_service)):
    return await service.get_refresh_time(account_id)


@router.post("", status_code=status.HTTP_200_OK)
async def refresh(refresh_data: RefreshRequest, service: RefreshService = Depends(RefreshService.get_service)):
    return await service.refresh(refresh_data)
