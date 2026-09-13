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
