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
