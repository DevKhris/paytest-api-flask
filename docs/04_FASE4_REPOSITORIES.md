# FASE 4: Repositories

## 4.1 Patrón Repository

El patrón Repository abstrae el acceso a datos, separando la lógica de negocio de la persistencia.

### Estructura Base

```
app/repositories/
├── __init__.py
├── base_repository.py    # Clase base con CRUD genérico
├── user_repository.py
├── account_repository.py
├── transaction_repository.py
├── contact_repository.py
└── session_repository.py
```

---

## 4.2 Base Repository

### app/repositories/base_repository.py

```python
from typing import TypeVar, Generic, Type, Optional, List, Any
from flask_sqlalchemy import SQLAlchemy
from app.extensions import db

T = TypeVar("T", bound=db.Model)


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model
        self.db = db

    def get_by_id(self, id: str) -> Optional[T]:
        return self.model.query.get(id)

    def get_all(self) -> List[T]:
        return self.model.query.all()

    def create(self, **kwargs) -> T:
        instance = self.model(**kwargs)
        self.db.session.add(instance)
        self.db.session.commit()
        return instance

    def update(self, instance: T, **kwargs) -> T:
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        self.db.session.commit()
        return instance

    def delete(self, instance: T) -> None:
        self.db.session.delete(instance)
        self.db.session.commit()

    def save(self, instance: T) -> T:
        self.db.session.add(instance)
        self.db.session.commit()
        return instance

    def find_by(self, **kwargs) -> Optional[T]:
        return self.model.query.filter_by(**kwargs).first()

    def find_all_by(self, **kwargs) -> List[T]:
        return self.model.query.filter_by(**kwargs).all()
```

---

## 4.3 User Repository

### app/repositories/user_repository.py

```python
from typing import Optional, List
from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    def get_by_unique_id(self, unique_id: str) -> Optional[User]:
        return self.find_by(unique_id=unique_id)

    def get_by_email(self, email: str) -> Optional[User]:
        return self.find_by(email=email)

    def exists_by_unique_id(self, unique_id: str) -> bool:
        return self.find_by(unique_id=unique_id) is not None

    def get_with_account(self, user_id: str) -> Optional[User]:
        return self.model.query.options().get(user_id)
```

---

## 4.4 Account Repository

### app/repositories/account_repository.py

```python
from typing import Optional
from app.models.account import Account
from app.repositories.base_repository import BaseRepository


class AccountRepository(BaseRepository[Account]):
    def __init__(self):
        super().__init__(Account)

    def get_by_user_id(self, user_id: str) -> Optional[Account]:
        return self.find_by(user_id=user_id)

    def get_by_user_id_or_raise(self, user_id: str) -> Account:
        account = self.get_by_user_id(user_id)
        if not account:
            raise ValueError(f"Account not found for user {user_id}")
        return account

    def get_with_transactions(self, account_id: str) -> Optional[Account]:
        return self.model.query.options(
            selectinload(Account.transactions)
        ).get(account_id)
```

---

## 4.5 Transaction Repository

### app/repositories/transaction_repository.py

```python
from typing import Optional, List
from datetime import datetime
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

    def get_by_reference_id(self, reference_id: str) -> Optional[Transaction]:
        return self.find_by(reference_id=reference_id)
```

---

## 4.6 Contact Repository

### app/repositories/contact_repository.py

```python
from typing import List, Optional
from app.models.contact import Contact
from app.repositories.base_repository import BaseRepository


class ContactRepository(BaseRepository[Contact]):
    def __init__(self):
        super().__init__(Contact)

    def get_by_owner_and_contact(
        self,
        owner_user_id: str,
        contact_user_id: str,
    ) -> Optional[Contact]:
        return self.find_by(
            owner_user_id=owner_user_id,
            contact_user_id=contact_user_id,
        )

    def get_contacts_by_owner(self, owner_user_id: str) -> List[Contact]:
        return self.find_all_by(owner_user_id=owner_user_id)

    def get_contacts_by_owner_paginated(
        self,
        owner_user_id: str,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[List[Contact], int]:
        query = self.model.query.filter_by(owner_user_id=owner_user_id)
        total = query.count()
        contacts = query.offset((page - 1) * per_page).limit(per_page).all()
        return contacts, total

    def exists_contact(self, owner_user_id: str, contact_user_id: str) -> bool:
        return self.get_by_owner_and_contact(owner_user_id, contact_user_id) is not None

    def delete_by_owner_and_contact(self, owner_user_id: str, contact_user_id: str) -> bool:
        contact = self.get_by_owner_and_contact(owner_user_id, contact_user_id)
        if contact:
            self.delete(contact)
            return True
        return False
```

---

## 4.7 Session Repository

### app/repositories/session_repository.py

