# FASE 2: Modelos de Datos

## 2.1 Diagrama de Entidades y Relaciones

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│      User       │       │     Account     │       │   Transaction   │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK, UUID)   │──1:1──│ id (PK, UUID)   │──1:N──│ id (PK, UUID)   │
│ unique_id       │       │ user_id (FK)    │       │ account_id (FK) │
│ name            │       │ created_at      │       │ type (ENUM)     │
│ password_hash   │       └─────────────────┘       │ amount          │
│ created_at      │                                 │ idempotency_key │
└─────────────────┘                                 │ reference_id(FK)│
        │                                           │ description     │
        │ 1:N                                       │ created_at      │
        ▼                                           └─────────────────┘
┌─────────────────┐       ┌─────────────────┐               │
│     Session     │       │     Contact     │               │
├─────────────────┤       ├─────────────────┤               │
│ id (PK, UUID)   │       │ id (PK, UUID)   │               │
│ user_id (FK)    │       │ owner_user_id   │───────────────┘
│ token           │       │ contact_user_id │ (FK)
│ ip_address      │       │ created_at      │
│ user_agent      │       └─────────────────┘
│ created_at      │
│ expires_at      │
│ is_active       │
└─────────────────┘
```

---

## 2.2 User Model - Detalle

### Tabla: `users`

| Campo | Tipo | Constraints | Descripción |
|-------|------|-------------|-------------|
| `id` | VARCHAR(36) | PK | UUID como string |
| `unique_id` | VARCHAR(12) | UNIQUE, NOT NULL, INDEX | ID público del usuario (ej: "A8LSIWVLGZ1Q") |
| `name` | VARCHAR(100) | NOT NULL | Nombre completo |
| `password_hash` | VARCHAR(255) | NOT NULL | Hash bcrypt de contraseña |
| `created_at` | DATETIME | NOT NULL, DEFAULT=now() | Timestamp de creación |

### Relaciones:
- `account`: 1:1 con `Account` (back_populates="user")
- `sessions`: 1:N con `Session` (back_populates="user")
- `contacts`: 1:N con `Contact` donde es owner (back_populates="owner")

### Índices:
- `unique_id` (único)
- `created_at`

---

## 2.3 Account Model - Detalle

### Tabla: `accounts`

| Campo | Tipo | Constraints | Descripción |
|-------|------|-------------|-------------|
| `id` | VARCHAR(36) | PK | UUID como string |
| `user_id` | VARCHAR(36) | FK → users.id, UNIQUE | Referencia al usuario |
| `created_at` | DATETIME | NOT NULL, DEFAULT=now() | Timestamp de creación |

### Relaciones:
- `user`: 1:1 con `User` (back_populates="account")
- `transactions`: 1:N con `Transaction` (back_populates="account")

### Balance Calculado:
```python
balance = SUM(INCOME transactions) - SUM(SPEND transactions)
```
El balance se calcula dinámicamente consultando el historial de transacciones.

### Restricciones:
- Un usuario solo puede tener UNA cuenta
- La cuenta se crea automáticamente con el usuario

---

## 2.4 Transaction Model - Detalle

### Tabla: `transactions`

| Campo | Tipo | Constraints | Descripción |
|-------|------|-------------|-------------|
| `id` | VARCHAR(36) | PK | UUID como string |
| `account_id` | VARCHAR(36) | FK → accounts.id, NOT NULL, INDEX | Cuenta asociada |
| `type` | ENUM(INCOME, SPEND, REQUEST) | NOT NULL | Tipo de transacción |
| `amount` | NUMERIC(12,2) | NOT NULL | Monto (siempre positivo) |
| `idempotency_key` | VARCHAR(64) | UNIQUE, NOT NULL, INDEX | Clave de idempotencia |
| `reference_id` | VARCHAR(36) | FK → transactions.id, NULLABLE | Referencia a transacción relacionada |
| `description` | VARCHAR(255) | NULLABLE | Descripción opcional |
| `created_at` | DATETIME | NOT NULL, DEFAULT=now(), INDEX | Timestamp |

### Enum: `TransactionType`
```python
class TransactionType(Enum):
    INCOME = "INCOME"   # Abono/Ingreso
    SPEND = "SPEND"     # Egreso
    REQUEST = "REQUEST"  # Solicitud de pago (pendiente, sin lógica aún)
