# FASE 6: Controllers (Endpoints REST)

## 6.1 Arquitectura de Controllers

Los controllers definen las rutas HTTP y delegan a los servicios.

```
app/controllers/
├── __init__.py
├── auth_controller.py      # /api/v1/auth/*
├── account_controller.py   # /api/v1/accounts/*
├── transaction_controller.py  # /api/v1/transactions/*
└── contact_controller.py  # /api/v1/contacts/*
```

---

## 6.2 Auth Controller

### app/controllers/auth_controller.py

```python
from flask import Blueprint, request, jsonify, g
from marshmallow import ValidationError

from app.services.auth_service import AuthService
from app.dto.requests.auth_dto import RoomCodeRequest, RegisterRequest, LoginRequest
from app.dto.responses.auth_response_dto import AuthResponse
from app.utils.decorators import handle_exceptions, require_auth

auth_bp = Blueprint("auth", __name__)
auth_service = AuthService()

room_code_schema = RoomCodeRequest()
register_schema = RegisterRequest()
login_schema = LoginRequest()
auth_response_schema = AuthResponse()


@auth_bp.route("/room-code", methods=["POST"])
@handle_exceptions
def validate_room_code():
    data = room_code_schema.load(request.json)
    auth_service.validate_room_code(data["room_code"])
    return jsonify({"message": "Room code valid", "room_code": data["room_code"]}), 200


@auth_bp.route("/register", methods=["POST"])
@handle_exceptions
def register():
    data = register_schema.load(request.json)

    user, token_data = auth_service.register(
        name=data["name"],
        password=data["password"],
        room_code=data["room_code"],
        ip_address=request.remote_addr,
        user_agent=request.headers.get("User-Agent"),
    )

    response = auth_response_schema.dump({
        "message": "User registered successfully",
        "user": user,
        "token": token_data,
    })
    return jsonify(response), 201


@auth_bp.route("/login", methods=["POST"])
@handle_exceptions
def login():
    data = login_schema.load(request.json)

    user, token_data = auth_service.login(
        userId=data["userId"],
        password=data["password"],
        ip_address=request.remote_addr,
        user_agent=request.headers.get("User-Agent"),
    )

    response = auth_response_schema.dump({
        "message": "Login successful",
        "user": user,
        "token": token_data,
    })
    return jsonify(response), 200


@auth_bp.route("/logout", methods=["POST"])
@require_auth
@handle_exceptions
def logout():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    auth_service.logout(token)
    return jsonify({"message": "Logout successful"}), 200
```

---

## 6.3 Account Controller

### app/controllers/account_controller.py

```python
from flask import Blueprint, request, jsonify, g
from marshmallow import ValidationError

from app.services.account_service import AccountService
from app.utils.decorators import handle_exceptions, require_auth

account_bp = Blueprint("accounts", __name__)
account_service = AccountService()


@account_bp.route("/me", methods=["GET"])
@require_auth
@handle_exceptions
def get_my_account():
    user = g.current_user
    account_data = account_service.get_account_details(user)
    return jsonify(account_data), 200


@account_bp.route("/balance", methods=["GET"])
@require_auth
@handle_exceptions
def get_balance():
    user = g.current_user
    balance_data = account_service.get_balance(user)
    return jsonify(balance_data), 200
```

---

## 6.4 Transaction Controller

### app/controllers/transaction_controller.py

```python
from flask import Blueprint, request, jsonify, g
from marshmallow import ValidationError

from app.services.transaction_service import TransactionService
from app.models.transaction import TransactionType
from app.dto.requests.transaction_dto import TransferRequest
from app.utils.decorators import handle_exceptions, require_auth

transaction_bp = Blueprint("transactions", __name__)
transaction_service = TransactionService()

transfer_schema = TransferRequest()


@transaction_bp.route("", methods=["GET"])
@require_auth
@handle_exceptions
def get_transactions():
    user = g.current_user

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    transaction_type = request.args.get("type", None, type=str)

    if transaction_type:
        try:
            transaction_type = TransactionType(transaction_type)
        except ValueError:
            return jsonify({"error": "Invalid transaction type"}), 400

    transactions_data = transaction_service.get_transactions(
        user=user,
        page=page,
        per_page=per_page,
        transaction_type=transaction_type,
    )
    return jsonify(transactions_data), 200


@transaction_bp.route("/transfer", methods=["POST"])
@require_auth
@handle_exceptions
def transfer():
    user = g.current_user
    data = transfer_schema.load(request.json)

    from decimal import Decimal

    result = transaction_service.transfer(
        sender=user,
        toUserId=data["toUserId"],
        amount=Decimal(str(data["amount"])),
        idempotency_key=data["idempotency_key"],
        description=data.get("description"),
    )
    return jsonify(result), 200
```

