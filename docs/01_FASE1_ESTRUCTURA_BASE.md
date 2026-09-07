# FASE 1: Estructura Base del Proyecto

## 1.1 Estructura de Directorios

```
paytest-api-flask/
├── app/
│   ├── __init__.py           # Flask Application Factory
│   ├── config.py             # Configuración por entorno
│   ├── extensions.py         # Extensiones Flask (db, migrate, etc.)
│   ├── models/               # Entidades SQLAlchemy
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── account.py
│   │   ├── transaction.py
│   │   ├── contact.py
│   │   └── session.py
│   ├── repositories/         # Capa de acceso a datos
│   │   ├── __init__.py
│   │   ├── base_repository.py
│   │   ├── user_repository.py
│   │   ├── account_repository.py
│   │   ├── transaction_repository.py
│   │   ├── contact_repository.py
│   │   └── session_repository.py
│   ├── services/            # Lógica de negocio
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── account_service.py
│   │   ├── transaction_service.py
│   │   └── contact_service.py
│   ├── controllers/         # Endpoints/Rutas
│   │   ├── __init__.py
│   │   ├── auth_controller.py
│   │   ├── account_controller.py
│   │   ├── transaction_controller.py
│   │   └── contact_controller.py
│   ├── dto/                 # Data Transfer Objects
│   │   ├── __init__.py
│   │   ├── requests/
│   │   │   ├── __init__.py
│   │   │   ├── auth_dto.py
│   │   │   ├── account_dto.py
│   │   │   ├── transaction_dto.py
│   │   │   └── contact_dto.py
│   │   └── responses/
│   │       ├── __init__.py
│   │       ├── auth_response_dto.py
│   │       ├── account_response_dto.py
│   │       ├── transaction_response_dto.py
│   │       └── contact_response_dto.py
│   ├── utils/               # Utilidades
│   │   ├── __init__.py
│   │   ├── hash.py
│   │   ├── id_generator.py
│   │   ├── idempotency.py
│   │   └── decorators.py
│   └── exceptions/          # Excepciones custom
│       ├── __init__.py
│       └── business_exceptions.py
├── tests/                   # Testing
│   ├── __init__.py
│   ├── conftest.py
│   ├── fixtures/
│   │   ├── __init__.py
│   │   └── factories.py
│   ├── unit/
│   │   └── __init__.py
│   └── integration/
│       └── __init__.py
├── migrations/              # Flask-Migrate
├── docs/                    # Documentación
├── requirements.txt
├── run.py                   # Entry point
└── app.py                   # Main app (actualizar)
```

---

## 1.2 requirements.txt

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
gunicorn>=21.0,<22
```

---

## 1.3 app/config.py

```python
import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-prod"
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or "jwt-secret-key-change-in-prod"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "postgresql://postgres:postgres@localhost:5432/paytest_dev"


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URL"
    ) or "postgresql://postgres:postgres@localhost:5432/paytest_test"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
```

---

## 1.4 app/extensions.py

```python
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
```

---

## 1.5 app/__init__.py (Application Factory)

```python
import logging
from flask import Flask, jsonify

from app.config import config
from app.extensions import db, migrate, cors


def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    configure_logging(app)
    configure_extensions(app)
    configure_error_handlers(app)
    register_blueprints(app)

    return app


def configure_logging(app):
    logging.basicConfig(
        level=app.config["LOG_LEVEL"],
        format=app.config["LOG_FORMAT"],
    )
    app.logger.setLevel(app.config["LOG_LEVEL"])


def configure_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})


def configure_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "Bad Request", "message": str(error)}), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({"error": "Unauthorized", "message": str(error)}), 401

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not Found", "message": str(error)}), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        app.logger.error(f"Internal error: {error}")
        return jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred"}), 500


def register_blueprints(app):
    from app.controllers.auth_controller import auth_bp
    from app.controllers.account_controller import account_bp
    from app.controllers.transaction_controller import transaction_bp
    from app.controllers.contact_controller import contact_bp

    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(account_bp, url_prefix="/api/v1/accounts")
    app.register_blueprint(transaction_bp, url_prefix="/api/v1/transactions")
    app.register_blueprint(contact_bp, url_prefix="/api/v1/contacts")
```

---

## 1.6 run.py

```python
import os
from app import create_app

