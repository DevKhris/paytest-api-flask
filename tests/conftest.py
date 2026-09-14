import os
import uuid
import pytest
from decimal import Decimal

os.environ.setdefault("FLASK_ENV", "testing")
os.environ.setdefault("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/paytest_test")


@pytest.fixture(scope="session")
def app():
    from app import create_app
    from app.extensions import db

    app = create_app("testing")

    with app.app_context():
        db.create_all()
        _seed_room_codes(db)
        yield app
        db.drop_all()


def _seed_room_codes(db):
    from app.models.room_code import RoomCode

    valid_codes = ["TRAINING01", "TRAINING02", "TRAINING03"]
    for code in valid_codes:
        existing = RoomCode.query.filter_by(code=code).first()
        if not existing:
            db.session.add(RoomCode(code=code, is_used=False))
    db.session.commit()


@pytest.fixture(scope="function")
def db_session(app):
    from app.extensions import db

    with app.app_context():
        yield db.session
        db.session.rollback()


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()


@pytest.fixture(scope="function")
def auth_headers(app, client, db_session):
    from app.services.auth_service import AuthService

    with app.app_context():
        auth_service = AuthService()

        user, token_data = auth_service.register(
            name="Test User",
            password="password123",
            room_code="TRAINING01",
        )

        headers = {
            "Authorization": f"Bearer {token_data['access_token']}",
            "Content-Type": "application/json",
        }

        return headers, user


@pytest.fixture(scope="function")
def sample_user(app, db_session):
    from app.models.user import User
    from app.utils.hash import HashUtil
    from app.utils.id_generator import IDGenerator

    with app.app_context():
        user = User(
            id=IDGenerator().generate_unique_id(),
            name="Sample User",
            password_hash=HashUtil().hash_password("password123"),
        )
        db_session.add(user)
        db_session.commit()

        return user


@pytest.fixture(scope="function")
def sample_account(app, db_session, sample_user):
    from app.models.account import Account
    from app.utils.id_generator import IDGenerator

    with app.app_context():
        account = Account(
            id=IDGenerator().generate_idempotency_key()[:16],
            user_id=sample_user.id,
        )
        db_session.add(account)
        db_session.commit()

        return account


@pytest.fixture(scope="function")
def sample_transaction(app, db_session, sample_account):
    from app.models.transaction import Transaction, TransactionType
    from app.utils.id_generator import IDGenerator

    with app.app_context():
        transaction = Transaction(
            id=IDGenerator().generate_idempotency_key()[:16],
            account_id=sample_account.id,
            type=TransactionType.INCOME,
            amount=Decimal("500.00"),
            idempotency_key=IDGenerator().generate_idempotency_key(),
            description="Sample transaction",
        )
        db_session.add(transaction)
        db_session.commit()

        return transaction
