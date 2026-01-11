# Payment System - Database Integration Tasks

## Overview
This document outlines the tasks to integrate PostgreSQL with the existing OOP payment system using raw psycopg (no ORM). The goal is to learn PostgreSQL deeply by writing raw SQL queries.

---

## Phase 1: Repository Layer (CRUD with Raw SQL)

### Task 1.1: Create Base Repository
- [ ] Create `src/repositories/base_repository.py`
- [ ] Implement `BaseRepository` class with common CRUD operations
- [ ] Use `DatabaseConnection` singleton for connection pooling
- [ ] Add methods: `execute_query()`, `execute_single()`, `execute_update()`
- [ ] Use parameterized queries with `%s` placeholders for SQL injection protection

### Task 1.2: User Repository
- [ ] Create `src/repositories/user_repository.py`
- [ ] Implement `UserRepository(BaseRepository)`
- [ ] Add method: `create(username, email, hashed_password, role)` → Returns user dict
- [ ] Add method: `get_by_id(user_id)` → Returns user dict or None
- [ ] Add method: `get_by_email(email)` → Returns user dict or None
- [ ] Add method: `update(user_id, **fields)` → Returns updated user dict
- [ ] Add method: `delete(user_id)` → Returns bool (success/failure)
- [ ] Add method: `list_all(limit, offset)` → Returns list of user dicts

### Task 1.3: Customer Repository
- [ ] Create `src/repositories/customer_repository.py`
- [ ] Implement `CustomerRepository(BaseRepository)`
- [ ] Add method: `create(user_id, address, phone)` → Returns customer dict
- [ ] Add method: `get_by_id(customer_id)` → Returns customer dict or None
- [ ] Add method: `get_by_user_id(user_id)` → Returns customer dict or None
- [ ] Add method: `get_with_user_info(customer_id)` → Returns joined dict (customer + user)
- [ ] Add method: `update(customer_id, **fields)` → Returns updated customer dict
- [ ] Add method: `delete(customer_id)` → Returns bool
- [ ] Practice: Write JOIN query to get customer with user details

### Task 1.4: Item Repository
- [ ] Create `src/repositories/item_repository.py`
- [ ] Implement `ItemRepository(BaseRepository)`
- [ ] Add method: `create(name, description, price, stock)` → Returns item dict
- [ ] Add method: `get_by_id(item_id)` → Returns item dict or None
- [ ] Add method: `list_all(limit, offset)` → Returns list of item dicts
- [ ] Add method: `search_by_name(name)` → Returns list of matching items
- [ ] Add method: `update_stock(item_id, quantity)` → Returns updated item dict
- [ ] Add method: `update(item_id, **fields)` → Returns updated item dict
- [ ] Add method: `delete(item_id)` → Returns bool
- [ ] Add method: `get_in_stock()` → Returns items with stock > 0

### Task 1.5: Order Repository
- [ ] Create `src/repositories/order_repository.py`
- [ ] Implement `OrderRepository(BaseRepository)`
- [ ] Add method: `create(customer_id, total, status)` → Returns order dict
- [ ] Add method: `get_by_id(order_id)` → Returns order dict or None
- [ ] Add method: `get_by_customer(customer_id)` → Returns list of orders
- [ ] Add method: `get_with_items(order_id)` → Returns order with joined items list
- [ ] Add method: `update_status(order_id, new_status)` → Returns updated order dict
- [ ] Add method: `update_total(order_id, new_total)` → Returns updated order dict
- [ ] Add method: `delete(order_id)` → Returns bool
- [ ] Practice: Complex JOIN query (orders + customers + users + order_items + items)

### Task 1.6: Order Item Repository
- [ ] Create `src/repositories/order_item_repository.py`
- [ ] Implement `OrderItemRepository(BaseRepository)`
- [ ] Add method: `create(order_id, item_id, quantity, price)` → Returns order_item dict
- [ ] Add method: `get_by_order(order_id)` → Returns list of order items
- [ ] Add method: `get_by_id(order_item_id)` → Returns order_item dict or None
- [ ] Add method: `update_quantity(order_item_id, quantity)` → Returns updated dict
- [ ] Add method: `delete(order_item_id)` → Returns bool
- [ ] Add method: `delete_by_order(order_id)` → Returns number of deleted items

