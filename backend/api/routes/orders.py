"""
Order management routes.
Uses your existing Order and Item models.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from schemas.order import OrderCreate, OrderResponse, OrderUpdate
from api.routes.auth import get_current_user
from src.models.customer import Customer  # YOUR existing model
from src.models.order import Order  # YOUR existing model
from src.models.item import Item  # YOUR existing model

router = APIRouter()


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new order.
    
    - Requires authentication
    - Creates order with items
    - Returns order details
    """
    try:
        # Create customer using YOUR existing Customer model
        customer = Customer(current_user["email"], current_user["email"])
        
        # Create order using YOUR existing Order model
        order = Order(customer=customer)
        
        # Add items to order using YOUR existing Item model
        for item_data in order_data.items:
            item = Item(item_data.name)
            item.price = float(item_data.price)
            item.stock = item_data.quantity
            # YOUR Order model's add_item method
            order.add_item(item, quantity=item_data.quantity)
        
        # TODO: Save to database
        # order_repo = OrderRepository()
        # order_repo.save(order)
        
        # Convert YOUR Order model to API response using schema helper
        return OrderResponse.from_order(order)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order creation failed: {str(e)}"
        )


@router.get("/", response_model=List[OrderResponse])
async def get_orders(current_user: dict = Depends(get_current_user)):
    """
    Get all orders for current user.
    
    - Returns user's order history
    """
    # TODO: Fetch from database filtered by user
    return []


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get order by ID."""
    # TODO: Fetch from database and verify ownership
    raise HTTPException(status_code=404, detail="Order not found")


@router.patch("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: str,
    update_data: OrderUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update order status (admin only)."""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # TODO: Update in database
    raise HTTPException(status_code=404, detail="Order not found")