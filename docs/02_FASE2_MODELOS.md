# FASE 2: Modelos de Datos

## 2.1 Diagrama de Entidades y Relaciones

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│      User       │       │     Account     │       │   Transaction   │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK, 12 chr) │──1:1──│ id (PK, ACC_*) │──1:N──│ id (PK, TXN_*)  │
│ name (max 50)   │       │ user_id (FK)    │       │ account_id (FK) │
│ password_hash   │       │ created_at      │       │ type (ENUM)     │
│ created_at      │       │ updated_at      │       │ amount          │
│ updated_at      │       └─────────────────┘       │ idempotency_key │
└─────────────────┘                                │ related_user_id │
        │ 1:N                                       │ description     │
        ▼                                           │ created_at      │
┌─────────────────┐       ┌─────────────────┐       └─────────────────┘
│     Session     │       │     Contact     │
├─────────────────┤       ├─────────────────┤
│ id (PK, UUID)   │       │ id (PK, UUID)   │
│ user_id (FK)    │       │ owner_id        │
│ token           │       │ contact_user_id │
│ ip_address      │       │ created_at      │
│ user_agent      │       └─────────────────┘
│ status (ENUM)   │
│ created_at      │
│ expires_at      │
└─────────────────┘
```

---

## 2.2 User Model - Detalle

### Tabla: `users`

| Campo | Tipo | Constraints | Descripción |
|-------|------|-------------|-------------|
| `id` | VARCHAR(12) | PK | ID público del usuario (ej: "A8LSIWVLGZ1Q") |
| `name` | VARCHAR(50) | NOT NULL | Nombre completo |
| `password_hash` | VARCHAR(255) | NOT NULL | Hash bcrypt de contraseña |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT=CURRENT_TIMESTAMP | Timestamp de creación |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT=CURRENT_TIMESTAMP ON UPDATE | Timestamp de última actualización |

### Relaciones:
- `account`: 1:1 con `Account` (back_populates="user")
- `sessions`: 1:N con `Session` (back_populates="user")
- `contacts`: 1:N con `Contact` donde es owner (back_populates="owner")

### Índices:
- `id` (único)
- `idx_users_name` en `name`

---

## 2.3 Account Model - Detalle

### Tabla: `accounts`

| Campo | Tipo | Constraints | Descripción |
|-------|------|-------------|-------------|
| `id` | VARCHAR(16) | PK | Formato ACC_{nanoid} (ej: "ACC_a1b2c3d4e5f6") |
| `user_id` | VARCHAR(12) | FK → users.id, UNIQUE | Referencia al usuario |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT=CURRENT_TIMESTAMP | Timestamp de creación |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT=CURRENT_TIMESTAMP ON UPDATE | Timestamp de última actualización |

### Relaciones:
- `user`: 1:1 con `User` (back_populates="account")
- `transactions`: 1:N con `Transaction` (back_populates="account")

### Balance Calculado:
```python
balance = Σ(INCOME amounts) - Σ(SPEND amounts) - Σ(REQUEST amounts)
```
El balance se calcula dinámicamente consultando el historial de transacciones. **NO se almacena en la tabla**.

### Restricciones:
- Un usuario solo puede tener UNA cuenta
- La cuenta se crea automáticamente con el usuario

---

## 2.4 Transaction Model - Detalle

### Tabla: `transactions`

| Campo | Tipo | Constraints | Descripción |
|-------|------|-------------|-------------|
| `id` | VARCHAR(16) | PK | Formato TXN_{nanoid} (ej: "TXN_a1b2c3d4e5f6") |
| `account_id` | VARCHAR(16) | FK → accounts.id, NOT NULL | Cuenta asociada |
| `type` | ENUM('INCOME', 'SPEND', 'REQUEST') | NOT NULL | Tipo de transacción |
| `amount` | DECIMAL(15,2) | NOT NULL | Monto (siempre positivo) |
| `idempotency_key` | VARCHAR(64) | UNIQUE, NOT NULL | Clave de idempotencia |
| `related_user_id` | VARCHAR(12) | NULLABLE | ID del usuario relacionado (ej: receptor en SPEND) |
| `description` | VARCHAR(255) | NULLABLE | Descripción opcional |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT=CURRENT_TIMESTAMP | Timestamp |

### Enum: `TransactionType`
```python
class TransactionType(Enum):
    INCOME = "INCOME"   # Abono/Ingreso
    SPEND = "SPEND"     # Egreso
    REQUEST = "REQUEST"  # Solicitud de pago (pendiente, sin lógica aún)
