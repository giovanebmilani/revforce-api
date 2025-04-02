from pydantic import BaseModel

# não sei se é o certo importar o account type aqui
# mas como ele é apenas um enum acho que não tem problema
from app.models.account_config import AccountType

class AccountConfigRequest(BaseModel):
    id_user: str
    tipo: AccountType
    chave_api: str