### Task 1.7: Payment Repository
- [ ] Create `src/repositories/payment_repository.py`
- [ ] Implement `PaymentRepository(BaseRepository)`
- [ ] Add method: `create(order_id, amount, method, status, transaction_id)` → Returns payment dict
- [ ] Add method: `get_by_id(payment_id)` → Returns payment dict or None
- [ ] Add method: `get_by_order(order_id)` → Returns list of payments
- [ ] Add method: `get_by_transaction_id(txn_id)` → Returns payment dict or None
- [ ] Add method: `update_status(payment_id, new_status)` → Returns updated payment dict
- [ ] Add method: `get_by_customer(customer_id)` → Returns payment history with JOINs

---

## Phase 2: Demo Script (Raw SQL Practice)

### Task 2.1: Create Demo Script
- [ ] Create `src/main_db_demo.py`
- [ ] Import all repositories
- [ ] Import `DatabaseConnection` from `src.utils.db_connection`

### Task 2.2: Demo - User & Customer CRUD
- [ ] Initialize database connection pool
- [ ] Create a new user (customer role)
- [ ] Fetch user by email
- [ ] Create customer linked to user
- [ ] Fetch customer with user info (JOIN query)
- [ ] Update customer address
- [ ] Print results

### Task 2.3: Demo - Items Management
- [ ] Create 3-5 new items
- [ ] List all items
- [ ] Search items by name
- [ ] Update stock for an item
- [ ] Fetch items in stock
- [ ] Print results

### Task 2.4: Demo - Order Creation
- [ ] Create a new order for a customer
- [ ] Add 2-3 order items to the order
- [ ] Calculate and update order total
- [ ] Fetch order with all items (JOIN query)
- [ ] Print order details

### Task 2.5: Demo - Payment Processing
- [ ] Create a payment for the order
- [ ] Update payment status to 'completed'
- [ ] Fetch payment by transaction ID
- [ ] Get customer's payment history (JOIN query)
- [ ] Print payment details

### Task 2.6: Demo - Complex Queries
- [ ] Query: Get all orders with customer info and item details
- [ ] Query: Get total revenue by payment method (GROUP BY)
- [ ] Query: Get customers with most orders (ORDER BY COUNT)
- [ ] Query: Get items that were never ordered (LEFT JOIN with WHERE NULL)
- [ ] Print aggregated results

### Task 2.7: Demo - Cleanup
- [ ] Close database connection pool
- [ ] Add proper error handling (try/except blocks)
- [ ] Add logging for each operation
- [ ] Make script runnable with `python src/main_db_demo.py`

---

## Phase 3: Integration with Existing Services

### Task 3.1: Integrate Customer Model
- [ ] Open `src/models/customer.py`
- [ ] Add `customer_id` property (database ID)
- [ ] Modify `__init__()` to accept optional `customer_id` parameter
- [ ] Add method: `save()` → Creates or updates customer in database
- [ ] Add method: `load_from_db(customer_id)` → Class method to load from database
- [ ] Modify `initiate_payment()` to persist transaction to database
- [ ] Update `add_transaction()` to use PaymentRepository

### Task 3.2: Integrate Order Model
- [ ] Open `src/models/order.py`
- [ ] Add `order_id` property (database ID)
- [ ] Add method: `save()` → Creates or updates order in database
- [ ] Add method: `load_from_db(order_id)` → Class method to load from database
- [ ] Modify order creation to persist to database
- [ ] Link order items to database

### Task 3.3: Integrate Payment Methods
- [ ] Open payment method files (credit_card.py, paypal.py, crypto.py)
- [ ] Add database persistence after successful payment
- [ ] Use PaymentRepository to create payment records
- [ ] Store transaction IDs in database

### Task 3.4: Integrate PaymentProcessor
- [ ] Open `src/services/payment_processor.py`
- [ ] Add database logging for each payment attempt
- [ ] Persist failed attempts to database
- [ ] Add method: `get_payment_history(customer_id)` using repository
- [ ] Add method: `get_payment_by_transaction_id(txn_id)` using repository

