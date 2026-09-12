# FASE 3: Data Transfer Objects (DTOs)

## 3.1 Propósito de los DTOs

Los DTOs (Data Transfer Objects) separan la lógica de validación de datos de la lógica de negocio:
- **Requests DTOs:** Validan y transforman datos de entrada
- **Response DTOs:** Formatean datos de salida de manera consistente

---

## 3.2 Request DTOs

### app/dto/requests/__init__.py

```python
from app.dto.requests.auth_dto import (
    RoomCodeRequest,
    RegisterRequest,
    LoginRequest,
)
from app.dto.requests.transaction_dto import TransferRequest
from app.dto.requests.contact_dto import AddContactRequest

__all__ = [
    "RoomCodeRequest",
    "RegisterRequest",
    "LoginRequest",
    "TransferRequest",
    "AddContactRequest",
]
```

### app/dto/requests/auth_dto.py

```python
from marshmallow import Schema, fields, validate, validates, ValidationError


class RoomCodeRequest(Schema):
    room_code = fields.String(
        required=True,
        validate=validate.Length(min=4, max=10),
    )


class RegisterRequest(Schema):
    name = fields.String(
        required=True,
        validate=validate.Length(min=2, max=100),
    )
    password = fields.String(
        required=True,
        validate=validate.Length(min=6, max=128),
        load_only=True,
    )
    room_code = fields.String(
        required=True,
        validate=validate.Length(min=4, max=10),
    )


class LoginRequest(Schema):
    userId = fields.String(
        required=True,
        validate=validate.Length(min=12, max=12),
    )
    password = fields.String(
        required=True,
        load_only=True,
    )
```

### app/dto/requests/transaction_dto.py

```python
from decimal import Decimal, InvalidOperation
from marshmallow import Schema, fields, validate, validates, ValidationError


class TransferRequest(Schema):
    toUserId = fields.String(
        required=True,
        validate=validate.Length(min=12, max=12),
    )
    amount = fields.Decimal(
        required=True,
        places=2,
        as_string=True,
    )
    idempotency_key = fields.String(
        required=True,
        validate=validate.Length(min=16, max=64),
    )
    description = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=255),
    )

    @validates("amount")
    def validate_amount(self, value):
        try:
            amount = Decimal(str(value))
            if amount <= 0:
                raise ValidationError("Amount must be greater than zero")
            if amount.is_nan() or amount.is_infinite():
                raise ValidationError("Amount cannot be NaN or infinite")
        except (InvalidOperation, ValueError):
            raise ValidationError("Invalid numeric value for amount")
```

### app/dto/requests/contact_dto.py

```python
from marshmallow import Schema, fields, validate


class AddContactRequest(Schema):
    contactUserId = fields.String(
        required=True,
        validate=validate.Length(min=12, max=12),
    )
```

---

## 3.3 Response DTOs

### app/dto/responses/__init__.py

```python
from app.dto.responses.auth_response_dto import (
    AuthResponse,
    TokenResponse,
    UserResponse,
)
from app.dto.responses.account_response_dto import AccountResponse, BalanceResponse
from app.dto.responses.transaction_response_dto import TransactionResponse, TransactionListResponse
from app.dto.responses.contact_response_dto import ContactResponse, ContactListResponse

__all__ = [
    "AuthResponse",
    "TokenResponse",
    "UserResponse",
    "AccountResponse",
    "BalanceResponse",
    "TransactionResponse",
    "TransactionListResponse",
    "ContactResponse",
    "ContactListResponse",
]
```

### app/dto/responses/auth_response_dto.py

```python
from marshmallow import Schema, fields


class UserResponse(Schema):
    userId = fields.String()
    name = fields.String()
    created_at = fields.DateTime(format="iso")
    updatedAt = fields.DateTime(format="iso")


class TokenResponse(Schema):
    access_token = fields.String()
    token_type = fields.String(default="Bearer")
    expires_in = fields.Integer()


class AuthResponse(Schema):
    message = fields.String()
    user = fields.Nested(UserResponse)
    token = fields.Nested(TokenResponse)
```

### app/dto/responses/account_response_dto.py

