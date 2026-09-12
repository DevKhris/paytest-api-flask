# FASE 5: Services

## 5.1 Arquitectura de Servicios

Los servicios contienen la lógica de negocio y coordinan repositorios y utilidades.

```
app/services/
├── __init__.py
├── auth_service.py
├── account_service.py
├── transaction_service.py
└── contact_service.py
```

---

## 5.2 Auth Service

### app/services/auth_service.py

```python
import jwt
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
from flask import current_app

from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction, TransactionType
from app.models.session import Session
from app.repositories.user_repository import UserRepository
from app.repositories.account_repository import AccountRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.session_repository import SessionRepository
from app.utils.hash import HashUtil
from app.utils.id_generator import IDGenerator
from app.exceptions.business_exceptions import (
    AuthenticationError,
    UserAlreadyExistsError,
    InvalidCredentialsError,
    RoomCodeInvalidError,
)

logger = logging.getLogger(__name__)


class AuthService:
    VALID_ROOM_CODES = {"TRAINING01", "TRAINING02", "DEMO001"}

    def __init__(self):
        self.user_repo = UserRepository()
        self.account_repo = AccountRepository()
        self.transaction_repo = TransactionRepository()
        self.session_repo = SessionRepository()
        self.hash_util = HashUtil()
        self.id_generator = IDGenerator()

    def validate_room_code(self, room_code: str) -> bool:
        if room_code not in self.VALID_ROOM_CODES:
            logger.warning(f"Invalid room code attempt: {room_code}")
            raise RoomCodeInvalidError(f"Invalid room code: {room_code}")
        return True

    def register(
        self,
        name: str,
        password: str,
        room_code: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Tuple[User, Dict[str, Any]]:
        self.validate_room_code(room_code)

        unique_id = self.id_generator.generate_unique_id()
        while self.user_repo.exists_by_unique_id(unique_id):
            unique_id = self.id_generator.generate_unique_id()

        password_hash = self.hash_util.hash_password(password)

        user = self.user_repo.create(
            unique_id=unique_id,
            name=name,
            password_hash=password_hash,
        )
        logger.info(f"User registered: {unique_id}")

        account = self.account_repo.create(user_id=user.id)
        logger.info(f"Account created for user: {unique_id}")

        initial_amount = self.id_generator.generate_initial_balance()
        idempotency_key = self.id_generator.generate_idempotency_key()

        transaction = self.transaction_repo.create(
            account_id=account.id,
            type=TransactionType.INCOME,
            amount=initial_amount,
            idempotency_key=idempotency_key,
            description="Fondo inicial de bienvenida",
        )
        logger.info(f"Initial transaction created: {transaction.id}, amount: {initial_amount}")

        token_data = self._generate_token(user, ip_address, user_agent)

        return user, token_data

    def login(
        self,
        userId: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Tuple[User, Dict[str, Any]]:
        user = self.user_repo.get_by_id(userId)
        if not user:
            logger.warning(f"Login attempt for non-existent user: {userId}")
            raise InvalidCredentialsError("Invalid credentials")

        if not self.hash_util.verify_password(password, user.password_hash):
            logger.warning(f"Invalid password for user: {userId}")
            raise InvalidCredentialsError("Invalid credentials")

        token_data = self._generate_token(user, ip_address, user_agent)
        logger.info(f"User logged in: {userId}")

        return user, token_data

    def logout(self, token: str) -> bool:
        session = self.session_repo.get_by_token(token)
        if not session:
            return False

        session.status = 'EXPIRED'
        self.session_repo.save(session)
        logger.info(f"User logged out, session deactivated")
        return True

    def verify_token(self, token: str) -> Optional[User]:
        try:
            payload = jwt.decode(
                token,
                current_app.config["JWT_SECRET_KEY"],
                algorithms=["HS256"],
            )
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None

        session = self.session_repo.get_by_token(token)
        if not session or session.status == 'EXPIRED':
            return None

        if session.expires_at < datetime.utcnow():
            session.status = 'EXPIRED'
            self.session_repo.save(session)
            return None

        user = self.user_repo.get_by_id(payload["user_id"])
        return user

    def _generate_token(
        self,
        user: User,
        ip_address: Optional[str],
        user_agent: Optional[str],
    ) -> Dict[str, Any]:
        expires_delta = current_app.config["JWT_ACCESS_TOKEN_EXPIRES"]
        expires_at = datetime.utcnow() + expires_delta

        payload = {
            "user_id": user.id,
            "exp": expires_at,
            "iat": datetime.utcnow(),
        }

        token = jwt.encode(
            payload,
            current_app.config["JWT_SECRET_KEY"],
            algorithm="HS256",
        )

        self.session_repo.create(
            user_id=user.id,
            token=token,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
            status='ACTIVE',
        )

        return {
            "access_token": token,
            "token_type": "Bearer",
            "expires_in": int(expires_delta.total_seconds()),
        }
```