### Task 3.5: Add Transaction Management
- [ ] Create `src/utils/transaction.py`
- [ ] Implement transaction context manager using psycopg
- [ ] Add method: `begin_transaction()`, `commit()`, `rollback()`
- [ ] Use in PaymentProcessor for atomic operations
- [ ] Example: Create order + order items + payment in single transaction

---

## Phase 4: Testing & Documentation

### Task 4.1: Unit Tests for Repositories
- [ ] Create `tests/unit/test_repositories/`
- [ ] Test each repository CRUD operation
- [ ] Use pytest fixtures for database setup/teardown
- [ ] Mock database connections where appropriate

### Task 4.2: Integration Tests
- [ ] Create `tests/integration/test_database_integration.py`
- [ ] Test complete workflows (create order → add items → process payment)
- [ ] Test transaction rollbacks
- [ ] Test foreign key constraints

### Task 4.3: Update Documentation
- [ ] Update README.md with database setup instructions
- [ ] Document repository usage examples
- [ ] Add ER diagram to documentation
- [ ] Document raw SQL queries used

### Task 4.4: Performance Testing
- [ ] Test connection pool under load
- [ ] Measure query performance
- [ ] Add indexes if needed (already in schema.sql)
- [ ] Document performance benchmarks

---

## Phase 5: Git Organization

### Task 5.1: Create Feature Branches
- [ ] Create `feature/repository-layer` branch
- [ ] Create `feature/demo-script` branch
- [ ] Create `feature/service-integration` branch
- [ ] Backdate commits similar to previous work

### Task 5.2: Merge to Develop
- [ ] Merge repositories branch first
- [ ] Merge demo script branch
- [ ] Merge integration branch
- [ ] Push to GitHub with corrected dates

---

## Learning Objectives

### PostgreSQL Concepts to Master:
- [x] Database schema design
- [x] Primary keys & foreign keys
- [x] ENUM types
- [x] Triggers & functions
- [x] Indexes for performance
- [ ] Raw SQL CRUD operations (INSERT, SELECT, UPDATE, DELETE)
- [ ] JOIN queries (INNER JOIN, LEFT JOIN, RIGHT JOIN)
- [ ] Aggregations (COUNT, SUM, AVG, GROUP BY, HAVING)
- [ ] Subqueries & CTEs (Common Table Expressions)
- [ ] Transactions (BEGIN, COMMIT, ROLLBACK)
- [ ] Parameterized queries (SQL injection prevention)
- [ ] Connection pooling
- [ ] Query optimization

### psycopg3 Features to Practice:
- [x] Connection management
- [x] Connection pooling
- [x] dict_row factory
- [ ] Parameterized queries with %s placeholders
- [ ] Context managers (with statements)
- [ ] Transaction control
- [ ] Error handling (psycopg.errors)
- [ ] Cursor operations (fetchone, fetchall, fetchmany)

---

## Quick Reference: psycopg Query Patterns

```python
# SELECT single row
row = db.execute_single(
    "SELECT * FROM users WHERE id = %s",
    (user_id,)
)

# SELECT multiple rows
rows = db.execute_query(
    "SELECT * FROM items WHERE price < %s",
    (max_price,)
)

# INSERT and return inserted row
result = db.execute_single(
    "INSERT INTO users (username, email, role) VALUES (%s, %s, %s) RETURNING *",
    (username, email, role)
)

# UPDATE and return updated row
result = db.execute_single(
    "UPDATE customers SET address = %s WHERE id = %s RETURNING *",
    (new_address, customer_id)
)

# DELETE and get rowcount
rowcount = db.execute_update(
    "DELETE FROM order_items WHERE order_id = %s",
    (order_id,)
)

# JOIN query
orders = db.execute_query(
    """
    SELECT o.*, c.address, u.username, u.email
    FROM orders o
    JOIN customers c ON o.customer_id = c.id
    JOIN users u ON c.user_id = u.id
    WHERE o.customer_id = %s
    """,
    (customer_id,)
)
```

---

## Getting Started

**Step 1:** Start with Task 1.1 (Create Base Repository)
**Step 2:** Continue with Task 1.2-1.7 (Implement all repositories)
**Step 3:** Build the demo script (Task 2.1-2.7)
**Step 4:** Integrate with existing models (Task 3.1-3.5)

Let's begin! 🚀
