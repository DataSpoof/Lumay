# Lumay — guidance for AI coding agents

A small FastAPI CRUD service. Read this before changing anything; it records the
decisions that are easy to break by accident.

## Commands

```bash
.venv\Scripts\python.exe -m pytest                       # full suite, ~1s
.venv\Scripts\python.exe -m ruff check .                 # lint
.venv\Scripts\python.exe -m ruff format .                # format
.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

On Windows the GitHub CLI is not on `PATH` and must be called through
PowerShell: `& "C:\Program Files\GitHub CLI\gh.exe" ...`.

## Architecture

Four layers, and changes belong in exactly one of them:

| File | Responsibility |
| --- | --- |
| `app/main.py` | Routes and HTTP concerns only. Handlers stay one or two lines. |
| `app/schemas.py` | Every validation rule. Do not validate inside handlers. |
| `app/crud.py` | All database access. Handlers never build queries. |
| `app/models.py` | ORM models, table definitions, column constraints. |
| `app/database.py` | Engine, session factory, `get_db` dependency. |

`get_item_or_404` in `app/main.py` resolves the `item_id` path parameter as a
dependency. Single-item routes take the resolved `Item`; they must not call
`crud.get_item` and repeat the 404 check.

## Invariants that are easy to break

**Validation belongs in the schema, not the database.** `ItemUpdate` rejects an
explicit `null` for `name`, `price`, and `in_stock` because those columns are
`NOT NULL`; letting a null through produced a 500 from an `IntegrityError`
instead of a 422. If you add a non-nullable column, add it to that validator.

**Timestamps are UTC everywhere.** SQLite discards `tzinfo` on write, so
`ItemRead` re-attaches UTC when reading. Do not "simplify" this away — dropping
either half makes responses offset-naive on SQLite while staying correct on
Postgres, which is worse than being consistently wrong.

**`PUT` is a partial update by design.** Omitted fields keep their value
(`exclude_unset=True`). Changing this breaks existing clients.

**Tables are created at startup via `create_all`.** There are no migrations, so
altering a column will not update an existing database. Say so explicitly if a
change needs one.

## Rules for changes

- Run `ruff check .`, `ruff format .`, and `pytest` before committing. CI runs
  the same three and nothing else, so green locally means green in CI.
- A behaviour change needs a test that fails without it. Never delete, skip, or
  weaken an existing test to get CI green — if a test fails, the change is
  wrong until proven otherwise.
- Pin new dependencies exactly, in `requirements.txt` or `requirements-dev.txt`.
- Never commit secrets, tokens, or `.env` files. Nothing here needs a credential.
- `main` is protected. Work on a branch and open a pull request; do not push to
  `main` and do not use `--force` on a shared branch.
- Report what you actually ran. If a check was skipped, say it was skipped.

## Scope

Match the request. Adding auth, caching, migrations, or new endpoints alongside
an unrelated fix makes the change unreviewable — propose it separately instead.
