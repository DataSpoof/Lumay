"""FastAPI application exposing CRUD endpoints for items."""

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import engine, get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Lumay API",
    description="A simple CRUD API built with FastAPI.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/items",
    response_model=schemas.ItemRead,
    status_code=status.HTTP_201_CREATED,
    tags=["items"],
)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    return crud.create_item(db, item)


@app.get("/items", response_model=list[schemas.ItemRead], tags=["items"])
def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return crud.list_items(db, skip=skip, limit=limit)


@app.get("/items/{item_id}", response_model=schemas.ItemRead, tags=["items"])
def read_item(item_id: int, db: Session = Depends(get_db)):
    db_item = crud.get_item(db, item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item


@app.put("/items/{item_id}", response_model=schemas.ItemRead, tags=["items"])
def update_item(
    item_id: int, item: schemas.ItemUpdate, db: Session = Depends(get_db)
):
    db_item = crud.get_item(db, item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return crud.update_item(db, db_item, item)


@app.delete(
    "/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["items"]
)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = crud.get_item(db, item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    crud.delete_item(db, db_item)