---

## 5.3 Account Service

### app/services/account_service.py

```python
import logging
from decimal import Decimal
from typing import Dict, Any, Optional

from app.models.user import User
from app.models.account import Account
from app.repositories.account_repository import AccountRepository
from app.repositories.transaction_repository import TransactionRepository
from app.exceptions.business_exceptions import AccountNotFoundError

logger = logging.getLogger(__name__)


class AccountService:
    def __init__(self):
        self.account_repo = AccountRepository()
        self.transaction_repo = TransactionRepository()

    def get_account_by_user(self, user: User) -> Account:
        account = self.account_repo.get_by_user_id(user.id)
        if not account:
            raise AccountNotFoundError(f"Account not found for user")
        return account

    def get_account_by_user_id(self, user_id: str) -> Account:
        account = self.account_repo.get_by_user_id(user_id)
        if not account:
            raise AccountNotFoundError(f"Account not found")
        return account

    def get_balance(self, user: User) -> Dict[str, Any]:
        account = self.get_account_by_user(user)
        balance = self.transaction_repo.calculate_balance(account.id)

        return {
            "balance": str(balance),
            "currency": "USD",
        }

    def get_account_details(self, user: User) -> Dict[str, Any]:
        account = self.get_account_by_user(user)
        balance = self.transaction_repo.calculate_balance(account.id)

        return {
            "id": account.id,
            "user_id": account.user_id,
            "balance": str(balance),
            "created_at": account.created_at.isoformat(),
        }
```

---

## 5.4 Transaction Service

### app/services/transaction_service.py

```python
import logging
from decimal import Decimal
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction, TransactionType
from app.repositories.account_repository import AccountRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.user_repository import UserRepository
from app.utils.id_generator import IDGenerator
from app.exceptions.business_exceptions import (
    InsufficientBalanceError,
    InvalidAmountError,
    RecipientNotFoundError,
    TransactionNotFoundError,
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
        transaction_type: Optional[TransactionType] = None,
    ) -> Dict[str, Any]:
        account = self.account_repo.get_by_user_id(user.id)
        if not account:
            raise AccountNotFoundError("Account not found")

        transactions, total = self.transaction_repo.get_by_account_id_paginated(
            account_id=account.id,
            page=page,
            per_page=per_page,
            transaction_type=transaction_type,
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
            logger.warning(f"Duplicate transaction attempt: {idempotency_key}")
            raise DuplicateTransactionError("Transaction already processed")

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

        spend_idempotency_key = self.id_generator.generate_idempotency_key()
        spend_transaction = self.transaction_repo.create(
            account_id=sender_account.id,
            type=TransactionType.SPEND,
            amount=amount,
            idempotency_key=spend_idempotency_key,
            relatedUserId=toUserId,
            description=f"Transfer to {toUserId}" + (f": {description}" if description else ""),
        )
        logger.info(f"SPEND transaction created: {spend_transaction.id}")

        request_idempotency_key = self.id_generator.generate_idempotency_key()
        request_transaction = self.transaction_repo.create(
            account_id=recipient_account.id,
            type=TransactionType.REQUEST,
            amount=amount,
            idempotency_key=request_idempotency_key,
            relatedUserId=sender.id,
            description=f"Transfer request from {sender.id}" + (f": {description}" if description else ""),
        )
        logger.info(f"REQUEST transaction created (pending approval): {request_transaction.id}")

        sender_balance_after = self.transaction_repo.calculate_balance(sender_account.id)
        recipient_balance_after = self.transaction_repo.calculate_balance(recipient_account.id)

        return {
            "transaction_id": spend_transaction.id,
            "amount": str(amount),
            "toUserId": toUserId,
            "sender_balance_after": str(sender_balance_after),
            "recipient_balance_after": str(recipient_balance_after),
            "status": "completed",
        }
```

---

## 5.5 Contact Service

### app/services/contact_service.py

