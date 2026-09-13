from typing import Optional, List
from decimal import Decimal
from app.models.transaction import Transaction, TransactionType
from app.repositories.base_repository import BaseRepository
from sqlalchemy import func


class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self):
        super().__init__(Transaction)

    def get_by_idempotency_key(self, idempotency_key: str) -> Optional[Transaction]:
        return self.find_by(idempotency_key=idempotency_key)

    def get_by_account_id(self, account_id: str) -> List[Transaction]:
        return self.find_all_by(account_id=account_id)

    def get_by_account_id_paginated(
        self,
        account_id: str,
        page: int = 1,
        per_page: int = 20,
        transaction_type: Optional[TransactionType] = None,
    ) -> tuple[List[Transaction], int]:
        query = self.model.query.filter_by(account_id=account_id)

        if transaction_type:
            query = query.filter_by(type=transaction_type)

        query = query.order_by(self.model.created_at.desc())

        total = query.count()
        transactions = query.offset((page - 1) * per_page).limit(per_page).all()

        return transactions, total

    def calculate_balance(self, account_id: str) -> Decimal:
        income_result = self.db.session.query(
            func.coalesce(func.sum(self.model.amount), 0)
        ).filter(
            self.model.account_id == account_id,
            self.model.type == TransactionType.INCOME
        ).scalar()

        spend_result = self.db.session.query(
            func.coalesce(func.sum(self.model.amount), 0)
        ).filter(
            self.model.account_id == account_id,
            self.model.type == TransactionType.SPEND
        ).scalar()

        return Decimal(str(income_result)) - Decimal(str(spend_result))

    def get_by_related_user_id(self, related_user_id: str) -> Optional[Transaction]:
        return self.find_by(related_user_id=related_user_id)
