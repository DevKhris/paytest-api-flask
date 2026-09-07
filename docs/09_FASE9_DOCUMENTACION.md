# FASE 9: Documentación de Endpoints

## 9.1 Archivos de Spec por Entidad

En `/docs/` se encuentran los specs detallados de cada entidad:

```
docs/
├── auth_spec.md       # Especificación de autenticación
├── account_spec.md    # Especificación de cuentas
├── transaction_spec.md # Especificación de transacciones
└── contact_spec.md   # Especificación de contactos
```

---

## 9.2 auth_spec.md

```markdown
# Auth API Specification

## Base URL
`/api/v1/auth`

## Endpoints

### POST /room-code
Valida un código de sala de espera.

**Request:**
```json
{
  "room_code": "TRAINING01"
}
```

**Response (200):**
```json
{
  "message": "Room code valid",
  "room_code": "TRAINING01"
}
```

**Errores:**
- 400: Código de sala inválido

---

### POST /register
Registra un nuevo usuario con cuenta y fondo inicial.

**Request:**
```json
{
  "name": "John Doe",
  "password": "securepassword123",
  "room_code": "TRAINING01"
}
```

**Response (201):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": "uuid-string",
    "unique_id": "A8LSIWVLGZ1Q",
    "name": "John Doe",
    "created_at": "2024-01-15T10:30:00Z"
  },
  "token": {
    "access_token": "eyJ...",
    "token_type": "Bearer",
    "expires_in": 86400
  }
}
```

**Errores:**
- 400: Datos inválidos
- 409: Usuario ya existe

---

### POST /login
Inicia sesión y retorna token JWT.

**Request:**
```json
{
  "unique_id": "A8LSIWVLGZ1Q",
  "password": "securepassword123"
}
```

**Response (200):**
```json
{
  "message": "Login successful",
  "user": {
    "id": "uuid-string",
    "unique_id": "A8LSIWVLGZ1Q",
    "name": "John Doe",
    "created_at": "2024-01-15T10:30:00Z"
  },
  "token": {
    "access_token": "eyJ...",
    "token_type": "Bearer",
    "expires_in": 86400
  }
}
```

**Errores:**
- 400: Datos inválidos
- 401: Credenciales inválidas

---

### POST /logout
Cierra la sesión actual.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "message": "Logout successful"
}
```

**Errores:**
- 401: Token inválido o faltante
```

---

## 9.3 account_spec.md

```markdown
# Account API Specification

## Base URL
`/api/v1/accounts`

## Endpoints

### GET /me
Obtiene los datos de la cuenta del usuario autenticado.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "id": "uuid-string",
  "user_id": "uuid-string",
  "balance": "750.50",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Errores:**
- 401: No autenticado
- 404: Cuenta no encontrada

---

### GET /balance
Obtiene el balance actual de la cuenta.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "balance": "750.50",
  "currency": "USD"
}
```

**Errores:**
- 401: No autenticado
- 404: Cuenta no encontrada
```

---

## 9.4 transaction_spec.md

```markdown
# Transaction API Specification

## Base URL
`/api/v1/transactions`

## Endpoints

### GET /
Lista transacciones con paginación.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `page` (int, default: 1): Página actual
- `per_page` (int, default: 20): Items por página
- `type` (string, optional): Filtrar por tipo (INCOME, SPEND, REQUEST)

**Response (200):**
```json
{
  "transactions": [
    {
      "id": "uuid-string",
      "account_id": "uuid-string",
      "type": "INCOME",
      "amount": "500.00",
      "idempotency_key": "uuid-hex",
      "reference_id": null,
      "description": "Fondo inicial de bienvenida",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 20
}
```

**Errores:**
- 401: No autenticado

---

### POST /transfer
Transfiere saldo a otro usuario.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request:**
```json
{
  "recipient_unique_id": "B7KDMNVPGH2R",
  "amount": "100.50",
  "idempotency_key": "unique-client-key-12345",
  "description": "Pago por servicios"
}
```

**Response (200):**
```json
{
  "transaction_id": "uuid-string",
  "amount": "100.50",
  "recipient_unique_id": "B7KDMNVPGH2R",
  "sender_balance_after": "650.00",
  "recipient_balance_after": "600.50",
  "status": "completed"
}
```

**Errores:**
- 400: Monto inválido o NaN
- 401: No autenticado
- 404: Beneficiario no encontrado
- 409: Transacción duplicada (idempotency_key)
- 422: Balance insuficiente
```

---

## 9.5 contact_spec.md

```markdown
# Contact API Specification

## Base URL
`/api/v1/contacts`

## Endpoints

### GET /
Lista todos los contactos del usuario.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "contacts": [
    {
      "id": "uuid-string",
      "contact_user_id": "uuid-string",
      "contact": {
        "id": "uuid-string",
        "unique_id": "B7KDMNVPGH2R",
        "name": "Jane Smith"
      },
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 1
}
```

**Errores:**
- 401: No autenticado

---

### POST /
Agrega un nuevo contacto.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request:**
```json
{
  "contact_unique_id": "B7KDMNVPGH2R"
}
```

**Response (201):**
```json
{
  "id": "uuid-string",
  "contact_user_id": "uuid-string",
  "contact": {
    "id": "uuid-string",
    "unique_id": "B7KDMNVPGH2R",
    "name": "Jane Smith"
  },
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Errores:**
- 400: No puedes agregarte a ti mismo / Datos inválidos
- 401: No autenticado
- 404: Usuario a agregar no encontrado
- 409: Contacto ya existe

---

### DELETE /{contact_id}
Elimina un contacto.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "message": "Contact deleted"
}
```

**Errores:**
- 401: No autenticado
- 404: Contacto no encontrado
```

---

## 9.6 Códigos de Sala Válidos

Para propósito de desarrollo/pruebas:

| Código | Descripción |
|--------|-------------|
| `TRAINING01` | Sala de entrenamiento 1 |
| `TRAINING02` | Sala de entrenamiento 2 |
| `DEMO2024` | Sala de demostración |

---

## 9.7 Códigos de Error Comunes

| Código HTTP | Significado |
|-------------|-------------|
| 200 | OK |
| 201 | Creado |
| 400 | Bad Request - Datos inválidos |
| 401 | Unauthorized - No autenticado |
| 404 | Not Found - Recurso no encontrado |
| 409 | Conflict - Duplicado |
| 422 | Unprocessable Entity - Error de negocio |
| 500 | Internal Server Error |
```

---

## 9.8 Resumen de Archivos

| Archivo | Descripción |
|---------|-------------|
| `docs/auth_spec.md` | Especificación completa de auth |
| `docs/account_spec.md` | Especificación completa de accounts |
| `docs/transaction_spec.md` | Especificación completa de transactions |
| `docs/contact_spec.md` | Especificación completa de contacts |
