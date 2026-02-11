# Organization Directory API

## Tech Stack

- **Python 3.13**, **FastAPI**, **Pydantic v2**
- **SQLAlchemy 2.0** + **asyncpg**
- **PostgreSQL 16** + **PostGIS 3.4**
- **GeoAlchemy2** + **Shapely**
- **Alembic**
- **Docker Compose**

## Project Structure

```
src/
  api/
    v1/              # Route handlers (buildings, organizations)
    dependencies/    # FastAPI DI (services, auth, database)
    middleware/       # Exception handlers
  core/              # Configuration
  domain/
    models/          # SQLAlchemy ORM models
    schemas/         # Pydantic schemas
    interfaces/      # Repository protocols
    exceptions/      # Domain exceptions
  infrastructure/
    repositories/    # Repository implementations
  services/          # Business logic
  seed.py            # Database seeding script
migrations/          # Alembic migrations
tests/
  unit/              # Unit tests (services, config, exceptions)
  integration/       # Integration tests (API endpoints)
```

## Quick Start

### Docker Compose

```bash
make build   # Build Docker images
make run     # Start PostgreSQL + API (applies migrations, seeds data)
```

API will be available at `http://localhost:8000`.

### Local Development

Prerequisites: Python 3.13+, [uv](https://docs.astral.sh/uv/), running PostgreSQL with PostGIS.

```bash
# Install dependencies
make install-deps

# Set environment variables (copy and edit)
cp .env.example .env

# Apply migrations
uv run alembic upgrade head

# Seed database
uv run python -m src.seed

# Start server
uv run uvicorn src.main:app --reload
```

## Environment Variables

All variables use the `APP_` prefix. Defaults are suitable for local development with Docker Compose.

### Database (`APP_POSTGRES_DATA_*`)

| Variable | Default | Description |
|---|---|---|
| `APP_POSTGRES_DATA_DATABASE` | `directory` | Database name |
| `APP_POSTGRES_DATA_HOST` | `127.0.0.1` | PostgreSQL host |
| `APP_POSTGRES_DATA_PORT` | `5432` | PostgreSQL port |
| `APP_POSTGRES_DATA_USER` | `postgres` | Database user |
| `APP_POSTGRES_DATA_PASSWORD` | `postgres` | Database password |
| `APP_POSTGRES_DATA_POOL_SIZE` | `5` | Connection pool size |
| `APP_POSTGRES_DATA_POOL_MAX_OVERFLOW` | `2` | Max overflow connections |
| `APP_POSTGRES_DATA_POOL_RECYCLE` | `1200` | Connection recycle time (sec) |

### Application (`APP_APP_*`)

| Variable | Default | Description |
|---|---|---|
| `APP_APP_TITLE` | `Organization Directory API` | Application title (Swagger UI) |
| `APP_APP_VERSION` | `1.0.0` | Application version |
| `APP_APP_DEBUG` | `false` | Debug mode (`true`/`false`) |

### Security (`APP_SECURITY_*`)

| Variable | Default | Description |
|---|---|---|
| `APP_SECURITY_API_KEY` | `secret-api-key` | API key for authentication |

All endpoints require the `X-Api-Key` header:

```bash
curl -H "X-Api-Key: secret-api-key" http://localhost:8000/api/v1/buildings/
```

### Activity Settings (`APP_ACTIVITY_*`)

| Variable | Default | Description |
|---|---|---|
| `APP_ACTIVITY_MAX_DEPTH` | `3` | Maximum activity nesting depth |

## API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Makefile Commands

| Command | Description |
|---|---|
| `make install-deps` | Install all dependencies (including dev) |
| `make format` | Auto-format code (ruff format + import sorting) |
| `make lint` | Run linter checks |
| `make sure` | Format + lint |
| `make test` | Run tests with coverage |
| `make build` | Build Docker images |
| `make run` | Start Docker Compose stack |
| `make stop` | Stop Docker Compose stack |
| `make down` | Stop and remove containers + volumes |
| `make logs` | Follow Docker Compose logs |
| `make all` | Format + lint + test + build |

## Testing

```bash
make test
```

Runs pytest with coverage report. Minimum coverage threshold: 70%.

## Contact
Feel free to reach out if you have any questions or feedback regarding this task:
* Telegram: [@lmikhailsokolovl](https://t.me/lmikhailsokolovl)
