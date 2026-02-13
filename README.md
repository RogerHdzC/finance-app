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
* `security_by_design`

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

# API

## Base Path

```
/api/v1
```

## Routers

* `users`
* `auth`

---

# Authentication Model (0002_auth)

Authentication has been introduced with:

## Access Token

* JWT Bearer token
* Signed with configurable algorithm
* Includes:

  * issuer (`iss`)
  * audience (`aud`)
  * expiration
* Required for protected endpoints

## Refresh Token

* Opaque token
* Stored **hashed** in database
* Rotation configurable via `JWT_REFRESH_ROTATE`
* Supports:

  * revocation
  * expiration tracking
  * replacement chaining (`replaced_by_id`)

---

# Protected Endpoints

Require valid JWT:

* `GET /users`
* `GET /users/{id}`
* `DELETE /users/{id}`

---

## Error handling

Domain-level errors are raised from the service layer and mapped to HTTP responses using a unified format:

```json
{
  "code": "string",
  "message": "string",
  "details": null,
  "trace_id": "string"
}
```

## Validation Handling

* FastAPI `RequestValidationError` → `422 VALIDATION_ERROR`
* Domain-level `ValidationError` → `422 VALIDATION_ERROR`
* DomainError subclasses mapped explicitly to HTTP status codes

This ensures:

* predictable error surface
* clean API contract
* separation of domain and transport concerns

---

## Tech stack

* **Language:** Python 3.14
* **API framework:** FastAPI
* **Database:** PostgreSQL
* **Test DB:** SQLite in-memory
* **ORM:** SQLAlchemy 2.x
* **Migrations:** Alembic
* **JWT:** pyjwt
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
│   ├── services/
│   └── security/
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
* `DATABASE_URL`
* `JWT_SECRET_KEY`
* `JWT_ALGORITHM`
* `JWT_EXPIRATION_DELTA_SECONDS`
* `JWT_ISSUER`
* `JWT_AUDIENCE`
* `JWT_REFRESH_EXPIRATION_SECONDS`
* `JWT_REFRESH_ROTATE`

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

* API tests
* Service layer tests
* Auth tests
* Refresh token service tests
* Dependency tests
* DB metadata tests

Run tests with coverage:

```bash
docker compose exec api sh -lc "uv run pytest --cov=app"
```

Current coverage is **~94%**.

---

## Current schema state (0001_core)

## 0001_core

* users
* accounts
* categories
* transactions
* alembic_version

## 0002_auth (in progress)

* refresh_tokens table added
* JWT authentication
* protected endpoints
* refresh rotation support

---

# Next Priority Actions

* Ensure `AuthService.refresh_access_token` is defined only once
* Validate refresh rotation logic through full test suite
* Fix Bruno tests to use:

  * `res.getStatus()`
  * `res.getBody()`
* Harden auth flows (token reuse detection, revoke-on-rotation)

---

## Roadmap (high-level)

* Auth hardening
* Authorization layer (role/ownership validation)
* Reports (derived-only calculations)
* Observability (structured logging + trace IDs)

---

# Contribution & PR Contract

This repository follows a strict pull request contract to ensure:

- migration discipline
- atomic changes
- conventional commit consistency
- traceable evolution of the schema

See:

📄 `docs/pr-contract.md`

All contributions must comply with the branch naming and PR title rules defined there.

---

## Why this project exists

This is not a toy CRUD project.

It exists to practice:

* schema evolution discipline
* migration safety
* secure authentication modeling
* explicit domain invariants
* production-ready backend architecture
* CI/CD friendly workflows

The objective is to build a backend system that is:

* internally consistent
* security-aware
* evolution-friendly
* SaaS-ready