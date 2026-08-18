"""Database operations, kept separate from the HTTP layer."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas


def list_items(db: Session, skip: int = 0, limit: int = 100) -> list[models.Item]:
    stmt = select(models.Item).order_by(models.Item.id).offset(skip).limit(limit)
    return list(db.scalars(stmt))


def get_item(db: Session, item_id: int) -> models.Item | None:
    return db.get(models.Item, item_id)


def create_item(db: Session, item: schemas.ItemCreate) -> models.Item:
    db_item = models.Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_item(
    db: Session, db_item: models.Item, item: schemas.ItemUpdate
) -> models.Item:
    # exclude_unset keeps fields the client omitted at their current value.
    for field, value in item.model_dump(exclude_unset=True).items():
        setattr(db_item, field, value)
    db.commit()
    db.refresh(db_item)
    return db_item


def delete_item(db: Session, db_item: models.Item) -> None:
    db.delete(db_item)
    db.commit()