```python
from datetime import datetime
from typing import Optional, List
from app.models.session import Session
from app.repositories.base_repository import BaseRepository


class SessionRepository(BaseRepository[Session]):
    def __init__(self):
        super().__init__(Session)

    def get_by_token(self, token: str) -> Optional[Session]:
        return self.find_by(token=token)

    def get_active_by_user_id(self, user_id: str) -> List[Session]:
        return self.model.query.filter_by(
            user_id=user_id,
            is_active=True,
        ).all()

    def get_expired_sessions(self) -> List[Session]:
        return self.find_all_by(is_active=True).filter(
            Session.expires_at < datetime.utcnow()
        )

    def deactivate_by_token(self, token: str) -> bool:
        session = self.get_by_token(token)
        if session:
            session.is_active = False
            self.save(session)
            return True
        return False

    def deactivate_all_for_user(self, user_id: str) -> int:
        sessions = self.get_active_by_user_id(user_id)
        count = 0
        for session in sessions:
            session.is_active = False
            self.save(session)
            count += 1
        return count

    def cleanup_expired(self) -> int:
        expired = self.model.query.filter(
            Session.is_active == True,
            Session.expires_at < datetime.utcnow(),
        ).all()
        count = 0
        for session in expired:
            session.is_active = False
            self.save(session)
            count += 1
        return count
```

---

## 4.8 Repositories __init__.py

```python
from app.repositories.base_repository import BaseRepository
from app.repositories.user_repository import UserRepository
from app.repositories.account_repository import AccountRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.contact_repository import ContactRepository
from app.repositories.session_repository import SessionRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "AccountRepository",
    "TransactionRepository",
    "ContactRepository",
    "SessionRepository",
]
```

---

## 4.9 Resumen de Métodos por Repository

### BaseRepository
| Método | Descripción |
|--------|-------------|
| `get_by_id(id)` | Obtiene por ID primario |
| `get_all()` | Obtiene todos los registros |
| `create(**kwargs)` | Crea nuevo registro |
| `update(instance, **kwargs)` | Actualiza registro |
| `delete(instance)` | Elimina registro |
| `save(instance)` | Guarda/actualiza registro |
| `find_by(**kwargs)` | Busca por campos específicos |
| `find_all_by(**kwargs)` | Busca todos por campos |

### UserRepository (extiende Base)
| Método | Descripción |
|--------|-------------|
| `get_by_unique_id(unique_id)` | Busca por ID público |
| `exists_by_unique_id(unique_id)` | Verifica existencia |

### AccountRepository (extiende Base)
| Método | Descripción |
|--------|-------------|
| `get_by_user_id(user_id)` | Obtiene cuenta por user_id |
| `get_by_user_id_or_raise(user_id)` | Obtiene o lanza excepción |
| `get_with_transactions(account_id)` | Obtiene con transacciones cargadas |

### TransactionRepository (extiende Base)
| Método | Descripción |
|--------|-------------|
| `get_by_idempotency_key(key)` | Busca por clave de idempotencia |
| `get_by_account_id(account_id)` | Lista transacciones de cuenta |
| `get_by_account_id_paginated(...)` | Lista paginada con filtros |
| `calculate_balance(account_id)` | Calcula balance dinámicamente |
| `get_by_reference_id(ref_id)` | Busca transacción relacionada |

### ContactRepository (extiende Base)
| Método | Descripción |
|--------|-------------|
| `get_by_owner_and_contact(...)` | Busca contacto específico |
| `get_contacts_by_owner(owner_id)` | Lista contactos de usuario |
| `get_contacts_by_owner_paginated(...)` | Lista paginada |
| `exists_contact(...)` | Verifica si existe contacto |
| `delete_by_owner_and_contact(...)` | Elimina por owner y contact |

### SessionRepository (extiende Base)
| Método | Descripción |
|--------|-------------|
| `get_by_token(token)` | Busca por token JWT |
| `get_active_by_user_id(user_id)` | Sesiones activas de usuario |
| `get_expired_sessions()` | Sesiones expiradas |
| `deactivate_by_token(token)` | Desactiva sesión |
| `deactivate_all_for_user(user_id)` | Desactiva todas las sesiones |
| `cleanup_expired()` | Limpia sesiones expiradas |

---

## 4.10 Resumen de Archivos

| Archivo | Descripción |
|---------|-------------|
| `app/repositories/__init__.py` | Export de repositories |
| `app/repositories/base_repository.py` | Clase base genérica |
| `app/repositories/user_repository.py` | Repository de User |
| `app/repositories/account_repository.py` | Repository de Account |
| `app/repositories/transaction_repository.py` | Repository de Transaction |
| `app/repositories/contact_repository.py` | Repository de Contact |
| `app/repositories/session_repository.py` | Repository de Session |
