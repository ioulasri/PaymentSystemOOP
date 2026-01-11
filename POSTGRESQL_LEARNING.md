# PostgreSQL Integration Learning Journey

## 📚 Complete Learning Path: From Setup to Repository Pattern

This document chronicles your learning journey integrating PostgreSQL with the Payment System OOP project using **raw SQL** and **psycopg3** (no ORM).

---

## Phase 1: Project Setup & Database Design

### Decision: Why PostgreSQL with psycopg?

**Your Goal:** Learn PostgreSQL deeply by writing raw SQL queries instead of using an ORM like SQLAlchemy.

**Benefits of this approach:**
- 🎯 **Deeper SQL knowledge**: You write every query yourself
- 🚀 **Better performance understanding**: See exactly what queries run
- 🔍 **Query optimization skills**: Learn EXPLAIN, indexes, etc.
- 💪 **Database-agnostic thinking**: SQL concepts transfer to any database

**psycopg3 advantages:**
- Modern Python PostgreSQL adapter
- Native support for Python 3.10+ type hints
- Async support (for future learning)
- Better connection pooling
- dict_row factory for clean results

---

### Step 1: Database Schema Design

**File:** `database/schema.sql` (263 lines)

#### What We Learned: Database Design Principles

**1. Tables and Relationships**

Our payment system has 6 main tables:

```
users (authentication & basic info)
  ↓ one-to-one
customers (customer-specific details)
  ↓ one-to-many
orders (purchase orders)
  ↓ many-to-many (through order_items)
items (products in catalog)

orders
  ↓ one-to-many
payments (transaction records)
```

**Key SQL Concepts Learned:**

##### Primary Keys
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,  -- Auto-incrementing integer
    username VARCHAR(50) UNIQUE NOT NULL,
    -- SERIAL = integer with auto-increment sequence
    -- PRIMARY KEY = unique identifier + indexed
);
```

**What SERIAL does:**
1. Creates an integer column
2. Creates a sequence: `users_id_seq`
3. Sets default value to `nextval('users_id_seq')`
4. Automatically increments: 1, 2, 3, 4...

##### Foreign Keys & Cascading

```sql
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL,
    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE  -- If user deleted, delete customer too
);

CREATE TABLE orders (
    customer_id INTEGER NOT NULL,
    FOREIGN KEY (customer_id)
        REFERENCES customers(id)
        ON DELETE CASCADE
);

CREATE TABLE order_items (
    item_id INTEGER NOT NULL,
    FOREIGN KEY (item_id)
        REFERENCES items(id)
        ON DELETE RESTRICT  -- Can't delete item if in orders
);
```

**CASCADE vs RESTRICT:**
- `ON DELETE CASCADE`: Delete related records automatically
- `ON DELETE RESTRICT`: Prevent deletion if related records exist
- `ON DELETE SET NULL`: Set foreign key to NULL
- `ON DELETE NO ACTION`: Like RESTRICT but checked at end of transaction

**Our business logic:**
- User deleted → Customer deleted → Orders deleted ✅
- Item deleted when in orders → Blocked ❌ (preserve order history)

##### ENUM Types (PostgreSQL-specific)

```sql
-- Define allowed values at database level
CREATE TYPE user_role_enum AS ENUM ('customer', 'admin', 'guest');
CREATE TYPE payment_method_enum AS ENUM ('credit_card', 'paypal', 'crypto');
CREATE TYPE order_status_enum AS ENUM ('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled');
CREATE TYPE payment_status_enum AS ENUM ('pending', 'processing', 'completed', 'failed', 'refunded');

CREATE TABLE users (
    role user_role_enum NOT NULL DEFAULT 'customer'
    -- Only 'customer', 'admin', or 'guest' allowed!
);
```

**Why use ENUMs?**
- ✅ Data integrity at database level
- ✅ Prevents typos ('custoemr' rejected)
- ✅ Self-documenting code
- ✅ Smaller storage than VARCHAR
- ❌ Harder to modify (need ALTER TYPE to add values)

##### CHECK Constraints

```sql
CREATE TABLE items (
    price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    -- Price must be non-negative

    stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0)
    -- Stock can't be negative
);

