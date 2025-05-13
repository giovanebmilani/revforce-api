from fastapi import APIRouter, Depends
from starlette import status

from app.services.account_config import AccountConfigService
from app.schemas.account_config import AccountConfigRequest

router = APIRouter(
    prefix="/account_config",
    tags=["account_config"]
)


@router.get("/{config_id}", status_code=status.HTTP_200_OK)
async def get_config(config_id: str, service: AccountConfigService = Depends(AccountConfigService.get_service)):
    return await service.get_config(config_id)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_config(config: AccountConfigRequest, service: AccountConfigService = Depends(AccountConfigService.get_service)):
    return await service.create_config(config)

@router.put("/{config_id}", status_code=status.HTTP_200_OK)
async def update_config(config_id: str, config: AccountConfigRequest, service: AccountConfigService = Depends(AccountConfigService.get_service)):
    return await service.update_config(config_id, config)

@router.delete('/{config_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_config(config_id: str, service: AccountConfigService = Depends(AccountConfigService.get_service)):
    return await service.delete_config(config_id)