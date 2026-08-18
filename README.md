# Lumay

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
| `created_at`  | datetime        | Set on creation               |
| `updated_at`  | datetime        | Refreshed on every update     |

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

## Layout

```
app/
  main.py       FastAPI app and route handlers
  database.py   Engine, session factory, get_db dependency
  models.py     SQLAlchemy ORM models
  schemas.py    Pydantic request/response models
  crud.py       Database operations
tests/          pytest suite
```

## Configuration

Set `DATABASE_URL` to point at another database; it defaults to
`sqlite:///./lumay.db`.