```python
import logging
from typing import Dict, Any, List

from app.models.user import User
from app.models.contact import Contact
from app.repositories.contact_repository import ContactRepository
from app.repositories.user_repository import UserRepository
from app.exceptions.business_exceptions import (
    ContactNotFoundError,
    ContactAlreadyExistsError,
    CannotAddSelfAsContactError,
)

logger = logging.getLogger(__name__)


class ContactService:
    def __init__(self):
        self.contact_repo = ContactRepository()
        self.user_repo = UserRepository()

    def add_contact(self, owner: User, contactUserId: str) -> Dict[str, Any]:
        if owner.id == contactUserId:
            raise CannotAddSelfAsContactError("Cannot add yourself as a contact")

        contact_user = self.user_repo.get_by_id(contactUserId)
        if not contact_user:
            raise ContactNotFoundError(f"User with ID {contactUserId} not found")

        if self.contact_repo.exists_contact(owner.id, contact_user.id):
            raise ContactAlreadyExistsError("Contact already exists")

        contact = self.contact_repo.create(
            ownerId=owner.id,
            contactUserId=contact_user.id,
        )
        logger.info(f"Contact added: {owner.id} -> {contactUserId}")

        return contact.to_dict()

    def get_contacts(self, owner: User) -> Dict[str, Any]:
        contacts, total = self.contact_repo.get_contacts_by_owner_paginated(
            owner_user_id=owner.id,
            page=1,
            per_page=100,
        )

        return {
            "contacts": [c.to_dict() for c in contacts],
            "total": total,
        }

    def delete_contact(self, owner: User, contact_id: str) -> bool:
        contact = self.contact_repo.get_by_id(contact_id)
        if not contact:
            raise ContactNotFoundError("Contact not found")

        if contact.owner_user_id != owner.id:
            raise ContactNotFoundError("Contact not found")

        self.contact_repo.delete(contact)
        logger.info(f"Contact deleted: {contact_id}")
        return True
```

---

## 5.6 Services __init__.py

```python
from app.services.auth_service import AuthService
from app.services.account_service import AccountService
from app.services.transaction_service import TransactionService
from app.services.contact_service import ContactService

__all__ = [
    "AuthService",
    "AccountService",
    "TransactionService",
    "ContactService",
]
```

---

## 5.7 Resumen de Métodos por Servicio

### AuthService
| Método | Descripción |
|--------|-------------|
| `validate_room_code(code)` | Valida código de sala |
| `register(name, password, room_code, ...)` | Registra usuario + crea cuenta + INCOME inicial |
| `login(userId, password, ...)` | Autentica usuario y genera JWT |
| `logout(token)` | Desactiva sesión (status='EXPIRED') |
| `verify_token(token)` | Verifica y retorna usuario del token |

### AccountService
| Método | Descripción |
|--------|-------------|
| `get_account_by_user(user)` | Obtiene cuenta del usuario |
| `get_balance(user)` | Obtiene balance actual |
| `get_account_details(user)` | Obtiene detalles completos de cuenta |

### TransactionService
| Método | Descripción |
|--------|-------------|
| `get_transactions(user, page, per_page, type)` | Lista transacciones con paginación |
| `transfer(sender, toUserId, amount, idempotency_key, ...)` | Transfiere saldo (crea SPEND + REQUEST pendiente) |

### ContactService
| Método | Descripción |
|--------|-------------|
| `add_contact(owner, contactUserId)` | Agrega contacto |
| `get_contacts(owner)` | Lista contactos del usuario |
| `delete_contact(owner, contact_id)` | Elimina contacto |

---

## 5.8 Validaciones de Negocio Implementadas

| Regla | Ubicación | Excepción |
|-------|-----------|-----------|
| Código de sala válido | AuthService | `RoomCodeInvalidError` |
| Usuario no existe al registrar | AuthService | `UserAlreadyExistsError` (implícito) |
| Credenciales válidas | AuthService | `InvalidCredentialsError` |
| Saldo suficiente | TransactionService | `InsufficientBalanceError` |
| Monto > 0 y no NaN/inf | TransactionService | `InvalidAmountError` |
| Beneficiario existe | TransactionService | `RecipientNotFoundError` |
| No transferirse a sí mismo | TransactionService | `InvalidAmountError` |
| Transacción idempotente | TransactionService | `DuplicateTransactionError` |
| Contacto no existe | ContactService | `ContactNotFoundError` |
| Contacto ya existe | ContactService | `ContactAlreadyExistsError` |
| No auto-contacto | ContactService | `CannotAddSelfAsContactError` |

---

## 5.9 Resumen de Archivos

| Archivo | Descripción |
|---------|-------------|
| `app/services/__init__.py` | Export de servicios |
| `app/services/auth_service.py` | Lógica de autenticación |
| `app/services/account_service.py` | Lógica de cuentas |
| `app/services/transaction_service.py` | Lógica de transacciones |
| `app/services/contact_service.py` | Lógica de contactos |
