"""Repository layer for database operations.

This package contains repository classes that handle all database interactions
using raw SQL with psycopg3. Each repository corresponds to a database table
and provides CRUD (Create, Read, Update, Delete) operations.

The repository pattern provides:
- Abstraction over database operations
- Centralized query management
- Easier testing through dependency injection
- Clear separation between business logic and data access
"""

from src.repositories.base_repository import BaseRepository

__all__ = ["BaseRepository"]
