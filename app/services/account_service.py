import logging
from typing import Dict, Any

from app.models.user import User
from app.repositories.account_repository import AccountRepository
from app.repositories.transaction_repository import TransactionRepository
from app.exceptions.business_exceptions import AccountNotFoundError
from app.utils.date_format import format_iso_datetime

logger = logging.getLogger(__name__)


class AccountService:
    def __init__(self):
        self.account_repo = AccountRepository()
        self.transaction_repo = TransactionRepository()

    def get_account_by_user(self, user: User):
        account = self.account_repo.get_by_user_id(user.id)
        if not account:
            raise AccountNotFoundError("Account not found for user")
        return account

    def get_account_by_user_id(self, user_id: str):
        account = self.account_repo.get_by_user_id(user_id)
        if not account:
            raise AccountNotFoundError("Account not found")
        return account

    def get_balance(self, user: User) -> Dict[str, Any]:
        account = self.get_account_by_user(user)
        balance = self.transaction_repo.calculate_balance(account.id)

        return {
            "balance": f"{balance:.2f}",
            "currency": "USD",
        }

    def get_account_details(self, user: User) -> Dict[str, Any]:
        account = self.get_account_by_user(user)
        balance = self.transaction_repo.calculate_balance(account.id)

        return {
            "id": account.id,
            "user_id": account.user_id,
            "balance": str(balance),
            "created_at": format_iso_datetime(account.created_at),
        }
