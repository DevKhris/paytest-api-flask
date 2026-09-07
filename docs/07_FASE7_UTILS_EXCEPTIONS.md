# FASE 7: Utils y Exceptions

## 7.1 Estructura

```
app/utils/
├── __init__.py
├── hash.py           # Hashing de contraseñas (bcrypt)
├── id_generator.py  # Generación de IDs únicos
├── idempotency.py   # Utilidades de idempotencia
└── decorators.py   # Decoradores (auth, validation)

app/exceptions/
├── __init__.py
└── business_exceptions.py  # Excepciones de negocio
```

---

## 7.2 Hash Utils

### app/utils/hash.py

```python
import bcrypt


class HashUtil:
    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
```

---

## 7.3 ID Generator

### app/utils/id_generator.py

```python
import random
import string
import uuid
from decimal import Decimal


class IDGenerator:
    ALPHABET = string.ascii_uppercase + string.digits
    UNIQUE_ID_LENGTH = 12

    @staticmethod
    def generate_unique_id() -> str:
        return "".join(random.choices(IDGenerator.ALPHABET, k=IDGenerator.UNIQUE_ID_LENGTH))

    @staticmethod
    def generate_idempotency_key() -> str:
        return f"{uuid.uuid4().hex}"

    @staticmethod
    def generate_initial_balance() -> Decimal:
        return Decimal(str(random.randint(10000, 100000))) / 100

    @staticmethod
    def generate_uuid() -> str:
        return str(uuid.uuid4())
```

---

## 7.4 Idempotency Utils

### app/utils/idempotency.py

```python
import hashlib
import time
from typing import Optional


class IdempotencyUtil:
    @staticmethod
    def generate_key(
        account_id: str,
        transaction_type: str,
        amount: str,
        recipient_id: Optional[str] = None,
    ) -> str:
        data = f"{account_id}:{transaction_type}:{amount}:{recipient_id or ''}"
        return hashlib.sha256(data.encode()).hexdigest()

    @staticmethod
    def validate_key(key: str) -> bool:
        if not key or len(key) < 16:
            return False
        return True

    @staticmethod
    def create_client_key() -> str:
        return f"client_{int(time.time() * 1000)}"
```

---

## 7.5 Exceptions

### app/exceptions/business_exceptions.py

```python
class BusinessException(Exception):
    status_code = 400

    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code


class AuthenticationError(BusinessException):
    status_code = 401


class InvalidCredentialsError(BusinessException):
    status_code = 401


class RoomCodeInvalidError(BusinessException):
    status_code = 400


class UserAlreadyExistsError(BusinessException):
    status_code = 409


class AccountNotFoundError(BusinessException):
    status_code = 404


class InsufficientBalanceError(BusinessException):
    status_code = 422


class InvalidAmountError(BusinessException):
    status_code = 400


class RecipientNotFoundError(BusinessException):
    status_code = 404


class TransactionNotFoundError(BusinessException):
    status_code = 404


class DuplicateTransactionError(BusinessException):
    status_code = 409


class ContactNotFoundError(BusinessException):
    status_code = 404


class ContactAlreadyExistsError(BusinessException):
    status_code = 409


class CannotAddSelfAsContactError(BusinessException):
    status_code = 400
```

### app/exceptions/__init__.py

```python
from app.exceptions.business_exceptions import (
    BusinessException,
    AuthenticationError,
    InvalidCredentialsError,
    RoomCodeInvalidError,
    UserAlreadyExistsError,
    AccountNotFoundError,
    InsufficientBalanceError,
    InvalidAmountError,
    RecipientNotFoundError,
    TransactionNotFoundError,
    DuplicateTransactionError,
    ContactNotFoundError,
    ContactAlreadyExistsError,
    CannotAddSelfAsContactError,
)

__all__ = [
    "BusinessException",
    "AuthenticationError",
    "InvalidCredentialsError",
    "RoomCodeInvalidError",
    "UserAlreadyExistsError",
    "AccountNotFoundError",
    "InsufficientBalanceError",
    "InvalidAmountError",
    "RecipientNotFoundError",
    "TransactionNotFoundError",
    "DuplicateTransactionError",
    "ContactNotFoundError",
    "ContactAlreadyExistsError",
    "CannotAddSelfAsContactError",
]
```