app = create_app(os.environ.get("FLASK_ENV", "development"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
```

---

## 1.7 app/models/__init__.py

```python
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.contact import Contact
from app.models.session import Session

__all__ = ["User", "Account", "Transaction", "Contact", "Session"]
```

---

## 1.8 Archivos de Models (Placeholders iniciales)

### app/models/user.py
```python
from datetime import datetime
from app.extensions import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True)
    unique_id = db.Column(db.String(12), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    account = db.relationship("Account", back_populates="user", uselist=False)
    sessions = db.relationship("Session", back_populates="user")
    contacts = db.relationship(
        "Contact",
        foreign_keys="Contact.owner_user_id",
        back_populates="owner",
    )

    def __repr__(self):
        return f"<User {self.unique_id}>"
```

### app/models/account.py
```python
from datetime import datetime
from decimal import Decimal
from app.extensions import db

class Account(db.Model):
    __tablename__ = "accounts"

    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="account")
    transactions = db.relationship("Transaction", back_populates="account")

    @property
    def balance(self):
        from app.models.transaction import TransactionType
        from sqlalchemy import func
        
        income = db.session.query(
            func.coalesce(func.sum(Transaction.amount), 0)
        ).filter(
            Transaction.account_id == self.id,
            Transaction.type == TransactionType.INCOME.value
        ).scalar()
        
        spend = db.session.query(
            func.coalesce(func.sum(Transaction.amount), 0)
        ).filter(
            Transaction.account_id == self.id,
            Transaction.type == TransactionType.SPEND.value
        ).scalar()
        
        return Decimal(str(income)) - Decimal(str(spend))

    def __repr__(self):
        return f"<Account {self.id}>"
```

### app/models/transaction.py
```python
from datetime import datetime
from decimal import Decimal
import enum
from app.extensions import db

class TransactionType(enum.Enum):
    INCOME = "INCOME"
    SPEND = "SPEND"
    REQUEST = "REQUEST"


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.String(36), primary_key=True)
    account_id = db.Column(db.String(36), db.ForeignKey("accounts.id"), nullable=False, index=True)
    type = db.Column(db.Enum(TransactionType), nullable=False)
    amount = db.Column(db.Numeric(precision=12, scale=2), nullable=False)
    idempotency_key = db.Column(db.String(64), unique=True, nullable=False, index=True)
    reference_id = db.Column(db.String(36), db.ForeignKey("transactions.id"), nullable=True)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    account = db.relationship("Account", back_populates="transactions")
    reference = db.relationship("Transaction", remote_side=[id], backref="related_transactions")

    def __repr__(self):
        return f"<Transaction {self.id} {self.type.value} {self.amount}>"
```

### app/models/contact.py
```python
from datetime import datetime
from app.extensions import db

class Contact(db.Model):
    __tablename__ = "contacts"

    id = db.Column(db.String(36), primary_key=True)
    owner_user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, index=True)
    contact_user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    owner = db.relationship(
        "User",
        foreign_keys=[owner_user_id],
        back_populates="contacts",
    )
    contact_user = db.relationship(
        "User",
        foreign_keys=[contact_user_id],
        lazy="joined",
    )

    __table_args__ = (
        db.UniqueConstraint("owner_user_id", "contact_user_id", name="uq_owner_contact"),
    )

    def __repr__(self):
        return f"<Contact {self.id}>"
```

### app/models/session.py
```python
from datetime import datetime
from app.extensions import db

class Session(db.Model):
    __tablename__ = "sessions"

    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, index=True)
    token = db.Column(db.String(512), unique=True, nullable=False, index=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(512), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    user = db.relationship("User", back_populates="sessions")

    def __repr__(self):
        return f"<Session {self.id}>"
```

---

## 1.9 Resumen de Archivos a Crear en FASE 1

| Archivo | Tipo |
|---------|------|
| `app/__init__.py` | Nuevo (Application Factory) |
| `app/config.py` | Nuevo |
| `app/extensions.py` | Nuevo |
| `app/models/__init__.py` | Nuevo |
| `app/models/user.py` | Nuevo |
| `app/models/account.py` | Nuevo |
| `app/models/transaction.py` | Nuevo |
| `app/models/contact.py` | Nuevo |
| `app/models/session.py` | Nuevo |
| `app/controllers/__init__.py` | Placeholder |
| `app/services/__init__.py` | Placeholder |
| `app/repositories/__init__.py` | Placeholder |
| `app/dto/__init__.py` | Placeholder |
| `app/utils/__init__.py` | Placeholder |
| `app/exceptions/__init__.py` | Placeholder |
| `requirements.txt` | Actualizar |
| `run.py` | Nuevo |
