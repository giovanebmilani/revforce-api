from fastapi import APIRouter, Depends
from starlette import status

from app.services.accounts import AccountService
from app.schemas.accounts import AccountRequest

router = APIRouter(
    prefix="/accounts",
    tags=["accounts"]
)


@router.get("/{account_id}", status_code=status.HTTP_200_OK)
async def get_account(account_id: str, service: AccountService = Depends(AccountService.get_service)):
    return await service.get_account(account_id)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_account(account: AccountRequest, service: AccountService = Depends(AccountService.get_service)):
    return await service.create_account(account)

@router.put("/{account_id}", status_code=status.HTTP_200_OK)
async def update_account(account_id: str, account: AccountRequest, service: AccountService = Depends(AccountService.get_service)):
    return await service.update_account(account_id, account)

@router.delete('/{account_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(account_id: str, service: AccountService = Depends(AccountService.get_service)):
    return await service.delete_account(account_id)