```

### Relaciones:
- `account`: N:1 con `Account` (back_populates="transactions")

### Índices:
- `idx_transactions_account` en `account_id`
- `idx_transactions_idem` UNIQUE en `idempotency_key`
- `idx_transactions_type` en `type`
- `idx_transactions_created` en `created_at`

### Validaciones de Negocio:
- `amount` > 0
- `amount` no puede ser NaN o infinito
- `idempotency_key` debe ser único globalmente

---

## 2.5 Contact Model - Detalle

### Tabla: `contacts`

| Campo | Tipo | Constraints | Descripción |
|-------|------|-------------|-------------|
| `id` | VARCHAR(36) | PK | UUID como string |
| `owner_id` | VARCHAR(12) | FK → users.id, NOT NULL | Usuario propietario |
| `contact_user_id` | VARCHAR(12) | FK → users.id, NOT NULL | Usuario de contacto |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT=CURRENT_TIMESTAMP | Timestamp |

### Relaciones:
- `owner`: N:1 con `User` (foreign_key=owner_id, back_populates="contacts")
- `contact_user`: N:1 con `User` (foreign_key=contact_user_id, lazy="joined")

**Nota:** El nombre del contacto se obtiene consultando `users` joined, **no se almacena**.

### Restricciones:
- `UNIQUE unique_contact (owner_id, contact_user_id)` - No duplicados
- `owner_id != contact_user_id` - No auto-contactos (validación en servicio)

### Índices:
- `idx_contacts_owner` en `owner_id`
- `idx_contacts_contact` en `contact_user_id`
- `unique_contact` UNIQUE en `(owner_id, contact_user_id)`

---

## 2.6 Session Model - Detalle

### Tabla: `sessions`

| Campo | Tipo | Constraints | Descripción |
|-------|------|-------------|-------------|
| `id` | VARCHAR(36) | PK | UUID como string |
| `user_id` | VARCHAR(12) | FK → users.id, NOT NULL | Usuario |
| `token` | VARCHAR(512) | UNIQUE, NOT NULL | JWT token |
| `ip_address` | VARCHAR(45) | NULLABLE | IP del cliente (IPv4/IPv6) |
| `user_agent` | VARCHAR(512) | NULLABLE | User-Agent del cliente |
| `status` | ENUM('ACTIVE', 'EXPIRED') | NOT NULL, DEFAULT='ACTIVE' | Estado de la sesión |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT=CURRENT_TIMESTAMP | Inicio de sesión |
| `expires_at` | TIMESTAMP | NOT NULL | Expiración del token |

### Metadatos de Rastreo:
- `ip_address`: Para auditoría y seguridad
- `user_agent`: Para identificar cliente
- `created_at`: Timestamp de login
- `expires_at`: Para invalidar sesiones

### Índices:
- `idx_sessions_token` UNIQUE en `token`
- `idx_sessions_user` en `user_id`
- `idx_sessions_expires` en `expires_at`

---

## 2.7 Código Completo de Models

### app/models/user.py

```python
from datetime import datetime
from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(12), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    account = db.relationship("Account", back_populates="user", uselist=False)
    sessions = db.relationship("Session", back_populates="user")
    contacts = db.relationship(
        "Contact",
        foreign_keys="Contact.owner_id",
        back_populates="owner",
    )

    def __repr__(self):
        return f"<User {self.id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
```

### app/models/account.py

```python
from datetime import datetime
from decimal import Decimal
from sqlalchemy import func
from app.extensions import db


