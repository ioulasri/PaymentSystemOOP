"""Base repository with common database operations.

This module provides the BaseRepository class that all specific repositories
inherit from. It encapsulates common database patterns using raw SQL with
psycopg3.

Key Learning Concepts:
----------------------
1. **Connection Pooling**: Reusing database connections for performance
2. **Parameterized Queries**: Using %s placeholders to prevent SQL injection
3. **Context Managers**: Using 'with' statements for automatic resource cleanup
4. **dict_row Factory**: Getting results as dictionaries instead of tuples
5. **Error Handling**: Catching and logging database errors properly

SQL Injection Prevention:
------------------------
WRONG:  f"SELECT * FROM users WHERE id = {user_id}"  # DANGEROUS!
RIGHT:  "SELECT * FROM users WHERE id = %s", (user_id,)  # SAFE!

Always use parameterized queries with %s placeholders and pass values as tuple.
"""

from typing import Any, Dict, List, Optional

import psycopg
from psycopg.rows import dict_row

from src.utils.db_connection import DatabaseConnection
from src.utils.logger import get_logger

logger = get_logger(__name__)


class BaseRepository:
    """Base class for all repository classes.

    Provides common database operations that child repositories inherit.
    Uses raw SQL with psycopg3 for direct PostgreSQL interaction.

    Attributes
    ----------
    table_name : str
        Name of the database table this repository manages.
    db : DatabaseConnection
        Singleton instance managing the connection pool.

    Learning Notes
    --------------
    - All queries use parameterized style with %s for safety
    - Results are returned as dictionaries (dict_row factory)
    - Errors are caught and logged for debugging
    - Connection pool handles connection lifecycle automatically
    """

    def __init__(self, table_name: str):
        """Initialize the repository.

        Parameters
        ----------
        table_name : str
            Name of the database table (e.g., 'users', 'orders').
        """
        self.table_name = table_name
        self.db = DatabaseConnection()
        logger.info(f"Initialized {self.__class__.__name__} for table '{table_name}'")

    def execute_query(
        self, query: str, params: Optional[tuple] = None
    ) -> List[Dict[str, Any]]:
        """Execute a SELECT query that returns multiple rows.

        Learning: This is for queries like:
        - SELECT * FROM users WHERE role = %s
        - SELECT * FROM orders WHERE customer_id = %s

        Parameters
        ----------
        query : str
            SQL SELECT query with %s placeholders.
        params : tuple, optional
            Values to substitute into the query.

        Returns
        -------
        list[dict]
            List of rows as dictionaries. Empty list if no results.

        Example
        -------
        >>> rows = repo.execute_query(
        ...     "SELECT * FROM users WHERE role = %s",
        ...     ('customer',)
        ... )
        >>> print(rows)
        [{'id': 1, 'username': 'john', 'role': 'customer'}, ...]
        """
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(row_factory=dict_row) as cur:
                    cur.execute(query, params or ())
                    result = cur.fetchall()
                    logger.debug(
                        f"Query returned {len(result)} rows from {self.table_name}"
                    )
                    return list(result) if result else []
        except psycopg.Error as e:
            logger.error(f"Query error on {self.table_name}: {e}")
            raise

    def execute_single(
        self, query: str, params: Optional[tuple] = None
    ) -> Optional[Dict[str, Any]]:
        """Execute a query that returns a single row or None.

        Learning: This is for queries like:
        - SELECT * FROM users WHERE id = %s
        - INSERT INTO users (...) VALUES (...) RETURNING *
        - UPDATE users SET ... WHERE id = %s RETURNING *

        The RETURNING clause in PostgreSQL is powerful - it lets you get
        the inserted/updated row immediately without a second query!

        Parameters
        ----------
        query : str
            SQL query with %s placeholders.
        params : tuple, optional
            Values to substitute into the query.

        Returns
        -------
        dict or None
            Single row as dictionary, or None if no result.

        Example
        -------
        >>> user = repo.execute_single(
        ...     "SELECT * FROM users WHERE id = %s",
        ...     (123,)
        ... )
        >>> print(user['username'] if user else 'Not found')
        """
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(row_factory=dict_row) as cur:
                    cur.execute(query, params or ())
                    result = cur.fetchone()
                    if result:
                        logger.debug(
                            f"Query returned single row from {self.table_name}"
                        )
                        return dict(result)
                    else:
                        logger.debug(f"Query returned no rows from {self.table_name}")
                        return None
        except psycopg.Error as e:
            logger.error(f"Query error on {self.table_name}: {e}")
            raise

    def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """Execute an INSERT, UPDATE, or DELETE query.

        Learning: Returns the number of affected rows, which is useful for:
        - Verifying that an UPDATE actually changed something
        - Counting how many rows were deleted
        - Checking if INSERT succeeded (rowcount = 1)

        Parameters
        ----------
        query : str
            SQL INSERT/UPDATE/DELETE query with %s placeholders.
        params : tuple, optional
            Values to substitute into the query.

        Returns
        -------
        int
            Number of rows affected (inserted, updated, or deleted).

        Example
        -------
        >>> count = repo.execute_update(
        ...     "DELETE FROM order_items WHERE order_id = %s",
        ...     (456,)
        ... )
        >>> print(f"Deleted {count} items")
        """
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, params or ())
                    rowcount = cur.rowcount
                    conn.commit()
                    logger.debug(
                        f"Update affected {rowcount} rows in {self.table_name}"
                    )
                    return int(rowcount) if rowcount is not None else 0
        except psycopg.Error as e:
            logger.error(f"Update error on {self.table_name}: {e}")
            raise

    def find_by_id(self, id_value: int) -> Optional[Dict[str, Any]]:
        """Find a single record by its primary key ID.

        Learning: Most tables have an 'id' column as primary key.
        This is the most common query pattern in any application.

        Parameters
        ----------
        id_value : int
            The primary key value to search for.

        Returns
        -------
        dict or None
            The record as a dictionary, or None if not found.

        Example
        -------
        >>> user = repo.find_by_id(1)
        >>> if user:
        ...     print(f"Found user: {user['username']}")
        ... else:
        ...     print("User not found")
        """
        query = f"SELECT * FROM {self.table_name} WHERE id = %s"
        return self.execute_single(query, (id_value,))

    def find_all(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Retrieve all records with optional pagination.

        Learning: LIMIT and OFFSET are used for pagination:
        - Page 1: LIMIT 100 OFFSET 0 (rows 1-100)
        - Page 2: LIMIT 100 OFFSET 100 (rows 101-200)
        - Page 3: LIMIT 100 OFFSET 200 (rows 201-300)

        Always use LIMIT to avoid accidentally loading millions of rows!

        Parameters
        ----------
        limit : int, default=100
            Maximum number of records to return.
        offset : int, default=0
            Number of records to skip (for pagination).

        Returns
        -------
        list[dict]
            List of records as dictionaries.

        Example
        -------
        >>> # Get first page (100 records)
        >>> page1 = repo.find_all(limit=100, offset=0)
        >>> # Get second page
        >>> page2 = repo.find_all(limit=100, offset=100)
        """
        query = f"SELECT * FROM {self.table_name} ORDER BY id LIMIT %s OFFSET %s"
        return self.execute_query(query, (limit, offset))

    def delete_by_id(self, id_value: int) -> bool:
        """Delete a record by its primary key ID.

        Learning: Returns True/False to indicate success/failure.
        This is more Pythonic than returning the rowcount.

        Parameters
        ----------
        id_value : int
            The primary key value of the record to delete.

        Returns
        -------
        bool
            True if a record was deleted, False if not found.

        Example
        -------
        >>> if repo.delete_by_id(999):
        ...     print("Deleted successfully")
        ... else:
        ...     print("Record not found")
        """
        query = f"DELETE FROM {self.table_name} WHERE id = %s"
        affected_rows = self.execute_update(query, (id_value,))
        return affected_rows > 0

    def count(self) -> int:
        """Count total number of records in the table.

        Learning: COUNT(*) is an aggregate function that counts rows.
        PostgreSQL optimizes this query internally.

        Returns
        -------
        int
            Total number of records in the table.

        Example
        -------
        >>> total_users = user_repo.count()
        >>> print(f"Total users: {total_users}")
        """
        query = f"SELECT COUNT(*) as count FROM {self.table_name}"
        result = self.execute_single(query)
        return int(result["count"]) if result else 0
