# Lumay

[![CI](https://github.com/DataSpoof/Lumay/actions/workflows/ci.yml/badge.svg)](https://github.com/DataSpoof/Lumay/actions/workflows/ci.yml)
[![CD](https://github.com/DataSpoof/Lumay/actions/workflows/cd.yml/badge.svg)](https://github.com/DataSpoof/Lumay/actions/workflows/cd.yml)

A simple CRUD API built with [FastAPI](https://fastapi.tiangolo.com/), SQLAlchemy 2.0, and SQLite.

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows  (source .venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API is then at http://127.0.0.1:8000, with interactive docs at
http://127.0.0.1:8000/docs and the OpenAPI schema at `/openapi.json`.

## Endpoints

| Method | Path          | Description                                  |
| ------ | ------------- | -------------------------------------------- |
| GET    | `/health`     | Liveness check                                |
| POST   | `/items`      | Create an item                                |
| GET    | `/items`      | List items (`?skip=0&limit=100`)              |
| GET    | `/items/{id}` | Fetch one item                                |
| PUT    | `/items/{id}` | Update an item (partial — omitted fields keep their value) |
| DELETE | `/items/{id}` | Delete an item                                |

### Item

| Field         | Type            | Notes                        |
| ------------- | --------------- | ---------------------------- |
| `id`          | int             | Assigned by the server        |
| `name`        | str             | Required, 1–120 chars         |
| `description` | str \| null     | Optional, up to 500 chars     |
| `price`       | float           | Must be >= 0, defaults to `0` |
| `in_stock`    | bool            | Defaults to `true`            |
| `created_at`  | datetime        | Set on creation, UTC          |
| `updated_at`  | datetime        | Refreshed on every update, UTC |

### Update semantics

`PUT /items/{id}` is a *partial* update: fields you omit keep their current
value, so you never have to send the whole object to change one field.

`description` is the only nullable field, so `{"description": null}` clears it.
Sending an explicit `null` for `name`, `price`, or `in_stock` is rejected with a
422 and a message naming the field — omit the field instead.

### Timestamps

Timestamps are generated and stored as UTC and always come back with an offset
(`...Z`). SQLite has no native timestamp type and silently discards `tzinfo` on
write, so `ItemRead` re-attaches UTC on the way out; responses are therefore
offset-aware on SQLite and on servers like Postgres alike.

### Example

```bash
curl -X POST http://127.0.0.1:8000/items -H "Content-Type: application/json" -d "{\"name\":\"Notebook\",\"price\":4.5}"
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest -q
```

Each test runs against a temporary SQLite file, so the suite never touches your
development database.

## Docker

```bash
docker build -t lumay .
docker run --rm -p 8000:8000 lumay
```

Published images are available from GitHub Container Registry:

```bash
docker pull ghcr.io/dataspoof/lumay:latest
```

## CI/CD

Two GitHub Actions workflows live in `.github/workflows/`:

**`ci.yml`** runs on every push and pull request to `main`:

- `ruff check` and `ruff format --check` for linting and formatting
- `pytest` on Python 3.11 and 3.12

**`cd.yml`** runs on pushes to `main` and on `v*` tags. It re-runs the test suite,
then builds the Docker image and pushes it to `ghcr.io/dataspoof/lumay`. Tags
applied: `latest` (main), `main`, `sha-<short>`, and for a release tag like
`v1.2.3` also `1.2.3` and `1.2`.

Authentication uses the built-in `GITHUB_TOKEN`, so no repository secrets need to
be configured. Packages published this way start out private; make the package
public from the repository's Packages page if you want anonymous `docker pull`.

## Layout

```
app/
  main.py       FastAPI app, route handlers, get_item_or_404 dependency
  database.py   Engine, session factory, get_db dependency
  models.py     SQLAlchemy ORM models
  schemas.py    Pydantic request/response models and validation rules
  crud.py       Database operations
tests/          pytest suite
```

Route handlers stay thin: `get_item_or_404` resolves the path parameter (or
raises 404) as a FastAPI dependency, so the three single-item routes receive an
`Item` and never repeat the lookup. Database work lives in `crud.py`, and every
validation rule lives in `schemas.py` rather than being checked inside handlers.

## Configuration

Set `DATABASE_URL` to point at another database; it defaults to
`sqlite:///./lumay.db`.
