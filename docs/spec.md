# PayTest Backend - Especificación Técnica

## 1. Rol y Objetivo

Actúa como un Desarrollador Backend Senior / Arquitecto de Software. Tu objetivo es diseñar e implementar la base para la API REST **PayTest Backend**, un sistema de simulación de pagos creado exclusivamente como entorno didáctico para capacitaciones de Testing con Agentes e Herramientas de IA. Esta API será consumida posteriormente por una aplicación Frontend.

---

## 2. Arquitectura y Principios de Diseño

- **Estilo:** API REST pura (sin ningún tipo de renderizado en servidor, solo respuestas JSON).
- **Principios:** Clean Code, SOLID, YAGNI y Patrones de Diseño aplicables (Repository, Factory, etc.).
- **Trazabilidad:** Sistema de logging robusto y estructurado para observabilidad de eventos del sistema.
- **Testing:** Configurar la infraestructura base para pruebas unitarias e integración (runner, utilidades, configuración de coverage), **sin implementar los test** (estos se realizaran durante la capacitacion).

---

## 3. Entidades Principales

### 3.1 User (Usuario)

- Posee un **ID Único** de referencia alfanumérico (ejemplo: `"A8LSIWVLGZ1Q"`).
- Autenticación mediante su ID Único + Contraseña (hasheada con algoritmo seguro).

### 3.2 Account (Cuenta)

- Vinculada directamente al Usuario a través de su ID Único.
- Refleja el balance actual derivado del historial de transacciones.

### 3.3 Transaction (Transacción)

- Representa todos los movimientos de saldo asociados a las cuentas.
- Tipos: `INCOME` (Ingreso/Abono Inicial), `SPEND` (Egreso) y `REQUEST` (Petición de pago).
- Cálculo del balance final dinámico o derivado estrictamente del historial de transacciones.

### 3.4 Contact (Contacto)

- Lista de contactos guardados por un usuario.
- Permite vincular a otros usuarios mediante su **ID Único**, retornando únicamente su Nombre e ID Único.

### 3.5 Session (Sesión)

- Manejo de sesiones de usuario con metadatos de rastreo (dirección IP, User-Agent/WebClient, timestamps).

---

## 4. Funcionalidades y Reglas de Negocio

### 4.1 Acceso, Registro e Inicialización de Cuentas

- **Sala de Espera:** Acceso inicial mediante un código de sala que valida la entrada al Dashboard.
- **Creación de Usuario y Carga Inicial:**
  - Al ingresar por primera vez, el backend genera un **ID Único** de usuario + Hash de contraseña para su posterior autenticación.
  - Se vincula automáticamente una cuenta al usuario.
  - **Fondo Inicial Automático:** Al crearse la cuenta, se genera de forma obligatoria una **transacción inicial de tipo `INCOME`** por un monto aleatorio ficticio. Este registro servirá como el punto de partida del historial de transacciones y del balance de la cuenta.

### 4.2 Movimientos de Saldo y Transferencias

- **Envío de Saldo:** Los usuarios pueden enviarse saldo entre sí especificando únicamente el **ID Único** del usuario destinatario y el monto a transferir.
- **Recepción de Saldo:** Actualización del historial e incremento del balance al recibir saldo de otro usuario.
- **Idempotencia:** **Todas** las transacciones (incluida la acreditación del saldo inicial) deben incluir mecanismos para garantizar idempotencia y evitar duplicaciones.
- **Restricciones Financieras Estrictas:**
  - **PROHIBIDO** saldos negativos tras una transacción.
  - **PROHIBIDO** valores infinitos, NaN, montos negativos o no numéricos.
  - Las operaciones son puramente ficticias (cálculos en memoria/BD directa, sin pasarelas de pago reales).

### 4.3 Contactos

- Permite a un usuario agregar a otros usuarios a su lista de contactos usando exclusivamente el **ID Único** del usuario a agregar.
- Endpoint para listar contactos mostrando únicamente: `Nombre` e `ID Único`.

### 4.4 Alcance del Proyecto (Exclusiones Didácticas)

- **EXCLUIDO:** Flujo de aprobación/rechazo de Solicitud de Pagos (`REQUEST`). Esta funcionalidad se desarrollará en una sesión posterior en vivo. La entidad `Transaction` debe soportar el tipo `REQUEST`, pero la lógica de resolución queda fuera de este alcance.

---

## 5. Decisiones Arquitectónicas

| Componente | Elección |
|------------|----------|
| Framework Web | Flask 3.x |
| Base de Datos | PostgreSQL |
| ORM | SQLAlchemy |
| Autenticación | JWT con PyJWT |
| Estructura | Arquitectura por capas (Controllers → Services → Repositories → Models) |
| Testing | pytest con pytest-cov y pytest-flask |

---

## 6. Entregables Esperados

1. **Estructura del Proyecto:** Arquitectura limpia por capas (Controladores, Servicios, Repositorios, Entidades/Modelos, DTOs).
2. **Endpoints REST:** Declaración limpia de rutas (ej: `/auth`, `/accounts`, `/transactions`, `/contacts`).
3. **Base de Testing:** Configuración del entorno de pruebas y script de coverage listo para ejecutarse.
4. **Documentación/OpenAPI:** Documentación básica de endpoints o archivo Swagger. Specs por entidad/funciones en formato `.md`.

---

## 7. Estructura de Archivos del Plan de Documentación

```
docs/
├── spec.md                    # Este archivo - Especificación completa
├── 00_INDEX.md               # Índice y guía de ejecución de fases
├── 01_FASE1_ESTRUCTURA_BASE.md
├── 02_FASE2_MODELOS.md
├── 03_FASE3_DTOS.md
├── 04_FASE4_REPOSITORIES.md
├── 05_FASE5_SERVICES.md
├── 06_FASE6_CONTROLLERS.md
├── 07_FASE7_UTILS_EXCEPTIONS.md
├── 08_FASE8_TESTING_INFRA.md
└── 09_FASE9_DOCUMENTACION.md
```
