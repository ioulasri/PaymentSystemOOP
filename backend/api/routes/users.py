"""
User management routes.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/me")
async def get_current_user_info():
    """Get current user information."""
    return {"message": "User routes - coming soon"}
