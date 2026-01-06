"""
Database Initialization Script.

This script initializes the payment system database by:
1. Executing the schema.sql file to create all tables
2. Optionally loading sample data for testing

Usage:
    python database/init_db.py
    python database/init_db.py --with-sample-data
"""

import argparse
import sys
from pathlib import Path

import psycopg

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import get_logger  # noqa: E402

logger = get_logger(__name__)


def read_sql_file(file_path: Path) -> str:
    """
    Read SQL file content.

    Args:
        file_path: Path to the SQL file

    Returns:
        SQL file content as string
    """
    if not file_path.exists():
        raise FileNotFoundError(f"SQL file not found: {file_path}")

    return file_path.read_text(encoding="utf-8")


def execute_sql_script(connection_string: str, sql_script: str) -> None:
    """
    Execute a SQL script.

    Args:
        connection_string: PostgreSQL connection string
        sql_script: SQL commands to execute
    """
    try:
        with psycopg.connect(connection_string) as conn:
            with conn.cursor() as cur:
                cur.execute(sql_script)
                conn.commit()
        logger.info("SQL script executed successfully")
    except Exception as e:
        logger.error(f"Error executing SQL script: {e}")
        raise


def initialize_database(connection_string: str, with_sample_data: bool = False) -> None:
    """
    Initialize the database with schema and optionally sample data.

    Args:
        connection_string: PostgreSQL connection string
        with_sample_data: If True, load sample data after schema creation
    """
    database_dir = Path(__file__).parent
    schema_file = database_dir / "schema.sql"

    logger.info("Starting database initialization...")

    # Execute schema
    logger.info(f"Executing schema from: {schema_file}")
    schema_sql = read_sql_file(schema_file)
    execute_sql_script(connection_string, schema_sql)

    logger.info("✓ Database schema created successfully")

    if with_sample_data:
        logger.info("Loading sample data...")
        load_sample_data(connection_string)
        logger.info("✓ Sample data loaded successfully")

    logger.info("✓ Database initialization complete!")


def load_sample_data(connection_string: str) -> None:
    """
    Load sample data into the database for testing.

    Args:
        connection_string: PostgreSQL connection string
    """
    sample_data_sql = """
    -- Sample Users
    INSERT INTO users (username, email, hashed_password, role) VALUES
        ('john_doe', 'john@example.com', 'hashed_password_123', 'customer'),
        ('jane_smith', 'jane@example.com', 'hashed_password_456', 'customer'),
        ('admin_user', 'admin@example.com', 'hashed_password_789', 'admin');

    -- Sample Customers
    INSERT INTO customers (user_id, address, phone) VALUES
        (1, '123 Main St, New York, NY 10001', '555-0101'),
        (2, '456 Oak Ave, Los Angeles, CA 90001', '555-0102');

    -- Sample Items
    INSERT INTO items (name, description, price, stock) VALUES
        ('MacBook Pro 16"', 'Apple MacBook Pro 16-inch with M3 chip', 2499.99, 15),
        ('iPhone 15 Pro', 'Latest iPhone with A17 Pro chip', 999.99, 50),
        ('AirPods Pro', 'Wireless earbuds with active noise cancellation', 249.99, 100),
        ('Magic Mouse', 'Apple Magic Mouse wireless', 79.99, 75),
        ('USB-C Cable', 'High-quality USB-C charging cable', 19.99, 200);

    -- Sample Orders
    INSERT INTO orders (customer_id, total, status) VALUES
        (1, 2779.98, 'delivered'),
        (1, 269.98, 'confirmed'),
        (2, 1249.98, 'processing');

    -- Sample Order Items
    INSERT INTO order_items (order_id, item_id, quantity, price) VALUES
        (1, 1, 1, 2499.99),
        (1, 4, 2, 79.99),
        (1, 5, 1, 19.99),
        (2, 3, 1, 249.99),
        (2, 5, 1, 19.99),
        (3, 2, 1, 999.99),
        (3, 3, 1, 249.99);

    -- Sample Payments
    INSERT INTO payments (order_id, amount, method, status, transaction_id) VALUES
        (1, 2779.98, 'credit_card', 'completed', 'TXN-2024-001'),
        (2, 269.98, 'paypal', 'completed', 'TXN-2024-002'),
        (3, 1249.98, 'crypto', 'processing', 'TXN-2024-003');
    """

    execute_sql_script(connection_string, sample_data_sql)


def verify_tables(connection_string: str) -> bool:
    """
    Verify that all tables were created successfully.

    Args:
        connection_string: PostgreSQL connection string

    Returns:
        True if all tables exist, False otherwise
    """
    expected_tables = [
        "users",
        "customers",
        "items",
        "orders",
        "order_items",
        "payments",
    ]

    query = """
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_type = 'BASE TABLE'
    ORDER BY table_name;
    """

    try:
        with psycopg.connect(connection_string) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                tables = [row[0] for row in cur.fetchall()]

        print("\n" + "=" * 60)
        print("DATABASE VERIFICATION")
        print("=" * 60)

        for table in expected_tables:
            status = "✓" if table in tables else "✗"
            print(f"{status} {table}")

        print("=" * 60)

        missing_tables = set(expected_tables) - set(tables)
        if missing_tables:
            logger.error(f"Missing tables: {missing_tables}")
            return False

        logger.info("All tables verified successfully")
        return True

    except Exception as e:
        logger.error(f"Error verifying tables: {e}")
        return False


def main() -> None:
    """Main entry point for database initialization."""
    parser = argparse.ArgumentParser(
        description="Initialize the payment system database"
    )
    parser.add_argument(
        "--connection-string",
        "-c",
        default="postgresql://localhost:5432/payment_system_db",
        help=(
            "PostgreSQL connection string "
            "(default: postgresql://localhost:5432/payment_system_db)"
        ),
    )
    parser.add_argument(
        "--with-sample-data",
        "-s",
        action="store_true",
        help="Load sample data after schema creation",
    )
    parser.add_argument(
        "--verify-only",
        "-v",
        action="store_true",
        help="Only verify existing tables without creating new ones",
    )

    args = parser.parse_args()

    try:
        if args.verify_only:
            verify_tables(args.connection_string)
        else:
            initialize_database(args.connection_string, args.with_sample_data)
            verify_tables(args.connection_string)
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
