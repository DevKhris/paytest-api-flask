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