---

## 6.5 Contact Controller

### app/controllers/contact_controller.py

```python
from flask import Blueprint, request, jsonify, g
from marshmallow import ValidationError

from app.services.contact_service import ContactService
from app.dto.requests.contact_dto import AddContactRequest
from app.utils.decorators import handle_exceptions, require_auth

contact_bp = Blueprint("contacts", __name__)
contact_service = ContactService()

add_contact_schema = AddContactRequest()


@contact_bp.route("", methods=["GET"])
@require_auth
@handle_exceptions
def get_contacts():
    user = g.current_user
    contacts_data = contact_service.get_contacts(user)
    return jsonify(contacts_data), 200


@contact_bp.route("", methods=["POST"])
@require_auth
@handle_exceptions
def add_contact():
    user = g.current_user
    data = add_contact_schema.load(request.json)

    contact_data = contact_service.add_contact(
        owner=user,
        contactUserId=data["contactUserId"],
    )
    return jsonify(contact_data), 201


@contact_bp.route("/<contact_id>", methods=["DELETE"])
@require_auth
@handle_exceptions
def delete_contact(contact_id):
    user = g.current_user
    contact_service.delete_contact(owner=user, contact_id=contact_id)
    return jsonify({"message": "Contact deleted"}), 200
```

---

## 6.6 Controllers __init__.py

```python
from app.controllers.auth_controller import auth_bp
from app.controllers.account_controller import account_bp
from app.controllers.transaction_controller import transaction_bp
from app.controllers.contact_controller import contact_bp

__all__ = ["auth_bp", "account_bp", "transaction_bp", "contact_bp"]
```

---

## 6.7 Decoradores

### app/utils/decorators.py

```python
import logging
from functools import wraps
from flask import request, jsonify, g
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)
auth_service = AuthService()


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

## 6.8 Resumen de Endpoints

### Auth Endpoints (`/api/v1/auth`)

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| POST | `/room-code` | No | Valida código de sala |
| POST | `/register` | No | Registra usuario nuevo |
| POST | `/login` | No | Inicia sesión |
| POST | `/logout` | Yes | Cierra sesión |

### Account Endpoints (`/api/v1/accounts`)

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/me` | Yes | Obtiene cuenta del usuario |
| GET | `/balance` | Yes | Obtiene balance actual |

### Transaction Endpoints (`/api/v1/transactions`)

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/` | Yes | Lista transacciones (paginado) |
| POST | `/transfer` | Yes | Transfiere saldo |

### Contact Endpoints (`/api/v1/contacts`)

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/` | Yes | Lista contactos |
| POST | `/` | Yes | Agrega contacto |
| DELETE | `/{id}` | Yes | Elimina contacto |

---

## 6.9 Códigos de Respuesta HTTP

| Código | Uso |
|--------|-----|
| 200 | OK (GET exitoso, logout) |
| 201 | Created (register, add contact, transfer) |
| 400 | Bad Request (validación fallida) |
| 401 | Unauthorized (token inválido/faltante) |
| 404 | Not Found (recurso no existe) |
| 409 | Conflict (duplicado, e.g., contacto ya existe) |
| 422 | Unprocessable Entity (error de negocio, e.g., saldo insuficiente) |
| 500 | Internal Server Error |

---

## 6.10 Resumen de Archivos

| Archivo | Descripción |
|---------|-------------|
| `app/controllers/__init__.py` | Export de blueprints |
| `app/controllers/auth_controller.py` | Endpoints de autenticación |
| `app/controllers/account_controller.py` | Endpoints de cuentas |
| `app/controllers/transaction_controller.py` | Endpoints de transacciones |
| `app/controllers/contact_controller.py` | Endpoints de contactos |
