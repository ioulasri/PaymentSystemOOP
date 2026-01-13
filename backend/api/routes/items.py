"""
Item/Product catalog routes.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_items():
    """Get all items."""
    return {"message": "Item routes - coming soon"}
