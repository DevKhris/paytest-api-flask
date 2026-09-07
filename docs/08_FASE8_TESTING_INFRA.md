# FASE 8: Testing Infrastructure

## 8.1 Estructura de Testing

```
tests/
├── __init__.py
├── conftest.py              # Fixtures pytest
├── fixtures/
│   ├── __init__.py
│   └── factories.py         # Factories para crear datos de prueba
├── unit/
│   ├── __init__.py
│   └── services/
│       └── __init__.py      # Tests unitarios de servicios (placeholder)
└── integration/
    ├── __init__.py
    └── controllers/
        └── __init__.py      # Tests de integración (placeholder)
```

---

## 8.2 requirements.txt (Testing Dependencies)

```txt
flask>=3.1,<4
flask-cors>=6.0,<7
flask-sqlalchemy>=3.1,<4
flask-migrate>=4.0,<5
sqlalchemy>=2.0,<3
psycopg2-binary>=2.9,<3
pyjwt>=2.10,<3
python-dotenv>=1.0,<2
marshmallow>=3.20,<4
bcrypt>=4.1,<5

pytest>=8.0,<9
pytest-cov>=4.1,<5
pytest-flask>=1.3,<2
```

---

## 8.3 conftest.py - Fixtures Principales

### tests/conftest.py

```python
import os
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
        yield app
        db.drop_all()


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
            unique_id=IDGenerator.generate_unique_id(),
            name="Sample User",
            password_hash=HashUtil.hash_password("password123"),
        )
        db_session.add(user)
        db_session.commit()

        return user


@pytest.fixture(scope="function")
def sample_account(app, db_session, sample_user):
    from app.models.account import Account

    with app.app_context():
        account = Account(user_id=sample_user.id)
        db_session.add(account)
        db_session.commit()

        return account


@pytest.fixture(scope="function")
def sample_transaction(app, db_session, sample_account):
    from app.models.transaction import Transaction, TransactionType
    from app.utils.id_generator import IDGenerator

    with app.app_context():
        transaction = Transaction(
            account_id=sample_account.id,
            type=TransactionType.INCOME,
            amount=Decimal("500.00"),
            idempotency_key=IDGenerator.generate_idempotency_key(),
            description="Sample transaction",
        )
        db_session.add(transaction)
        db_session.commit()

        return transaction
```

---

## 8.4 Factories - factories.py

### tests/fixtures/factories.py

```python
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
            id=str(uuid.uuid4()),
            unique_id=unique_id or f"TEST{uuid.uuid4().hex[:8].upper()}",
            name=name,
            password_hash=password_hash,
            created_at=datetime.utcnow(),
        )


class AccountFactory:
    @staticmethod
    def create(user_id=None):
        from app.models.account import Account

        return Account(
            id=str(uuid.uuid4()),
            user_id=user_id or str(uuid.uuid4()),
            created_at=datetime.utcnow(),
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
            id=str(uuid.uuid4()),
            account_id=account_id or str(uuid.uuid4()),
            type=TransactionType[transaction_type],
            amount=amount,
            idempotency_key=idempotency_key or str(uuid.uuid4()),
            description=description,
            created_at=datetime.utcnow(),
        )


class ContactFactory:
    @staticmethod
    def create(owner_user_id=None, contact_user_id=None):
        from app.models.contact import Contact

        return Contact(
            id=str(uuid.uuid4()),
            owner_user_id=owner_user_id or str(uuid.uuid4()),
            contact_user_id=contact_user_id or str(uuid.uuid4()),
            created_at=datetime.utcnow(),
        )


class SessionFactory:
    @staticmethod
    def create(
        user_id=None,
        token="test_token",
        ip_address="127.0.0.1",
        is_active=True,
        expires_hours=24,
    ):
        from app.models.session import Session

        return Session(
            id=str(uuid.uuid4()),
            user_id=user_id or str(uuid.uuid4()),
            token=token,
            ip_address=ip_address,
            user_agent="Test Client",
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=expires_hours),
            is_active=is_active,
        )
```

---

## 8.5 tests/__init__.py y fixtures/__init__.py

### tests/__init__.py

```python
# Tests package
```

### tests/fixtures/__init__.py

```python
from tests.fixtures.factories import (
    UserFactory,
    AccountFactory,
    TransactionFactory,
    ContactFactory,
    SessionFactory,
)

__all__ = [
    "UserFactory",
    "AccountFactory",
    "TransactionFactory",
    "ContactFactory",
    "SessionFactory",
]
```

---

## 8.6 Placeholders para Tests

### tests/unit/__init__.py

```python
# Unit tests package
# Tests to be implemented during training session
```

### tests/unit/services/__init__.py

```python
# Unit tests for services
# Placeholder for:
# - tests/unit/services/test_auth_service.py
# - tests/unit/services/test_account_service.py
# - tests/unit/services/test_transaction_service.py
# - tests/unit/services/test_contact_service.py
```

### tests/integration/__init__.py

```python
# Integration tests package
```

### tests/integration/controllers/__init__.py

```python
# Integration tests for controllers
# Placeholder for:
# - tests/integration/controllers/test_auth_controller.py
# - tests/integration/controllers/test_account_controller.py
# - tests/integration/controllers/test_transaction_controller.py
# - tests/integration/controllers/test_contact_controller.py
```

---

## 8.7 pytest.ini - Configuración de Tests

### pytest.ini (en raíz del proyecto)

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --cov=app --cov-report=html --cov-report=term-missing
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
```

---

## 8.8 Resumen de Archivos de Testing

| Archivo | Descripción |
|---------|-------------|
| `tests/__init__.py` | Package marker |
| `tests/conftest.py` | Fixtures pytest (app, db, client, auth) |
| `tests/fixtures/__init__.py` | Exports de factories |
| `tests/fixtures/factories.py` | Factories para datos de prueba |
| `tests/unit/__init__.py` | Package marker |
| `tests/unit/services/__init__.py` | Placeholder tests unitarios |
| `tests/integration/__init__.py` | Package marker |
| `tests/integration/controllers/__init__.py` | Placeholder tests integración |
| `pytest.ini` | Configuración de pytest |

---

## 8.9 Comandos para Ejecutar Tests

```bash
# Instalar dependencias
pip install -r requirements.txt

# Crear base de datos de test
createdb -U postgres paytest_test

# Ejecutar tests con coverage
pytest --cov=app --cov-report=html

# Ejecutar tests sin coverage
pytest -v

# Ejecutar solo tests unitarios
pytest tests/unit/

# Ejecutar solo tests de integración
pytest tests/integration/

# Ver report de coverage en HTML
open htmlcov/index.html
```

---

## 8.10 Fixtures Disponibles

| Fixture | Scope | Descripción |
|---------|-------|-------------|
| `app` | session | Aplicación Flask configurada para tests |
| `db_session` | function | Sesión de base de datos con rollback |
| `client` | function | Cliente de pruebas Flask |
| `auth_headers` | function | Headers con JWT válido + usuario |
| `sample_user` | function | Usuario de prueba |
| `sample_account` | function | Cuenta de prueba |
| `sample_transaction` | function | Transacción de prueba |

---

## 8.11Factories Disponibles

| Factory | Descripción |
|---------|-------------|
| `UserFactory.create()` | Crea instancia de User |
| `AccountFactory.create()` | Crea instancia de Account |
| `TransactionFactory.create()` | Crea instancia de Transaction |
| `ContactFactory.create()` | Crea instancia de Contact |
| `SessionFactory.create()` | Crea instancia de Session |