CREATE TABLE order_items (
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    -- Must order at least 1 item

    price NUMERIC(10, 2) NOT NULL CHECK (price >= 0)
);
```

**CHECK vs Application Validation:**
- Both should be used together
- Database: Last line of defense
- Application: Better error messages for users

##### Indexes (Performance)

```sql
-- Index foreign keys for fast JOINs
CREATE INDEX idx_customers_user_id ON customers(user_id);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_item_id ON order_items(item_id);
CREATE INDEX idx_payments_order_id ON payments(order_id);

-- Index frequently queried columns
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_method ON payments(method);
CREATE INDEX idx_payments_transaction_id ON payments(transaction_id);

-- Composite index for date range queries
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_payments_created_at ON payments(created_at);
```

**When to add indexes:**
- ✅ Foreign key columns (used in JOINs)
- ✅ Columns in WHERE clauses
- ✅ Columns in ORDER BY clauses
- ✅ Frequently searched columns
- ❌ Small tables (< 1000 rows)
- ❌ Columns with low cardinality (many duplicates)
- ❌ Write-heavy tables (indexes slow down INSERT/UPDATE)

**How to check if index is used:**
```sql
EXPLAIN ANALYZE SELECT * FROM orders WHERE customer_id = 1;
-- Look for "Index Scan" (good) vs "Seq Scan" (slow)
```

##### Triggers & Functions

```sql
-- Function to update timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger: Run before UPDATE on users
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

**What happens:**
1. User runs: `UPDATE users SET email = 'new@email.com' WHERE id = 1`
2. Trigger activates BEFORE the UPDATE
3. Function sets `updated_at = CURRENT_TIMESTAMP`
4. Row is saved with both changes

**Triggers we created:**
- `users.updated_at` - Auto-update on user changes
- `customers.updated_at` - Auto-update on customer changes
- `orders.updated_at` - Auto-update on order changes
- `items.updated_at` - Auto-update on item changes

##### Timestamps

```sql
CREATE TABLE users (
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

**TIMESTAMP types:**
- `TIMESTAMP` - No timezone (2025-01-11 14:30:00)
- `TIMESTAMPTZ` - With timezone (2025-01-11 14:30:00+00)
- `DATE` - Date only (2025-01-11)
- `TIME` - Time only (14:30:00)

**Best practice:** Use `TIMESTAMPTZ` for production apps (handles timezones)

---

### Step 2: Connection Pooling

**File:** `src/utils/db_connection.py` (307 lines)

#### What We Learned: Database Connection Management

##### The Problem: Connection Overhead

**Opening a database connection is expensive:**

```python
# Each connection takes ~50ms
import time
start = time.time()
conn = psycopg.connect("postgresql://localhost/mydb")
print(f"Time: {(time.time() - start) * 1000}ms")  # ~50ms
```

**What happens during connection:**
1. TCP socket creation (network handshake)
2. PostgreSQL authentication (username/password check)
3. Session initialization (settings, parameters)
4. Memory allocation

**For 1000 queries without pooling:**
```python
for i in range(1000):
    conn = psycopg.connect(...)  # 50ms × 1000 = 50 seconds wasted!
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (i,))
    conn.close()
```

##### The Solution: Connection Pool

```python
from psycopg.pool import ConnectionPool

# Create pool once at startup
pool = ConnectionPool(
    conninfo="postgresql://localhost/mydb",
    min_size=5,    # Keep 5 connections ready
    max_size=20,   # Allow up to 20 connections
)

# Reuse connections from pool
for i in range(1000):
    with pool.connection() as conn:  # Instant! Reuses existing connection
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE id = %s", (i,))
    # Connection returns to pool automatically
