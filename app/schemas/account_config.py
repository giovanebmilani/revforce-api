from pydantic import BaseModel

# não sei se é o certo importar o account type aqui
# mas como ele é apenas um enum acho que não tem problema
from app.models.account_config import AccountType

class AccountConfigRequest(BaseModel):
    account_id: str
    type: AccountType
    api_secret: str
    api_id: str
    access_token: str