```python
from marshmallow import Schema, fields


class AccountResponse(Schema):
    accountId = fields.String()
    userId = fields.String()
    balance = fields.String()
    created_at = fields.DateTime(format="iso")
    updatedAt = fields.DateTime(format="iso")


class BalanceResponse(Schema):
    balance = fields.String()
    currency = fields.String(default="USD")
```

### app/dto/responses/transaction_response_dto.py

```python
from marshmallow import Schema, fields


class TransactionResponse(Schema):
    id = fields.String()
    accountId = fields.String()
    type = fields.String()
    amount = fields.String()
    idempotency_key = fields.String()
    relatedUserId = fields.String(allow_none=True)
    description = fields.String(allow_none=True)
    created_at = fields.DateTime(format="iso")


class TransactionListResponse(Schema):
    transactions = fields.List(fields.Nested(TransactionResponse))
    total = fields.Integer()
    page = fields.Integer()
    per_page = fields.Integer()
```

### app/dto/responses/contact_response_dto.py

```python
from marshmallow import Schema, fields


class ContactUserInfo(Schema):
    userId = fields.String()
    name = fields.String()


class ContactResponse(Schema):
    id = fields.String()
    ownerId = fields.String()
    contactUserId = fields.String()
    contact = fields.Nested(ContactUserInfo)
    created_at = fields.DateTime(format="iso")


class ContactListResponse(Schema):
    contacts = fields.List(fields.Nested(ContactResponse))
    total = fields.Integer()
```

---

## 3.4 Ejemplo de Uso de DTOs en un Controller

```python
from flask import request, jsonify
from marshmallow import ValidationError
from app.dto.requests.auth_dto import RegisterRequest
from app.dto.responses.auth_response_dto import AuthResponse

register_schema = RegisterRequest()
auth_response_schema = AuthResponse()

@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = register_schema.load(request.json)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    
    # ... lógica del servicio ...
    
    response_data = auth_response_schema.dump({"user": user, "token": token_data})
    return jsonify(response_data), 201
```

---

## 3.5 Resumen de DTOs

### Request DTOs

| DTO | Campos | Validaciones |
|-----|--------|--------------|
| `RoomCodeRequest` | room_code | length 4-10 |
| `RegisterRequest` | name, password, room_code | name 2-50, password 6-128 |
| `LoginRequest` | userId, password | userId exact 12 |
| `TransferRequest` | toUserId, amount, idempotency_key, description | amount > 0, not NaN/inf |
| `AddContactRequest` | contactUserId | userId exact 12 |

### Response DTOs

| DTO | Campos | Uso |
|-----|--------|-----|
| `UserResponse` | userId, name, created_at, updatedAt | Devolver datos de usuario |
| `TokenResponse` | access_token, token_type, expires_in | Devolver JWT |
| `AuthResponse` | message, user, token | Respuesta completa de auth |
| `AccountResponse` | accountId, userId, balance, created_at, updatedAt | Datos de cuenta |
| `BalanceResponse` | balance, currency | Solo balance |
| `TransactionResponse` | id, accountId, type, amount, ... | Una transacción |
| `TransactionListResponse` | transactions[], total, page, per_page | Lista paginada |
| `ContactResponse` | id, ownerId, contactUserId, contact{}, created_at | Un contacto |
| `ContactListResponse` | contacts[], total | Lista de contactos |

---

## 3.6 Resumen de Archivos

| Archivo | Descripción |
|---------|-------------|
| `app/dto/__init__.py` | Export de DTOs |
| `app/dto/requests/__init__.py` | Export requests |
| `app/dto/requests/auth_dto.py` | DTOs de autenticación |
| `app/dto/requests/transaction_dto.py` | DTO de transferencias |
| `app/dto/requests/contact_dto.py` | DTO de contactos |
| `app/dto/responses/__init__.py` | Export responses |
| `app/dto/responses/auth_response_dto.py` | Response DTOs auth |
| `app/dto/responses/account_response_dto.py` | Response DTOs account |
| `app/dto/responses/transaction_response_dto.py` | Response DTOs transaction |
| `app/dto/responses/contact_response_dto.py` | Response DTOs contact |
