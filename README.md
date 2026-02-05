# Finance App — Personal Finance Platform
Personal finance application designed as a **SaaS-ready backend system**, with a strong emphasis on **data correctness, auditability, and explicit state**.

This project is intentionally used as a **learning and experimentation platform** to design production-oriented backend systems, focusing on:
- correct data modeling
- traceability
- migrations discipline
- cloud-readiness (Docker + CI/CD friendly)

> **Status:** Active development
> Core architecture and data model are stable.
> Authentication and advanced features are in progress.

---

## Core principles

- `correctness_over_convenience`
- `explicit_data_only`
- `auditability_first`
- `no_inferred_state`

These principles drive all design decisions in the system.

---

## Key data strategies

- **IDs:** UUIDs generated at database level
- **Balances:** never stored — always derived from `transactions`
- **Transfers:** modeled as **two linked transactions** (expense + income) via `transfer_group_id`
- **Categories:** supports both global templates (`user_id IS NULL`) and user-specific categories

---

## Architecture

The system follows a **layered backend architecture**:

* **API layer** – FastAPI routers
* **Service layer** – domain logic and invariants
* **Schemas** – request/response validation
* **Models** – SQLAlchemy ORM
* **Domain errors** – explicitly modeled and mapped to HTTP responses
* **Core modules** – cross-cutting concerns (security, OpenAPI, dependencies)

The application is initialized via an **application factory** with centralized error handling.

---

## Error handling

Domain-level errors are raised from the service layer and mapped to HTTP responses using a unified format:

```json
{
  "code": "string",
  "detail": "string",
  "meta": {}
}
```

This ensures consistent, predictable error contracts for API consumers.

---

## Tech stack

* **Language:** Python 3.14
* **API framework:** FastAPI
* **Database:** PostgreSQL
* **ORM:** SQLAlchemy 2.x
* **Migrations:** Alembic
* **Password hashing:** Argon2 (`passlib`)
* **Dependency management:** `uv`
* **Testing:** pytest + coverage
* **Containerization:** Docker & Docker Compose

---

## Repository structure (simplified)

```
apps/api/
├── app/
│   ├── core/
│   ├── db/
│   ├── exceptions/
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   └── services/
├── alembic/
└── tests/

infra/
├── docker-compose.yml
└── dev-entrypoint.sh
```

---

## Requirements

- Docker + Docker Compose  
- (Optional) `uv` locally if running outside containers

---

## Environment variables

Create a `.env` file (not committed) based on `.env.example`.

Required variables:
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `DATABASE_URL`

> `DATABASE_URL` must point to the Postgres host as seen from the `api` container  
> Example:
> `postgresql+psycopg://<user>:<pass>@db:5432/<db>`

---

## Running locally (Docker)

From the repository root:

```bash
docker compose --env-file ../.env up -d --build
````

The `api` container automatically:

1. Applies migrations (`alembic upgrade head`)
2. Starts the API with hot-reload

API available at:

* [http://localhost:8000](http://localhost:8000)

---

## Useful commands

### View logs

```bash
docker compose --env-file ../.env logs -f api
docker compose --env-file ../.env logs -f db
```

### Run migrations manually

```bash
docker compose --env-file ../.env exec api sh -lc "uv run alembic upgrade head"
```

### Check Alembic version

```bash
docker compose --env-file ../.env exec db psql -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT * FROM alembic_version;"
```

### List tables

```bash
docker compose --env-file ../.env exec db psql -U $POSTGRES_USER -d $POSTGRES_DB -c "\dt"
```

### Reset database (DEV ONLY — destructive)

```bash
docker compose down -v
docker compose --env-file ../.env up -d --build
```

---

## Testing

The project includes a structured test suite covering:

* API endpoints
* service/domain logic
* domain-level errors

Run tests with coverage:

```bash
docker compose exec api sh -lc "uv run pytest --cov=app"
```

Current coverage is **~94%**.

---

## Current schema state (0001_core)

Tables:

* `users`
* `accounts`
* `categories`
* `transactions`
* `alembic_version`

Relevant constraints and indexes:

* `transactions`: composite indexes `(user_id, date)` and `(account_id, date)`
* `transactions`: unique `(user_id, hash_dedupe)`
* `categories`: partial unique index for global categories (`user_id IS NULL`)
* `categories`: user-scoped unique `(user_id, name)`

---

## Roadmap (high-level)

* Authentication & authorization
* CRUD completion
* `0002_auth`: refresh tokens, auth hardening
* CSV import with dry-run and deduplication
* Reports: summary / by_account / by_category (derived data only)

---

## Why this project exists

This project is not intended to be a feature-complete finance app.
Its primary goal is to **practice backend system design decisions under real constraints**, including:

* schema evolution
* migration safety
* explicit data modeling
* correctness guarantees
* future cloud deployment readiness