```

### Relaciones:
- `account`: N:1 con `Account` (back_populates="transactions")
- `reference`: Self-referential para transacciones relacionadas (ej: transferencia)

### Índices:
- `account_id`
- `idempotency_key` (único)
- `created_at`
- `type`

### Validaciones de Negocio:
- `amount` > 0
- `amount` no puede ser NaN o infinito
- `idempotency_key` debe ser único por cuenta

---

## 2.5 Contact Model - Detalle

### Tabla: `contacts`

| Campo | Tipo | Constraints | Descripción |
|-------|------|-------------|-------------|
| `id` | VARCHAR(36) | PK | UUID como string |
| `owner_user_id` | VARCHAR(36) | FK → users.id, NOT NULL, INDEX | Usuario propietario |
| `contact_user_id` | VARCHAR(36) | FK → users.id, NOT NULL, INDEX | Usuario de contacto |
| `created_at` | DATETIME | NOT NULL, DEFAULT=now() | Timestamp |

### Relaciones:
- `owner`: N:1 con `User` (foreign_key=owner_user_id, back_populates="contacts")
- `contact_user`: N:1 con `User` (foreign_key=contact_user_id, lazy="joined")

### Restricciones:
- `UNIQUE(owner_user_id, contact_user_id)` - No duplicados
- `owner_user_id != contact_user_id` - No auto-contactos

### Índices:
- `owner_user_id`
- `contact_user_id`
- `UNIQUE(owner_user_id, contact_user_id)`

---

## 2.6 Session Model - Detalle

### Tabla: `sessions`

| Campo | Tipo | Constraints | Descripción |
|-------|------|-------------|-------------|
| `id` | VARCHAR(36) | PK | UUID como string |
| `user_id` | VARCHAR(36) | FK → users.id, NOT NULL, INDEX | Usuario |
| `token` | VARCHAR(512) | UNIQUE, NOT NULL, INDEX | JWT token |
| `ip_address` | VARCHAR(45) | NULLABLE | IP del cliente (IPv4/IPv6) |
| `user_agent` | VARCHAR(512) | NULLABLE | User-Agent del cliente |
| `created_at` | DATETIME | NOT NULL, DEFAULT=now() | Inicio de sesión |
| `expires_at` | DATETIME | NOT NULL | Expiración del token |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT=True | Estado de la sesión |

### Metadatos de Rastreo:
- `ip_address`: Para auditoría y seguridad
- `user_agent`: Para identificar cliente
- `created_at`: Timestamp de login
- `expires_at`: Para invalidar sesiones

### Índices:
- `user_id`
- `token` (único)
- `is_active`

---

## 2.7 Código Completo de Models

### app/models/user.py

```python
from datetime import datetime
from app.extensions import db
import uuid


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
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

    def to_dict(self):
        return {
            "id": self.id,
            "unique_id": self.unique_id,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
        }
```

### app/models/account.py

```python
from datetime import datetime
from decimal import Decimal
from sqlalchemy import func
from app.extensions import db
import uuid


class Account(db.Model):
    __tablename__ = "accounts"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="account")
    transactions = db.relationship("Transaction", back_populates="account")

    @property
    def balance(self):
        from app.models.transaction import Transaction, TransactionType

        income = db.session.query(
            func.coalesce(func.sum(Transaction.amount), 0)
        ).filter(
            Transaction.account_id == self.id,
            Transaction.type == TransactionType.INCOME
        ).scalar()

        spend = db.session.query(
            func.coalesce(func.sum(Transaction.amount), 0)
        ).filter(
            Transaction.account_id == self.id,
            Transaction.type == TransactionType.SPEND
        ).scalar()

        return Decimal(str(income)) - Decimal(str(spend))

    def __repr__(self):
        return f"<Account {self.id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "balance": str(self.balance),
            "created_at": self.created_at.isoformat(),
        }
```

### app/models/transaction.py

```python
from datetime import datetime
from decimal import Decimal
import enum
from app.extensions import db
import uuid


class TransactionType(enum.Enum):
    INCOME = "INCOME"
    SPEND = "SPEND"
    REQUEST = "REQUEST"


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
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

    def to_dict(self):
        return {
            "id": self.id,
            "account_id": self.account_id,
            "type": self.type.value,
            "amount": str(self.amount),
            "idempotency_key": self.idempotency_key,
            "reference_id": self.reference_id,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
        }
```

### app/models/contact.py

```python
from datetime import datetime
from app.extensions import db
import uuid


class Contact(db.Model):
    __tablename__ = "contacts"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
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

    def to_dict(self):
        return {
            "id": self.id,
            "owner_user_id": self.owner_user_id,
            "contact_user_id": self.contact_user_id,
            "contact": {
                "id": self.contact_user.id,
                "unique_id": self.contact_user.unique_id,
                "name": self.contact_user.name,
            } if self.contact_user else None,
            "created_at": self.created_at.isoformat(),
        }
```

### app/models/session.py

```python
from datetime import datetime
from app.extensions import db
import uuid


class Session(db.Model):
    __tablename__ = "sessions"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
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

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "is_active": self.is_active,
        }
```

### app/models/__init__.py

```python
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction, TransactionType
from app.models.contact import Contact
from app.models.session import Session

__all__ = ["User", "Account", "Transaction", "TransactionType", "Contact", "Session"]
```

---

## 2.8 Resumen de Archivos de la FASE 2

| Archivo | Descripción |
|---------|-------------|
| `app/models/__init__.py` | Exports de todos los modelos |
| `app/models/user.py` | Modelo User completo |
| `app/models/account.py` | Modelo Account con balance dinámico |
| `app/models/transaction.py` | Modelo Transaction con enum TransactionType |
| `app/models/contact.py` | Modelo Contact con relaciones |
| `app/models/session.py` | Modelo Session con metadata |

---

## 2.9 Notas de Implementación

1. **UUIDs como strings:** Usar `str(uuid.uuid4())` para generar IDs legibles
2. **Balance dinámico:** Se calcula en cada consulta, no se almacena
3. **TransactionType enum:** Los valores se guardan como strings en DB
4. **Lazy loading:** `contact_user` usa `lazy="joined"` para optimizar consultas de lista
5. **Índices:** Crear índices en campos frecuentemente consultados
