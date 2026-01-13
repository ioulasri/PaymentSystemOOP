"""
Pydantic schemas for User API endpoints.
These schemas validate API requests/responses and convert to/from existing models.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# Import your existing models
from src.models.customer import Customer
from src.models.admin import Admin


class UserBase(BaseModel):
    """Base user schema."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    """Schema for user registration (API input)."""
    password: str = Field(..., min_length=8, max_length=100)
    role: Optional[str] = "customer"  # customer or admin


class UserLogin(BaseModel):
    """Schema for user login (API input)."""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Schema for user response (API output - public data only)."""
    id: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

    @staticmethod
    def from_customer(customer: Customer) -> "UserResponse":
        """Convert Customer model to API response."""
        return UserResponse(
            id=customer._user_id,
            username=customer._name,
            email=customer.email,
            role="customer",
            is_active=True,
            created_at=datetime.utcnow()  # TODO: Get from DB
        )

    @staticmethod
    def from_admin(admin: Admin) -> "UserResponse":
        """Convert Admin model to API response."""
        return UserResponse(
            id=admin._user_id,
            username=admin._name,
            email=admin.email,
            role="admin",
            is_active=True,
            created_at=datetime.utcnow()  # TODO: Get from DB
        )


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse