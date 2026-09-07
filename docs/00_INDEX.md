# PayTest Backend - Índice de Fases

## Tabla de Contenidos

| # | Archivo | Descripción |
|---|---------|-------------|
| 0 | `spec.md` | Especificación técnica completa del proyecto |
| 1 | `00_INDEX.md` | Este archivo - Índice y guía de ejecución |
| 2 | `01_FASE1_ESTRUCTURA_BASE.md` | Estructura de carpetas, configuración, app factory |
| 3 | `02_FASE2_MODELOS.md` | Modelos de datos (User, Account, Transaction, Contact, Session) |
| 4 | `03_FASE3_DTOS.md` | Data Transfer Objects (requests y responses) |
| 5 | `04_FASE4_REPOSITORIES.md` | Capa de acceso a datos |
| 6 | `05_FASE5_SERVICES.md` | Lógica de negocio |
| 7 | `06_FASE6_CONTROLLERS.md` | Endpoints REST |
| 8 | `07_FASE7_UTILS_EXCEPTIONS.md` | Utilidades y excepciones custom |
| 9 | `08_FASE8_TESTING_INFRA.md` | Infraestructura de testing (conftest, fixtures) |
| 10 | `09_FASE9_DOCUMENTACION.md` | Documentación OpenAPI/specs por entidad |

---

## Orden de Implementación Sugerido

```
FASE 1 (Config)
    ↓
FASE 2 (Models) ← Depende de FASE 1
    ↓
FASE 3 (DTOs) ← Depende de FASE 2
    ↓
FASE 7 (Utils/Exceptions) ← Independiente, pero requerido por otros
    ↓
FASE 4 (Repositories) ← Depende de FASE 2, 7
    ↓
FASE 5 (Services) ← Depende de FASE 3, 4, 7
    ↓
FASE 6 (Controllers) ← Depende de FASE 5, 7
    ↓
FASE 8 (Testing) ← Depende de FASE 1, 2, 4, 5
    ↓
FASE 9 (Documentation) ← Independiente
```

---

## Dependencias Entre Fases

| Fase | Depende De |
|------|------------|
| FASE 1: Estructura Base | Ninguna |
| FASE 2: Modelos | FASE 1 |
| FASE 3: DTOs | FASE 2 |
| FASE 4: Repositories | FASE 2, FASE 7 |
| FASE 5: Services | FASE 3, FASE 4, FASE 7 |
| FASE 6: Controllers | FASE 5, FASE 7 |
| FASE 7: Utils/Exceptions | Ninguna |
| FASE 8: Testing | FASE 1, FASE 2, FASE 4, FASE 5 |
| FASE 9: Documentación | Ninguna |

---

## Resumen de Tecnologías

- **Runtime:** Python 3.11+
- **Framework:** Flask 3.x
- **ORM:** SQLAlchemy 2.x
- **Base de Datos:** PostgreSQL
- **Auth:** PyJWT
- **Testing:** pytest, pytest-cov, pytest-flask
- **Migraciones:** Flask-Migrate (Alembic)
- **Validación:** marshmallow o pydantic

---

## Scripts Disponibles (Post-Implementación)

```bash
# Instalación de dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
python run.py

# Ejecutar tests con coverage
pytest --cov=app --cov-report=html

# Generar migraciones
flask db upgrade
```

---

## Convenciones de Código

- **Nomenclatura:**
  - Clases: `PascalCase` (ej: `UserRepository`)
  - Métodos/funciones: `snake_case` (ej: `get_by_id`)
  - Constantes: `UPPER_SNAKE_CASE` (ej: `MAX_BALANCE`)
  - Variables: `snake_case` (ej: `user_id`)

- **Imports:** Usar rutas absolutas desde `app`
  ```python
  from app.models.user import User
  from app.services.auth_service import AuthService
  ```

- **Tipo de retorno API:** Siempre JSON
- **Códigos HTTP:** Seguir estándar REST
- **Logging:** Usar `logging` stdlib con formato estructurado

---

## Guía de Uso de Este Plan

1. Leer `spec.md` para entender el proyecto completo
2. Seguir las fases en orden numérico
3. Cada archivo de fase contiene:
   - Estructura de archivos a crear
   - Contenido detallado de cada archivo
   - Dependencias específicas
   - Reglas de negocio aplicadas
4. Al finalizar todas las fases, el proyecto estará listo para testing
