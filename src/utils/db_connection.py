"""
Database Connection Manager for Payment System.

This module provides connection pooling and management using psycopg3.
It handles connection lifecycle, pooling, and provides context managers
for safe database operations.

Key Concepts:
    - Connection Pool: Reuses database connections instead of creating new ones
    - Context Manager: Ensures connections are properly returned to the pool
    - Thread-safe: Can be used in multi-threaded applications
"""

import os
from contextlib import contextmanager
from typing import Generator, Optional

import psycopg
from psycopg.pool import ConnectionPool
from psycopg.rows import dict_row

from src.utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseConnection:
    """
    Manages PostgreSQL connections using connection pooling.

    This class implements the Singleton pattern to ensure only one pool exists.
    The pool maintains a set of reusable database connections.

    Attributes:
        _pool: The connection pool instance (class variable)
        _connection_string: PostgreSQL connection string
    """

    _pool: Optional[ConnectionPool] = None
    _connection_string: Optional[str] = None

    @classmethod
    def initialize(
        cls,
        connection_string: Optional[str] = None,
        min_size: int = 2,
        max_size: int = 10,
    ) -> None:
        """
        Initialize the connection pool.

        Args:
            connection_string: PostgreSQL connection string (DSN format).
                             If None, reads from DATABASE_URL environment variable.
            min_size: Minimum number of connections to maintain in the pool
            max_size: Maximum number of connections allowed in the pool

        Example:
            >>> DatabaseConnection.initialize(
            ...     "postgresql://user:pass@localhost:5432/payment_system_db",
            ...     min_size=2,
            ...     max_size=10
            ... )

        Notes:
            - Call this once at application startup
            - The pool is thread-safe and can be used across threads
            - Connections are created lazily as needed
        """
        if cls._pool is not None:
            logger.warning(
                "Connection pool already initialized. Closing existing pool."
            )
            cls.close_pool()

        # Get connection string from parameter or environment
        if connection_string is None:
            connection_string = os.getenv(
                "DATABASE_URL", "postgresql://localhost:5432/payment_system_db"
            )

        cls._connection_string = connection_string

        try:
            # Create connection pool
            cls._pool = ConnectionPool(
                conninfo=connection_string,
                min_size=min_size,
                max_size=max_size,
                kwargs={"row_factory": dict_row},  # Return rows as dictionaries
                timeout=30,  # Connection timeout in seconds
            )
            logger.info(
                "Database connection pool initialized",
                extra={
                    "min_size": min_size,
                    "max_size": max_size,
                    "database": connection_string.split("/")[-1].split("?")[0],
                },
            )
        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            raise

    @classmethod
    def get_pool(cls) -> ConnectionPool:
        """
        Get the connection pool instance.

        Returns:
            The connection pool

        Raises:
            RuntimeError: If pool is not initialized
        """
        if cls._pool is None:
            raise RuntimeError(
                "Database connection pool not initialized. "
                "Call DatabaseConnection.initialize() first."
            )
        return cls._pool

    @classmethod
    @contextmanager
    def get_connection(cls) -> Generator[psycopg.Connection, None, None]:
        """
        Get a connection from the pool using a context manager.

        This is the recommended way to get connections. The connection
        is automatically returned to the pool when the context exits.

        Yields:
            A database connection from the pool

        Example:
            >>> with DatabaseConnection.get_connection() as conn:
            ...     with conn.cursor() as cur:
            ...         cur.execute("SELECT * FROM users")
            ...         users = cur.fetchall()

        Notes:
            - Connection is automatically returned to pool
            - Exceptions are propagated after cleanup
            - Connection is NOT automatically committed
        """
        pool = cls.get_pool()
        conn = pool.getconn()
        try:
            yield conn
        finally:
            pool.putconn(conn)

    @classmethod
    @contextmanager
    def get_cursor(cls, commit: bool = False) -> Generator[psycopg.Cursor, None, None]:
        """
        Get a cursor with automatic connection and transaction management.

        Args:
            commit: If True, automatically commits on success

        Yields:
            A database cursor

        Example:
            >>> # Read-only query
            >>> with DatabaseConnection.get_cursor() as cur:
            ...     cur.execute("SELECT * FROM users WHERE id = %s", (1,))
            ...     user = cur.fetchone()

            >>> # Write query with auto-commit
            >>> with DatabaseConnection.get_cursor(commit=True) as cur:
            ...     cur.execute(
            ...         "INSERT INTO users (username, email) VALUES (%s, %s)",
            ...         ("john", "john@example.com")
            ...     )

        Notes:
            - Connection is automatically returned to pool
            - If commit=True, transaction is committed on success
            - If exception occurs, transaction is rolled back
        """
        pool = cls.get_pool()
        conn = pool.getconn()
        try:
            with conn.cursor() as cur:
                yield cur
                if commit:
                    conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            pool.putconn(conn)

    @classmethod
    def execute_query(cls, query: str, params: tuple = ()) -> list[dict]:
        """
        Execute a SELECT query and return all results.

        Args:
            query: SQL SELECT query with %s placeholders
            params: Query parameters (uses %s placeholders, NOT f-strings!)

        Returns:
            List of dictionaries (one per row)

        Example:
            >>> results = DatabaseConnection.execute_query(
            ...     "SELECT * FROM users WHERE role = %s",
            ...     ("customer",)
            ... )
            >>> for user in results:
            ...     print(user['username'])
        """
        with cls.get_cursor() as cur:
            cur.execute(query, params)
            result = cur.fetchall()
            return list(result) if result else []

    @classmethod
    def execute_single(cls, query: str, params: tuple = ()) -> Optional[dict]:
        """
        Execute a SELECT query and return a single result.

        Args:
            query: SQL SELECT query
            params: Query parameters

        Returns:
            Dictionary representing the row, or None if not found

        Example:
            >>> user = DatabaseConnection.execute_single(
            ...     "SELECT * FROM users WHERE id = %s",
            ...     (1,)
            ... )
            >>> if user:
            ...     print(user['username'])
        """
        with cls.get_cursor() as cur:
            cur.execute(query, params)
            result = cur.fetchone()
            return dict(result) if result else None

    @classmethod
    def execute_update(cls, query: str, params: tuple = ()) -> int:
        """
        Execute an INSERT/UPDATE/DELETE query.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            Number of rows affected

        Example:
            >>> rows_updated = DatabaseConnection.execute_update(
            ...     "UPDATE users SET is_active = %s WHERE id = %s",
            ...     (False, 1)
            ... )
        """
        with cls.get_cursor(commit=True) as cur:
            cur.execute(query, params)
            rowcount = cur.rowcount
            return int(rowcount) if rowcount is not None else 0

    @classmethod
    def close_pool(cls) -> None:
        """
        Close the connection pool and all connections.

        Call this when shutting down the application.

        Example:
            >>> # At application shutdown
            >>> DatabaseConnection.close_pool()
        """
        if cls._pool is not None:
            cls._pool.close()
            cls._pool = None
            logger.info("Database connection pool closed")

    @classmethod
    def get_pool_stats(cls) -> dict:
        """
        Get statistics about the connection pool.

        Returns:
            Dictionary with pool statistics

        Example:
            >>> stats = DatabaseConnection.get_pool_stats()
            >>> print(f"Available connections: {stats['available']}")
        """
        if cls._pool is None:
            return {"status": "not initialized"}

        pool = cls._pool
        return {
            "status": "active",
            "size": pool.size,
            "min_size": pool.min_size,
            "max_size": pool.max_size,
        }