```

**Performance improvement: 50 seconds → 1 second! (50x faster)**

##### Our Implementation: Singleton Pattern

```python
class DatabaseConnection:
    """Singleton connection pool manager."""

    _instance = None  # Single shared instance
    _pool = None      # Shared connection pool

    def __new__(cls):
        """Ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self, connection_string: str, min_size: int = 5, max_size: int = 20):
        """Create connection pool (called once at startup)."""
        if self._pool is None:
            self._pool = ConnectionPool(
                conninfo=connection_string,
                min_size=min_size,
                max_size=max_size
            )
```

**Why Singleton?**
- Only one pool for entire application
- Prevents creating multiple pools (wastes resources)
- Shared across all repository instances

**Usage:**
```python
# First call creates the pool
db = DatabaseConnection()
db.initialize("postgresql://localhost/payment_system_db")

# Subsequent calls return same instance
db2 = DatabaseConnection()  # Same pool!
assert db is db2  # True - same object
```

##### Context Managers for Safety

```python
@contextmanager
def get_connection(self):
    """Get connection from pool, return it automatically."""
    conn = self._pool.getconn()  # Get from pool
    try:
        yield conn  # Give to caller
    finally:
        self._pool.putconn(conn)  # Always return to pool
```

**Why context managers?**

```python
# Without context manager (risky):
conn = pool.getconn()
try:
    cur = conn.cursor()
    cur.execute("SELECT ...")
    pool.putconn(conn)  # Must remember this!
except Exception:
    pool.putconn(conn)  # And this!
    raise

# With context manager (safe):
with pool.connection() as conn:
    cur = conn.cursor()
    cur.execute("SELECT ...")
# Connection automatically returned even if exception occurs!
```

##### Helper Methods We Created

```python
def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
    """Execute SELECT query, return list of dicts."""
    with self.get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(query, params or ())
            return list(cur.fetchall())

def execute_single(self, query: str, params: tuple = None) -> Optional[Dict]:
    """Execute query, return single dict or None."""
    with self.get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(query, params or ())
            result = cur.fetchone()
            return dict(result) if result else None

def execute_update(self, query: str, params: tuple = None) -> int:
    """Execute INSERT/UPDATE/DELETE, return affected rows."""
    with self.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            conn.commit()  # Don't forget to commit!
            return cur.rowcount
```

---

### Step 3: Database Initialization

**File:** `database/init_db.py` (241 lines)

#### What We Learned: Database Setup Automation

##### Script Features

```python
def initialize_database(connection_string: str, with_sample_data: bool = False):
    """
    1. Read schema.sql file
    2. Execute all CREATE statements
    3. Optionally load sample data
    4. Verify tables exist
    """
```

##### Sample Data for Testing

```sql
-- 3 sample users
INSERT INTO users (username, email, hashed_password, role) VALUES
    ('john_doe', 'john@example.com', 'hashed_password_123', 'customer'),
    ('jane_smith', 'jane@example.com', 'hashed_password_456', 'customer'),
    ('admin_user', 'admin@example.com', 'hashed_password_789', 'admin');

-- 2 sample customers
INSERT INTO customers (user_id, address, phone) VALUES
    (1, '123 Main St, New York, NY 10001', '555-0101'),
    (2, '456 Oak Ave, Los Angeles, CA 90001', '555-0102');

-- 5 sample items
INSERT INTO items (name, description, price, stock) VALUES
    ('MacBook Pro 16"', 'Apple MacBook Pro with M3 chip', 2499.99, 15),
    ('iPhone 15 Pro', 'Latest iPhone with A17 Pro chip', 999.99, 50),
    -- ...

-- 3 sample orders with items
-- 3 sample payments
```

**Why sample data?**
- Quick testing without manual data entry
- Demonstrates relationships between tables
- Provides realistic scenarios

##### Usage

```bash
# Initialize with sample data
python database/init_db.py --with-sample-data

# Just verify tables exist
python database/init_db.py --verify-only

# Custom connection string
python database/init_db.py -c "postgresql://user:pass@host/db"
```

---

## Phase 2: PostgreSQL Security & Privileges

### The Permission Problem You Encountered

**Symptom:** Could connect to database but couldn't query tables

```sql
payment_system_db=# SELECT * FROM users;
ERROR:  permission denied for table users
```

#### What We Learned: PostgreSQL Permission System

##### Understanding PostgreSQL Objects Hierarchy

```
PostgreSQL Server (Cluster)
  └── Databases
        └── Schemas (default: public)
              └── Tables
                    └── Columns
                          └── Privileges (SELECT, INSERT, UPDATE, DELETE)
```

##### Default PostgreSQL Behavior

**When you create a table:**
```sql
CREATE TABLE users (...);
-- Created by user: postgres (or whoever ran the command)
-- Owner: postgres
-- Other users: NO access by default!
```

**This is by design for security:**
- Banking apps: Prevent developer from seeing customer data
- Multi-tenant apps: Separate user data
- Auditing: Track who accesses what

##### Our Solution: GRANT Privileges

```sql
-- Grant all privileges on existing tables
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO CURRENT_USER;

-- Grant privileges on sequences (for SERIAL columns)
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO CURRENT_USER;

-- Make future tables automatically grant privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT ALL ON TABLES TO CURRENT_USER;
```

##### Understanding GRANT Syntax

```sql
GRANT privilege_type ON object_type TO user_or_role;
```

**Privilege types:**
- `SELECT` - Read data
- `INSERT` - Add rows
- `UPDATE` - Modify rows
- `DELETE` - Remove rows
- `TRUNCATE` - Empty table
- `REFERENCES` - Create foreign keys
- `TRIGGER` - Create triggers
- `ALL PRIVILEGES` - All of the above

**Examples:**
```sql
-- Grant SELECT only (read-only user)
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;

-- Grant everything
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_user;

-- Revoke privileges
REVOKE DELETE ON users FROM app_user;
```

##### Checking Your Privileges

```sql
-- See what you can do
SELECT
    table_name,
    privilege_type
FROM information_schema.table_privileges
WHERE grantee = CURRENT_USER
    AND table_schema = 'public'
ORDER BY table_name, privilege_type;
```

---

## Phase 3: Repository Pattern

### Step 4: Base Repository

**File:** `src/repositories/base_repository.py` (307 lines)

#### What We Learned: Software Design Patterns

##### The Repository Pattern

**Problem:** Database code scattered everywhere

```python
# payment_processor.py
conn = psycopg.connect(...)
cur = conn.cursor()
cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
user = cur.fetchone()
conn.close()

# customer.py
conn = psycopg.connect(...)
cur = conn.cursor()
cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
user = cur.fetchone()
conn.close()

# admin.py
conn = psycopg.connect(...)
cur = conn.cursor()
cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
user = cur.fetchone()
conn.close()

# Code duplication! Maintenance nightmare!
```

**Solution:** Centralize database operations

```python
# user_repository.py
class UserRepository:
    def find_by_id(self, user_id: int) -> Optional[Dict]:
        query = "SELECT * FROM users WHERE id = %s"
        return self.execute_single(query, (user_id,))

# Now everywhere just uses:
user_repo = UserRepository()
user = user_repo.find_by_id(123)
```

##### Our BaseRepository Methods

###### 1. execute_query() - Multiple Rows

```python
def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
    """For SELECT queries that return 0+ rows."""
    with self.db.get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(query, params or ())
            result = cur.fetchall()
            return list(result) if result else []
```

**Use cases:**
```python
# Get all customers
customers = repo.execute_query("SELECT * FROM customers")

# Get customers in a city
ny_customers = repo.execute_query(
    "SELECT * FROM customers WHERE city = %s",
    ('New York',)
)

# Empty result is [] not None
empty = repo.execute_query("SELECT * FROM users WHERE id > 99999")
# empty = []
```

###### 2. execute_single() - One Row or None

```python
def execute_single(self, query: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
    """For queries that return exactly 0 or 1 row."""
    with self.db.get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(query, params or ())
            result = cur.fetchone()
            return dict(result) if result else None
```

**Use cases:**
```python
# Find one user
user = repo.execute_single(
    "SELECT * FROM users WHERE id = %s",
    (123,)
)
if user:
    print(f"Found: {user['username']}")
else:
    print("Not found")

# INSERT with RETURNING (PostgreSQL feature!)
new_user = repo.execute_single(
    "INSERT INTO users (username, email) VALUES (%s, %s) RETURNING *",
    ('bob', 'bob@example.com')
)
print(f"Created user with ID: {new_user['id']}")

# UPDATE with RETURNING
updated = repo.execute_single(
    "UPDATE users SET email = %s WHERE id = %s RETURNING *",
    ('newemail@example.com', 123)
)
```

###### 3. execute_update() - Modify Data

```python
def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
    """For INSERT/UPDATE/DELETE. Returns affected row count."""
    with self.db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            rowcount = cur.rowcount
            conn.commit()  # IMPORTANT: Commit changes!
            return int(rowcount) if rowcount is not None else 0
```

**Use cases:**
```python
# Update email
count = repo.execute_update(
    "UPDATE users SET email = %s WHERE id = %s",
    ('new@email.com', 123)
)
if count > 0:
    print("Updated successfully")
else:
    print("User not found")

# Delete old records
deleted = repo.execute_update(
    "DELETE FROM orders WHERE created_at < %s",
    ('2020-01-01',)
)
print(f"Deleted {deleted} old orders")

# Insert (when you don't need the row back)
repo.execute_update(
    "INSERT INTO logs (message) VALUES (%s)",
    ('User logged in',)
)
```

##### Convenience Methods

###### find_by_id() - Most Common Query

```python
def find_by_id(self, id_value: int) -> Optional[Dict[str, Any]]:
    """Shorthand for SELECT * FROM table WHERE id = ?"""
    query = f"SELECT * FROM {self.table_name} WHERE id = %s"
    return self.execute_single(query, (id_value,))
```

**Usage:**
```python
user_repo = UserRepository()
user = user_repo.find_by_id(5)  # Clean and simple!
```

###### find_all() - Pagination

```python
def find_all(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """Get records with pagination."""
    query = f"SELECT * FROM {self.table_name} ORDER BY id LIMIT %s OFFSET %s"
    return self.execute_query(query, (limit, offset))
```

**Understanding LIMIT and OFFSET:**

```sql
-- Page 1: First 20 rows
SELECT * FROM users ORDER BY id LIMIT 20 OFFSET 0;
-- Returns rows 1-20

-- Page 2: Next 20 rows
SELECT * FROM users ORDER BY id LIMIT 20 OFFSET 20;
-- Returns rows 21-40

-- Page 3: Next 20 rows
SELECT * FROM users ORDER BY id LIMIT 20 OFFSET 40;
-- Returns rows 41-60
```

**Pagination formula:**
```python
page_number = 3      # Which page? (1-indexed)
items_per_page = 20

offset = (page_number - 1) * items_per_page
# page 1: offset = 0
# page 2: offset = 20
# page 3: offset = 40

records = repo.find_all(limit=items_per_page, offset=offset)
```

###### delete_by_id() - Safe Deletion

```python
def delete_by_id(self, id_value: int) -> bool:
    """Delete by ID. Returns True if deleted, False if not found."""
    query = f"DELETE FROM {self.table_name} WHERE id = %s"
    affected_rows = self.execute_update(query, (id_value,))
    return affected_rows > 0
```

**Usage:**
```python
if user_repo.delete_by_id(999):
    print("User deleted!")
else:
    print("User not found")
```

###### count() - Total Records

```python
def count(self) -> int:
    """Count total records in table."""
    query = f"SELECT COUNT(*) as count FROM {self.table_name}"
    result = self.execute_single(query)
    return result["count"] if result else 0
```

**Usage:**
```python
total = user_repo.count()
print(f"Total users: {total}")

# Useful for pagination
total_pages = (total + items_per_page - 1) // items_per_page
```

---

## Critical Security Concepts

### SQL Injection Prevention

#### The Attack

```python
# NEVER DO THIS!
user_input = "1 OR 1=1; DROP TABLE users;--"
query = f"SELECT * FROM users WHERE id = {user_input}"
# Executes: SELECT * FROM users WHERE id = 1 OR 1=1; DROP TABLE users;--
# Result: All users returned, then users table DELETED! 💥
```

**Real-world example (2015 TalkTalk hack):**
```sql
-- Attacker entered this in a login form:
username: admin'--
password: anything

-- Server executed:
SELECT * FROM users WHERE username = 'admin'--' AND password = 'anything'
-- Everything after -- is a comment!
-- Attacker logged in as admin without password!
```

#### The Defense: Parameterized Queries

```python
# ALWAYS DO THIS!
user_input = "1 OR 1=1; DROP TABLE users;--"
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_input,))

# PostgreSQL treats input as DATA, not CODE:
# SELECT * FROM users WHERE id = '1 OR 1=1; DROP TABLE users;--'
# Looks for user with literal ID = '1 OR 1=1; DROP TABLE users;--'
# No SQL injection possible!
```

#### How Parameterization Works

**Step-by-step:**

1. **Query is parsed separately from data**
```python
query = "SELECT * FROM users WHERE id = %s"  # %s is placeholder
params = (user_input,)  # Data passed separately
```

2. **PostgreSQL compiles query once**
```
Parse tree:
  SELECT
    FROM users
    WHERE id = $1  -- $1 = first parameter
```

3. **Data is safely substituted**
```
$1 = '1 OR 1=1; DROP TABLE users;--' (as string literal)
```

4. **Special characters are escaped**
```sql
-- Single quotes in data are automatically escaped
user_input = "O'Brien"
-- Becomes: 'O''Brien' in the query (note double quote)
```

#### Rule of Thumb

```python
# NEVER use f-strings or % formatting with user input:
query = f"SELECT * FROM users WHERE username = '{username}'"  # ❌ DANGEROUS!
query = "SELECT * FROM users WHERE username = '%s'" % username  # ❌ DANGEROUS!

# ALWAYS use parameterized queries:
query = "SELECT * FROM users WHERE username = %s"  # ✅ SAFE!
cursor.execute(query, (username,))
```

**Exception:** Table/column names can't be parameterized (they're not data)
```python
# This is OK (table_name is from our code, not user input):
query = f"SELECT * FROM {self.table_name} WHERE id = %s"
#                      ^^^^^^^^^^^^^^^^^^      ^^
#                      From trusted source     User input - parameterized!
```

---

## PostgreSQL-Specific Features

### RETURNING Clause

**Most databases require 2 queries:**
```sql
-- Query 1: Insert
INSERT INTO users (username, email) VALUES ('bob', 'bob@example.com');

-- Query 2: Get the new row (including auto-generated ID)
SELECT * FROM users WHERE username = 'bob';
```

**PostgreSQL: Do it in 1 query!**
```sql
INSERT INTO users (username, email)
VALUES ('bob', 'bob@example.com')
RETURNING *;

-- Output:
-- id | username | email            | created_at          | updated_at
-- 5  | bob      | bob@example.com  | 2025-01-11 15:30:00 | 2025-01-11 15:30:00
```

**Works with UPDATE and DELETE too:**
```sql
-- See what changed
UPDATE users SET email = 'newemail@example.com' WHERE id = 5
RETURNING id, username, email, updated_at;

-- See what was deleted
DELETE FROM users WHERE id = 5
RETURNING *;
```

**Why it's useful:**
- Get auto-generated ID immediately
- Verify what was actually updated
- Audit trail (log deleted records)
- Atomic operation (no race conditions)

### dict_row Factory

**Default psycopg behavior (tuples):**
```python
cur.execute("SELECT id, username, email FROM users WHERE id = 1")
row = cur.fetchone()
print(row)
# Output: (1, 'john_doe', 'john@example.com')

# Access by position (error-prone):
user_id = row[0]
username = row[1]  # Have to remember order!
email = row[2]
```

**With dict_row factory (dictionaries):**
```python
from psycopg.rows import dict_row

cur = conn.cursor(row_factory=dict_row)
cur.execute("SELECT id, username, email FROM users WHERE id = 1")
row = cur.fetchone()
print(row)
# Output: {'id': 1, 'username': 'john_doe', 'email': 'john@example.com'}

# Access by name (clear and safe):
user_id = row['id']
username = row['username']
email = row['email']
```

**Benefits:**
- Self-documenting code
- Column order doesn't matter
- Easy to serialize to JSON
- Type hints work better
- IDE autocomplete

---

## What You've Learned So Far

### Database Design ✅
- [x] Primary keys and SERIAL
- [x] Foreign keys with CASCADE/RESTRICT
- [x] ENUM types for data validation
- [x] CHECK constraints
- [x] Indexes for performance
- [x] Triggers and functions
- [x] Timestamps

### PostgreSQL Operations ✅
- [x] Connection pooling
- [x] Singleton pattern
- [x] Context managers
- [x] RETURNING clause
- [x] dict_row factory
- [x] GRANT/REVOKE privileges

### Security ✅
- [x] SQL injection prevention
- [x] Parameterized queries
- [x] PostgreSQL permission system

### Software Engineering ✅
- [x] Repository pattern
- [x] Separation of concerns
- [x] DRY principle (Don't Repeat Yourself)
- [x] Code reusability

---

## Next Steps

### Repositories to Build:
1. **UserRepository** - ENUM handling, password hashing
2. **CustomerRepository** - JOINs (customer + user)
3. **ItemRepository** - Filtering, search, stock management
4. **OrderRepository** - Complex JOINs, aggregations
5. **OrderItemRepository** - Many-to-many relationships
6. **PaymentRepository** - Transactions, GROUP BY

### Advanced Concepts Coming:
- [ ] JOIN queries (INNER, LEFT, RIGHT)
- [ ] Aggregations (COUNT, SUM, AVG, GROUP BY)
- [ ] Subqueries and CTEs
- [ ] Transactions (BEGIN, COMMIT, ROLLBACK)
- [ ] Query optimization with EXPLAIN
- [ ] Full-text search
- [ ] JSON columns

---

## Quick Reference

### Common Patterns

```python
# Get one record
user = repo.execute_single(
    "SELECT * FROM users WHERE id = %s",
    (user_id,)
)

# Get multiple records
users = repo.execute_query(
    "SELECT * FROM users WHERE role = %s",
    ('customer',)
)

# Insert with RETURNING
new_user = repo.execute_single(
    "INSERT INTO users (username, email) VALUES (%s, %s) RETURNING *",
    ('alice', 'alice@example.com')
)

# Update with RETURNING
updated = repo.execute_single(
    "UPDATE users SET email = %s WHERE id = %s RETURNING *",
    ('new@email.com', 5)
)

# Delete and count
count = repo.execute_update(
    "DELETE FROM users WHERE id = %s",
    (5,)
)

# Count records
total = repo.count()
```

### psql Commands

```bash
# Connect to database
psql -d payment_system_db

# List tables
\dt

# Describe table
\d users

# Show table data
SELECT * FROM users;

# Quit
\q
```

---

**Ready to continue with UserRepository?** 🚀

This will teach you:
- Working with ENUM types
- Handling timestamps
- Query by multiple criteria
- Password fields

Let me know when you're ready!
