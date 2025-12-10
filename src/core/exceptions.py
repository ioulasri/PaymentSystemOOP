"""Custom exception classes for the payment system.

This module defines project-specific exceptions for validation,
payment processing, and error handling.
"""

from typing import Optional


class ProjectError(Exception):
    """Raised when input validation fails."""

    def __init__(self, message: str, field: Optional[str] = None) -> None:
        """Initialize ProjectError with message and optional field."""
        self.message = message
        self.field = field
        super().__init__(f"{message}" + (f" (Field): {field}") if field else "")


class ValidationError(ProjectError):
    """Raised when input validation fails."""

    def __init__(self, message: str, field: Optional[str] = None) -> None:
        """Initialize ValidationError with message and optional field."""
        super().__init__(message, field)


class PaymentError(ProjectError):
    """Raised when payment fails."""

    def __init__(self, message: str, field: Optional[str] = None) -> None:
        """Initialize PaymentError with message and optional field."""
        super().__init__(message, field)


class ProjectValueError(ProjectError):
    """Raised when value validation fails."""

    def __init__(self, message: str, field: Optional[str] = None) -> None:
        """Initialize ProjectValueError with message and optional field."""
        super().__init__(message, field)


class OrderError(ProjectError):
    """Raised when order fails."""

    def __init__(self, message: str, field: Optional[str] = None) -> None:
        """Initialize OrderError with message and optional field."""
        super().__init__(message, field)


class ProjectTypeError(ProjectError):
    """Raised when type validation fails."""

    def __init__(self, message: str, field: Optional[str] = None) -> None:
        """Initialize ProjectTypeError with message and optional field."""
        super().__init__(message, field)
