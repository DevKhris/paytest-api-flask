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
