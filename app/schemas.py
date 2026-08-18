"""Pydantic request/response models."""

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ItemBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    price: float = Field(default=0.0, ge=0)
    in_stock: bool = True


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    """Partial update: omitted fields keep their current value.

    Only ``description`` is nullable in the database, so an explicit ``null``
    for any other field is rejected here as a 422. Letting it through would
    reach the database as a NOT NULL violation and surface as a 500.
    """

    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    price: float | None = Field(default=None, ge=0)
    in_stock: bool | None = None

    @field_validator("name", "price", "in_stock", mode="before")
    @classmethod
    def _reject_explicit_null(cls, value: object) -> object:
        # Only runs for keys the client actually sent; Pydantic skips
        # validation of defaults, so an omitted field stays None untouched.
        if value is None:
            raise ValueError("cannot be null; omit the field to leave it unchanged")
        return value


class ItemRead(ItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime

    @field_validator("created_at", "updated_at")
    @classmethod
    def _ensure_utc(cls, value: datetime) -> datetime:
        # SQLite has no native timestamp type and drops tzinfo on write, so
        # values read back are naive. They are always stored as UTC, and
        # normalising here keeps responses offset-aware on every backend.
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)
