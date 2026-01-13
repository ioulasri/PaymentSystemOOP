"""
Pydantic schemas for Order API endpoints.
Converts between API JSON and your existing Order/Item models.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

# Import your existing models
from src.models.order import Order
from src.models.item import Item


class ItemInOrder(BaseModel):
    """Item within an order (API representation)."""
    item_id: str
    name: str
    price: Decimal
    quantity: int = 1

    @staticmethod
    def from_item(item: Item, quantity: int = 1) -> "ItemInOrder":
        """Convert Item model to API response."""
        return ItemInOrder(
            item_id=item.item_id,
            name=item.name,
            price=Decimal(str(item.price)),
            quantity=quantity
        )


class OrderCreate(BaseModel):
    """Schema for creating an order (API input)."""
    items: List[ItemInOrder] = Field(..., min_items=1)


class OrderUpdate(BaseModel):
    """Schema for updating order status (API input)."""
    status: str = Field(..., pattern="^(pending|processing|completed|cancelled)$")


class OrderResponse(BaseModel):
    """Schema for order response (API output)."""
    order_id: str
   