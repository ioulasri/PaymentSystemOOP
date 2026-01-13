"""
Pydantic schemas for Item API endpoints.
Converts between API JSON and your existing Item model.
"""

from pydantic import BaseModel, Field
from decimal import Decimal

# Import your existing model
from src.models.item import Item


class ItemCreate(BaseModel):
    """Schema for creating an item (API input)."""
    name: str = Field(..., min_length=1, max_length=100)
    price: Decimal = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    description: str = ""


class ItemUpdate(BaseModel):
    """Schema for updating an item (API input)."""
    name: str | None = None
    price: Decimal | None = Field(None, gt=0)
    stock: int | None = Field(None, ge=0)
    description: str | None = None


class ItemResponse(BaseModel):
    """Schema for item response (API output)."""
    item_id: str
    name: str
    price: Decimal
    stock: int
    description: str

    class Config:
        from_attributes = True

    @staticmethod
    def from_item(item: Item) -> "ItemResponse":
        """Convert Item model to API response."""
        return ItemResponse(
            item_id=item.item_id,
            name=item.name,
            price=Decimal(str(item.price)),
            stock=item.stock,
            description=getattr(item, 'description', '')  # If description exists
        )

    def to_item(self) -> Item:
        """Convert API input to Item model."""
        item = Item(self.name)
        item.price = float(self.price)
        item.stock = self.stock
        if hasattr(item, 'description'):
            item.description = self.description
        return item