class Account(db.Model):
    __tablename__ = "accounts"

    id = db.Column(db.String(16), primary_key=True)
    user_id = db.Column(db.String(12), db.ForeignKey("users.id"), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

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

        request = db.session.query(
            func.coalesce(func.sum(Transaction.amount), 0)
        ).filter(
            Transaction.account_id == self.id,
            Transaction.type == TransactionType.REQUEST
        ).scalar()

        return Decimal(str(income)) - Decimal(str(spend)) - Decimal(str(request))

    def __repr__(self):
        return f"<Account {self.id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "balance": str(self.balance),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
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

    id = db.Column(db.String(16), primary_key=True)
    account_id = db.Column(db.String(16), db.ForeignKey("accounts.id"), nullable=False, index=True)
    type = db.Column(db.Enum(TransactionType), nullable=False)
    amount = db.Column(db.Numeric(precision=15, scale=2), nullable=False)
    idempotency_key = db.Column(db.String(64), unique=True, nullable=False, index=True)
    related_user_id = db.Column(db.String(12), nullable=True)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    account = db.relationship("Account", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction {self.id} {self.type.value} {self.amount}>"

    def to_dict(self):
        return {
            "id": self.id,
            "account_id": self.account_id,
            "type": self.type.value,
            "amount": str(self.amount),
            "idempotency_key": self.idempotency_key,
            "related_user_id": self.related_user_id,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
        }
```

### app/models/contact.py

```python
from datetime import datetime
from app.extensions import db


class Contact(db.Model):
    __tablename__ = "contacts"

    id = db.Column(db.String(36), primary_key=True)
    owner_id = db.Column(db.String(12), db.ForeignKey("users.id"), nullable=False, index=True)
    contact_user_id = db.Column(db.String(12), db.ForeignKey("users.id"), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    owner = db.relationship(
        "User",
        foreign_keys=[owner_id],
        back_populates="contacts",
    )
    contact_user = db.relationship(
        "User",
        foreign_keys=[contact_user_id],
        lazy="joined",
    )

    __table_args__ = (
        db.UniqueConstraint("owner_id", "contact_user_id", name="unique_contact"),
    )

    def __repr__(self):
        return f"<Contact {self.id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "owner_id": self.owner_id,
            "contact_user_id": self.contact_user_id,
            "contact": {
                "id": self.contact_user.id,
                "name": self.contact_user.name,
            } if self.contact_user else None,
            "created_at": self.created_at.isoformat(),
        }
```

### app/models/session.py

```python
from datetime import datetime
from app.extensions import db


class Session(db.Model):
    __tablename__ = "sessions"

    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(12), db.ForeignKey("users.id"), nullable=False, index=True)
    token = db.Column(db.String(512), unique=True, nullable=False, index=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(512), nullable=True)
    status = db.Column(db.String(20), default='ACTIVE', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)

    user = db.relationship("User", back_populates="sessions")

    def __repr__(self):
        return f"<Session {self.id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "token": self.token,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
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
| `app/models/session.py` | Modelo Session con status ENUM |

---

## 2.9 Notas de Implementación

1. **IDs alfanuméricos:** Usar `id` de 12 caracteres para User y `ACC_{nanoid}`/`TXN_{nanoid}` para Account/Transaction
2. **Balance dinámico:** Se calcula en cada consulta desde transactions, NO se almacena
3. **TransactionType enum:** Los valores se guardan como strings en DB
4. **Lazy loading:** `contact_user` usa `lazy="joined"` para optimizar consultas de lista
5. **Índices:** Crear índices en campos frecuentemente consultados
6. **Contactos:** Usar snake_case (`owner_id`, `contact_user_id`) para nombres de columnas
7. **Session status:** Usar `status` ENUM('ACTIVE', 'EXPIRED') en vez de `is_active` BOOLEAN
8. **Timestamps:** Usar `created_at` y `updated_at` de forma consistente
9. **Contact name:** Se obtiene consultando users joined, NO se almacena en contacts
