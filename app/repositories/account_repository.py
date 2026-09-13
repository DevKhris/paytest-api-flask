from typing import Optional
from app.models.account import Account
from app.repositories.base_repository import BaseRepository


class AccountRepository(BaseRepository[Account]):
    def __init__(self):
        super().__init__(Account)

    def get_by_user_id(self, user_id: str) -> Optional[Account]:
        return self.find_by(user_id=user_id)

    def get_by_user_id_or_raise(self, user_id: str) -> Account:
        account = self.get_by_user_id(user_id)
        if not account:
            raise ValueError(f"Account not found for user {user_id}")
        return account
