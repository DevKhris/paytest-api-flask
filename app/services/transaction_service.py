import logging
from decimal import Decimal
from typing import Dict, Any, Optional

from app.extensions import db
from app.models.user import User
from app.repositories.account_repository import AccountRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.user_repository import UserRepository
from app.utils.id_generator import IDGenerator
from app.exceptions.business_exceptions import (
    AccountNotFoundError,
    InsufficientBalanceError,
    InvalidAmountError,
    RecipientNotFoundError,
    DuplicateTransactionError,
)

logger = logging.getLogger(__name__)


class TransactionService:
    def __init__(self):
        self.account_repo = AccountRepository()
        self.transaction_repo = TransactionRepository()
        self.user_repo = UserRepository()
        self.id_generator = IDGenerator()

    def get_transactions(
        self,
        user: User,
        page: int = 1,
        per_page: int = 20,
    ) -> Dict[str, Any]:
        account = self.account_repo.get_by_user_id(user.id)
        if not account:
            raise AccountNotFoundError("Account not found")

        transactions, total = self.transaction_repo.get_by_account_id_paginated(
            account_id=account.id,
            page=page,
            per_page=per_page,
        )

        return {
            "transactions": [t.to_dict() for t in transactions],
            "total": total,
            "page": page,
            "per_page": per_page,
        }

    def transfer(
        self,
        sender: User,
        toUserId: str,
        amount: Decimal,
        idempotency_key: str,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        existing = self.transaction_repo.get_by_idempotency_key(idempotency_key)
        if existing:
            logger.info(f"Idempotent transaction returned: {idempotency_key}")
            sender_account = self.account_repo.get_by_user_id(sender.id)
            recipient_user = self.user_repo.get_by_id(toUserId)
            recipient_account = self.account_repo.get_by_user_id(recipient_user.id) if recipient_user else None
            sender_balance_after = self.transaction_repo.calculate_balance(sender_account.id) if sender_account else "0"
            recipient_balance_after = self.transaction_repo.calculate_balance(recipient_account.id) if recipient_account else "0"
            return {
                "transaction_id": existing.id,
                "amount": f"{existing.amount:.2f}",
                "toUserId": toUserId,
                "sender_balance_after": f"{sender_balance_after:.2f}",
                "recipient_balance_after": f"{recipient_balance_after:.2f}",
                "status": "completed",
            }

        if amount <= 0:
            raise InvalidAmountError("Transfer amount must be greater than zero")

        if amount.is_nan() or amount.is_infinite():
            raise InvalidAmountError("Invalid amount: NaN or infinite")

        recipient_user = self.user_repo.get_by_id(toUserId)
        if not recipient_user:
            raise RecipientNotFoundError(f"Recipient with ID {toUserId} not found")

        if sender.id == toUserId:
            raise InvalidAmountError("Cannot transfer to yourself")

        sender_account = self.account_repo.get_by_user_id(sender.id)
        if not sender_account:
            raise AccountNotFoundError("Sender account not found")

        recipient_account = self.account_repo.get_by_user_id(recipient_user.id)
        if not recipient_account:
            raise AccountNotFoundError("Recipient account not found")

        sender_balance = self.transaction_repo.calculate_balance(sender_account.id)
        if sender_balance < amount:
            logger.warning(
                f"Insufficient balance for user {sender.id}: "
                f"balance={sender_balance}, requested={amount}"
            )
            raise InsufficientBalanceError(
                f"Insufficient balance. Available: {sender_balance}, Requested: {amount}"
            )

        try:
            spend_idempotency_key = self.id_generator.generate_idempotency_key()
            spend_transaction = self.transaction_repo.create(
                account_id=sender_account.id,
                type=TransactionType.SPEND,
                amount=amount,
                idempotency_key=spend_idempotency_key,
                related_user_id=toUserId,
                description=f"Transfer to {toUserId}" + (f": {description}" if description else ""),
            )
            logger.info(f"SPEND transaction created: {spend_transaction.id}")

            request_idempotency_key = self.id_generator.generate_idempotency_key()
            request_transaction = self.transaction_repo.create(
                account_id=recipient_account.id,
                type=TransactionType.INCOME,
                amount=amount,
                idempotency_key=request_idempotency_key,
                related_user_id=sender.id,
                description=f"Transfer from {sender.id}" + (f": {description}" if description else ""),
            )
            logger.info(f"INCOME transaction created: {request_transaction.id}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Transfer failed, rolled back: {str(e)}")
            raise

        sender_balance_after = self.transaction_repo.calculate_balance(sender_account.id)
        recipient_balance_after = self.transaction_repo.calculate_balance(recipient_account.id)

        return {
            "transaction_id": spend_transaction.id,
            "amount": f"{amount:.2f}",
            "toUserId": toUserId,
            "sender_balance_after": f"{sender_balance_after:.2f}",
            "recipient_balance_after": f"{recipient_balance_after:.2f}",
            "status": "completed",
        }
