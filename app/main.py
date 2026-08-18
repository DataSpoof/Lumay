"""FastAPI application exposing CRUD endpoints for items."""

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import engine, get_db

NOT_FOUND = {404: {"description": "Item not found"}}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Suitable for a single-service app; a real deployment would run
    # migrations instead of creating tables at startup.
    models.Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Lumay API",
    description="A simple CRUD API built with FastAPI.",
    version="0.1.0",
    lifespan=lifespan,
)


def get_item_or_404(item_id: int, db: Session = Depends(get_db)) -> models.Item:
    """Resolve the ``item_id`` path parameter, or raise 404."""
    db_item = crud.get_item(db, item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item


@app.get("/health", tags=["meta"], summary="Liveness check")
def health() -> dict[str, str]:
    """Report that the service is up. Does not touch the database."""
    return {"status": "ok"}


@app.post(
    "/items",
    response_model=schemas.ItemRead,
    status_code=status.HTTP_201_CREATED,
    tags=["items"],
    summary="Create an item",
)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    """Create an item and return it with its assigned id and timestamps."""
    return crud.create_item(db, item)


@app.get(
    "/items",
    response_model=list[schemas.ItemRead],
    tags=["items"],
    summary="List items",
)
def list_items(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum items to return"),
    db: Session = Depends(get_db),
):
    """Return a page of items ordered by id. An out-of-range page is empty."""
    return crud.list_items(db, skip=skip, limit=limit)


@app.get(
    "/items/{item_id}",
    response_model=schemas.ItemRead,
    tags=["items"],
    responses=NOT_FOUND,
    summary="Fetch an item",
)
def read_item(item: models.Item = Depends(get_item_or_404)):
    """Fetch a single item by id."""
    return item


@app.put(
    "/items/{item_id}",
    response_model=schemas.ItemRead,
    tags=["items"],
    responses=NOT_FOUND,
    summary="Update an item",
)
def update_item(
    payload: schemas.ItemUpdate,
    item: models.Item = Depends(get_item_or_404),
    db: Session = Depends(get_db),
):
    """Apply a partial update. Omitted fields keep their current value."""
    return crud.update_item(db, item, payload)


@app.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["items"],
    responses=NOT_FOUND,
    summary="Delete an item",
)
def delete_item(
    item: models.Item = Depends(get_item_or_404), db: Session = Depends(get_db)
):
    """Delete an item. Returns 204 with no body."""
    crud.delete_item(db, item)
