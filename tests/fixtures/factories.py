import uuid
from decimal import Decimal
from datetime import datetime, timedelta


class UserFactory:
    @staticmethod
    def create(
        unique_id=None,
        name="Test User",
        password_hash="hashed_password",
    ):
        from app.models.user import User

        return User(
            id=unique_id or f"{''.join(__import__('random').choices(__import__('string').ascii_uppercase + __import__('string').digits, k=12))}",
            name=name,
            password_hash=password_hash,
        )


class AccountFactory:
    @staticmethod
    def create(user_id=None):
        from app.models.account import Account

        return Account(
            user_id=user_id or str(uuid.uuid4())[:12],
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
            account_id=account_id or str(uuid.uuid4())[:16],
            type=TransactionType[transaction_type],
            amount=amount,
            idempotency_key=idempotency_key or str(uuid.uuid4()),
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