---

## 7.6 Utils __init__.py

```python
from app.utils.hash import HashUtil
from app.utils.id_generator import IDGenerator
from app.utils.idempotency import IdempotencyUtil

__all__ = ["HashUtil", "IDGenerator", "IdempotencyUtil"]
```

---

## 7.7 Decorators (Repetido para Completitud)

### app/utils/decorators.py

```python
import logging
from functools import wraps
from flask import request, jsonify, g
from marshmallow import ValidationError

from app.services.auth_service import AuthService
from app.exceptions.business_exceptions import BusinessException

logger = logging.getLogger(__name__)


def handle_exceptions(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationError as e:
            logger.warning(f"Validation error: {e.messages}")
            return jsonify({"errors": e.messages}), 400
        except BusinessException as e:
            logger.warning(f"Business error: {e.message}")
            return jsonify({"error": e.message}), e.status_code
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return jsonify({"error": "Internal server error"}), 500

    return decorated_function


def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_service = AuthService()

        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid authorization header"}), 401

        token = auth_header.replace("Bearer ", "")

        user = auth_service.verify_token(token)
        if not user:
            return jsonify({"error": "Invalid or expired token"}), 401

        g.current_user = user
        g.current_token = token

        return f(*args, **kwargs)

    return decorated_function
```

---

## 7.8 Resumen de Utilidades

### HashUtil
| Método | Descripción |
|--------|-------------|
| `hash_password(password)` | Genera hash bcrypt de password |
| `verify_password(password, hash)` | Verifica password contra hash |

### IDGenerator
| Método | Descripción |
|--------|-------------|
| `generate_unique_id()` | Genera ID público de 12 caracteres (ej: "A8LSIWVLGZ1Q") |
| `generate_idempotency_key()` | Genera clave UUID para idempotencia |
| `generate_initial_balance()` | Genera monto aleatorio ($100-$1000) |
| `generate_uuid()` | Genera UUID v4 estándar |

### IdempotencyUtil
| Método | Descripción |
|--------|-------------|
| `generate_key(...)` | Genera clave hash para transacción |
| `validate_key(key)` | Valida formato de clave |
| `create_client_key()` | Genera clave para cliente |

---

## 7.9 Resumen de Excepciones

| Excepción | Status Code | Uso |
|-----------|-------------|-----|
| `BusinessException` | 400 | Base class |
| `AuthenticationError` | 401 | Error de autenticación |
| `InvalidCredentialsError` | 401 | Credenciales inválidas |
| `RoomCodeInvalidError` | 400 | Código de sala inválido |
| `UserAlreadyExistsError` | 409 | Usuario ya existe |
| `AccountNotFoundError` | 404 | Cuenta no encontrada |
| `InsufficientBalanceError` | 422 | Balance insuficiente |
| `InvalidAmountError` | 400 | Monto inválido |
| `RecipientNotFoundError` | 404 | Beneficiario no encontrado |
| `TransactionNotFoundError` | 404 | Transacción no encontrada |
| `DuplicateTransactionError` | 409 | Transacción duplicada |
| `ContactNotFoundError` | 404 | Contacto no encontrado |
| `ContactAlreadyExistsError` | 409 | Contacto ya existe |
| `CannotAddSelfAsContactError` | 400 | No auto-contacto |

---

## 7.10 Resumen de Archivos

| Archivo | Descripción |
|---------|-------------|
| `app/utils/__init__.py` | Export de utilidades |
| `app/utils/hash.py` | Utilidad de hashing bcrypt |
| `app/utils/id_generator.py` | Generador de IDs |
| `app/utils/idempotency.py` | Utilidades de idempotencia |
| `app/utils/decorators.py` | Decoradores auth y exceptions |
| `app/exceptions/__init__.py` | Export de excepciones |
| `app/exceptions/business_exceptions.py` | Excepciones de negocio |
