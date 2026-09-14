import uuid
import random
import string
from decimal import Decimal
from datetime import datetime, timedelta


def _generate_id(length: int) -> str:
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choices(chars, k=length))


class UserFactory:
    @staticmethod
    def create(
        unique_id=None,
        name="Test User",
        password_hash="hashed_password",
    ):
        from app.models.user import User

        return User(
            id=unique_id or _generate_id(12),
            name=name,
            password_hash=password_hash,
        )


class AccountFactory:
    @staticmethod
    def create(user_id=None):
        from app.models.account import Account

        return Account(
            id=_generate_id(16),
            user_id=user_id or _generate_id(12),
        )


class TransactionFactory:
    @staticmethod
    def create(
        account_id=None,
        transaction_type="INCOME",
        amount=Decimal("100.00"),
        idempotency_key=None,
        description=None,
    ):
        from app.models.transaction import Transaction, TransactionType

        return Transaction(
            id=_generate_id(16),
            account_id=account_id or _generate_id(16),
            type=TransactionType[transaction_type],
            amount=amount,
            idempotency_key=idempotency_key or uuid.uuid4().hex,
            description=description,
        )


class ContactFactory:
    @staticmethod
    def create(owner_id=None, contact_user_id=None):
        from app.models.contact import Contact

        return Contact(
            owner_id=owner_id or str(uuid.uuid4())[:12],
            contact_user_id=contact_user_id or str(uuid.uuid4())[:12],
        )


class SessionFactory:
    @staticmethod
    def create(
        user_id=None,
        token="test_token",
        ip_address="127.0.0.1",
        status="ACTIVE",
        expires_hours=24,
    ):
        from app.models.session import Session

        return Session(
            user_id=user_id or str(uuid.uuid4())[:12],
            token=token,
            ip_address=ip_address,
            user_agent="Test Client",
            status=status,
            expires_at=datetime.utcnow() + timedelta(hours=expires_hours),
        )
