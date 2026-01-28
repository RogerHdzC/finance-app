# Finance App (MVP / 0001_core)

Aplicación financiera personal **SaaS-ready** enfocada en:
- Control explícito de movimientos
- Trazabilidad total
- Correctitud por encima de conveniencia
- Sin estado inferido (p. ej. sin balances almacenados)

## Stack
- **API:** FastAPI (Python)
- **DB:** PostgreSQL
- **ORM:** SQLAlchemy
- **Migraciones:** Alembic
- **Dependencias:** uv (`pyproject.toml` + `uv.lock`)
- **Infra dev:** Docker Compose (API + DB)

---

## Principios de datos (MVP)
- `correctness_over_convenience`
- `explicit_data_only`
- `auditability_first`
- `no_inferred_state`

### Estrategias clave
- **IDs:** UUID generados por la aplicación
- **Balances:** derivados desde `transactions` (no se almacenan columnas de balance)
- **Transfers:** estrategia de **2 movimientos** (expense + income) vinculados por `transfer_group_id`
- **Categorías:** soporta global templates (`user_id = NULL`) y categorías del usuario (`user_id != NULL`)

---

## Estructura del repo (alto nivel)
- `apps/api/` → FastAPI, modelos, Alembic, migraciones
- `infra/` → Dockerfiles y docker-compose
- `.dockerignore` / `.gitignore` → higiene del repo

---

## Requisitos
- Docker + Docker Compose
- (Opcional) `uv` local si quieres correr fuera de Docker

---

## Variables de entorno
Crea un `.env` (no se commitea) basado en `.env.example`.

Ejemplo (ajusta a tu entorno):
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `DATABASE_URL`

**Nota:** `DATABASE_URL` debe apuntar al host de Postgres visto desde el contenedor `api`.
En Docker Compose normalmente sería algo como:
`postgresql+psycopg://<user>:<pass>@db:5432/<db>`

---

## Levantar en desarrollo (Docker)
Desde la raíz del repo:

```bash
docker compose up --env-file ../.env -d --build
````

El contenedor `api` ejecuta:

1. `alembic upgrade head`
2. `uvicorn ... --reload`

API disponible en:

* [http://localhost:8000](http://localhost:8000)

---

## Comandos útiles

### Ver logs

```bash
docker compose logs --env-file ../.env -f api
docker compose logs --env-file ../.env -f db
```

### Correr migraciones manualmente (sin reiniciar)

```bash
docker compose --env-file ../.env exec api sh -lc "uv run alembic upgrade head"
```

### Ver versión aplicada por Alembic

```bash
docker compose --env-file ../.env exec db psql -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT * FROM alembic_version;"
```

### Listar tablas

```bash
docker compose --env-file ../.env exec db psql -U $POSTGRES_USER -d $POSTGRES_DB -c "\dt"
```

### Reset completo de DB (DEV ONLY — borra datos)

```bash
docker compose down -v
docker compose up --env-file ../.env -d --build
```

---

## Estado del schema (0001_core)

Tablas:

* `users`
* `accounts`
* `categories`
* `transactions`
* `alembic_version`

Índices/constraints relevantes:

* `transactions`: índices compuestos `(user_id, date)` y `(account_id, date)`
* `transactions`: unique compuesto `(user_id, hash_dedupe)`
* `categories`: unique parcial global por `name` cuando `user_id IS NULL`
* `categories`: unique parcial por usuario `(user_id, name)` cuando `user_id IS NOT NULL`

---

## Contribución / Git workflow (recomendado)

* Commits pequeños y “verticales” por capacidad.
* Evitar `sudo git ...` (problemas de permisos).
* Para cambios grandes, trabajar en ramas:

  * `feat/...`, `chore/...`, `fix/...`

---

## Roadmap (alto nivel)

* CRUD
* 0002_auth: refresh tokens, hardening auth
* Import CSV: dry-run, dedupe user-scoped, mapping de categorías
* Reportes: summary / by_account / by_category (sin balances almacenados)

````
