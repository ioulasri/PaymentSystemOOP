# 🗄️ **Payment System Database Structure**

## **Overview**
This document describes the PostgreSQL database structure for the Payment System OOP project using **raw SQL with psycopg** (not ORM).

---

## 📊 **Database Schema**

### **Database Name:** `payment_system_db`

### **Connection String:**
```
postgresql://localhost:5432/payment_system_db
```

---

## 🏗️ **Table Structure**

### **1. users** - User Authentication & Roles
Stores user authentication information and role-based access control.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role user_role_enum NOT NULL DEFAULT 'customer',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

**Columns:**
- `id`: Auto-incrementing primary key
- `username`: Unique username (3+ characters)
- `email`: Unique email (validated format)
- `hashed_password`: Bcrypt/scrypt hashed password
- `role`: ENUM('customer', 'admin')
- `is_active`: Account activation status
- `created_at`: Registration timestamp
- `updated_at`: Auto-updated on changes

**Indexes:**
- Primary key on `id`
- Unique index on `username`
- Unique index on `email`
- B-tree index on `role` (for role-based queries)

**Constraints:**
- `username` must be >= 3 characters
- `email` must match email regex pattern

---

### **2. customers** - Customer Extended Information
One-to-One relationship with users table for customer-specific data.

```sql
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    address TEXT,
    phone VARCHAR(20),
    fraud_status VARCHAR(20) NOT NULL DEFAULT 'clear',
    failed_attempts INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

**Columns:**
- `id`: Auto-incrementing primary key
- `user_id`: Foreign key to users (ONE-TO-ONE)
- `address`: Customer shipping/billing address
- `phone`: Contact phone number
- `fraud_status`: ENUM('clear', 'under_review', 'flagged', 'blocked')
- `failed_attempts`: Failed payment attempt counter
- `created_at`: Customer record creation timestamp

**Relationships:**
- `user_id` → `users.id` (ONE-TO-ONE, CASCADE DELETE)

**Indexes:**
- Primary key on `id`
- Unique index on `user_id`
- B-tree index on `fraud_status`

**Constraints:**
- `failed_attempts` >= 0
- `fraud_status` must be valid enum value

---

### **3. items** - Product Catalog
Stores product information and inventory.

```sql
CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

**Columns:**
- `id`: Auto-incrementing primary key
- `name`: Product name
- `description`: Product description
- `price`: Product price (up to 99,999,999.99)
- `stock`: Available inventory count
- `is_active`: Product visibility flag
- `created_at`: Product creation timestamp
- `updated_at`: Auto-updated on changes

**Indexes:**
- Primary key on `id`
- B-tree index on `name` (for search)
- B-tree index on `is_active` (for filtering)

**Constraints:**
- `price` >= 0
- `stock` >= 0
- `name` cannot be empty/whitespace

---

### **4. orders** - Customer Orders
Represents customer purchase orders.

```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    total DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    status order_status_enum NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

**Columns:**
- `id`: Auto-incrementing primary key
- `customer_id`: Foreign key to customers (ONE-TO-MANY)
- `total`: Order total amount (calculated from order_items)
- `status`: ENUM('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled')
- `created_at`: Order placement timestamp
- `updated_at`: Auto-updated on changes

**Relationships:**
- `customer_id` → `customers.id` (MANY-TO-ONE, CASCADE DELETE)

**Indexes:**
- Primary key on `id`
- B-tree index on `customer_id` (for customer order lookup)
- B-tree index on `status` (for order filtering)
- B-tree index on `created_at` (for date-range queries)

**Constraints:**
- `total` >= 0

---

### **5. order_items** - Order Line Items
Junction table for Many-to-Many relationship between orders and items.

```sql
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE RESTRICT,
    quantity INTEGER NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (order_id, item_id)
);
```

**Columns:**
- `id`: Auto-incrementing primary key
- `order_id`: Foreign key to orders
- `item_id`: Foreign key to items
- `quantity`: Number of items ordered
- `price`: Price at time of purchase (snapshot)
- `created_at`: Line item creation timestamp

**Relationships:**
- `order_id` → `orders.id` (MANY-TO-ONE, CASCADE DELETE)
- `item_id` → `items.id` (MANY-TO-ONE, RESTRICT DELETE)

**Indexes:**
- Primary key on `id`
- B-tree index on `order_id` (for order lookup)
- B-tree index on `item_id` (for item sales analytics)
- Unique compound index on `(order_id, item_id)`

**Constraints:**
- `quantity` > 0
- `price` >= 0
- Cannot add same item twice to an order (unique constraint)

**Note:** DELETE RESTRICT on `item_id` prevents accidental deletion of items with order history.

---

### **6. payments** - Payment Transactions
Records payment transactions for orders.

```sql
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    order_id INTEGER UNIQUE NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    amount DECIMAL(10, 2) NOT NULL,
    method payment_method_enum NOT NULL,
    status payment_status_enum NOT NULL DEFAULT 'pending',
    transaction_id VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

**Columns:**
- `id`: Auto-incrementing primary key
- `order_id`: Foreign key to orders (ONE-TO-ONE)
- `amount`: Payment amount
- `method`: ENUM('credit_card', 'paypal', 'crypto')
- `status`: ENUM('pending', 'processing', 'completed', 'failed', 'refunded')
- `transaction_id`: Unique external transaction identifier
- `created_at`: Payment initiation timestamp
- `updated_at`: Auto-updated on status changes

**Relationships:**
- `order_id` → `orders.id` (ONE-TO-ONE, CASCADE DELETE)

**Indexes:**
- Primary key on `id`
- Unique index on `order_id` (one payment per order)
- Unique index on `transaction_id`
- B-tree index on `status` (for payment reconciliation)

**Constraints:**
- `amount` > 0
- `transaction_id` cannot be empty

---

## 🔗 **Relationships Diagram**

```
users (1) ──────< (1) customers (1) ──────< (*) orders
                                                  │
                                                  │ (1)
                                                  │
                                                  └──────< (1) payments

orders (*) ──────< (*) order_items (*) >────── (*) items
```

**Legend:**
- `(1)` = One
- `(*)` = Many
- `──────<` = One-to-Many
- `>──────` = Many-to-One

---

## 🎯 **Key PostgreSQL Features Used**

### **1. ENUM Types**
```sql
CREATE TYPE user_role_enum AS ENUM ('customer', 'admin');
CREATE TYPE payment_method_enum AS ENUM ('credit_card', 'paypal', 'crypto');
CREATE TYPE order_status_enum AS ENUM ('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled');
CREATE TYPE payment_status_enum AS ENUM ('pending', 'processing', 'completed', 'failed', 'refunded');
```

**Benefits:**
- Type safety at database level
- Clear constraints on allowed values
- Better performance than VARCHAR with CHECK constraints

---

### **2. Automatic Timestamps**
```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

**Tables with auto-update triggers:**
- `users`
- `items`
- `orders`
- `payments`

---

### **3. Cascading Deletes**
When a user is deleted, all related data is automatically removed:

```
users (CASCADE) → customers (CASCADE) → orders (CASCADE) → order_items
                                              └─────────→ payments
```

**Example:**
```sql
DELETE FROM users WHERE id = 1;
-- Automatically deletes:
-- - customer record
-- - all orders
-- - all order_items
-- - all payments
```

---

### **4. Indexes for Performance**

**Purpose:**
- Speed up SELECT queries
- Optimize JOIN operations
- Improve ORDER BY performance

**Examples:**
```sql
CREATE INDEX idx_orders_customer_id ON orders(customer_id);  -- Fast customer order lookup
CREATE INDEX idx_orders_created_at ON orders(created_at);    -- Date-range queries
CREATE INDEX idx_payments_status ON payments(status);        -- Payment reconciliation
```

---

## 📈 **Sample Queries**

### **Get Customer with User Info (JOIN)**
```sql
SELECT
    c.id as customer_id,
    c.address,
    c.phone,
    u.username,
    u.email,
    u.role
FROM customers c
JOIN users u ON c.user_id = u.id
WHERE c.id = 1;
```

---

### **Get Order with All Items (Multiple JOINs)**
```sql
SELECT
    o.id as order_id,
    o.total,
    o.status,
    oi.quantity,
    oi.price,
    i.name as item_name,
    i.description
FROM orders o
JOIN order_items oi ON o.id = oi.order_id
JOIN items i ON oi.item_id = i.id
WHERE o.id = 1;
```

---

### **Get Customer Order History with Payments**
```sql
SELECT
    o.id,
    o.total,
    o.status,
    o.created_at,
    p.method,
    p.status as payment_status,
    p.transaction_id
FROM orders o
LEFT JOIN payments p ON o.id = p.order_id
WHERE o.customer_id = 1
ORDER BY o.created_at DESC;
```

---

### **Calculate Total Sales per Item**
```sql
SELECT
    i.name,
    i.price,
    SUM(oi.quantity) as total_sold,
    SUM(oi.quantity * oi.price) as total_revenue
FROM items i
JOIN order_items oi ON i.id = oi.item_id
JOIN orders o ON oi.order_id = o.id
WHERE o.status != 'cancelled'
GROUP BY i.id, i.name, i.price
ORDER BY total_revenue DESC;
```

---

## 🔧 **Database Operations**

### **Initialize Database**
```bash
# Create database
createdb payment_system_db

# Run schema and load sample data
python database/init_db.py --with-sample-data

# Verify tables
python database/init_db.py --verify-only
```

---

### **Connect to Database**
```bash
# Using psql
psql -d payment_system_db

# List tables
\dt

# Describe table
\d users

# Show all data
SELECT * FROM users;
```

---

### **Backup and Restore**
```bash
# Backup
pg_dump payment_system_db > backup.sql

# Restore
psql payment_system_db < backup.sql
```

---

## 🎓 **What You're Learning**

1. **DDL (Data Definition Language)**
   - CREATE TABLE, DROP TABLE
   - CREATE TYPE (ENUMs)
   - CREATE INDEX
   - ALTER TABLE

2. **Constraints**
   - PRIMARY KEY
   - FOREIGN KEY (with CASCADE/RESTRICT)
   - UNIQUE
   - CHECK
   - NOT NULL
   - DEFAULT

3. **Relationships**
   - One-to-One (users ↔ customers)
   - One-to-Many (customers → orders)
   - Many-to-Many (orders ↔ items via order_items)

4. **Triggers & Functions**
   - PL/pgSQL functions
   - BEFORE/AFTER triggers
   - Automatic timestamp updates

5. **Performance**
   - B-tree indexes
   - Compound indexes
   - Query optimization

---

## 📝 **Next Steps**

1. ✅ **Database schema created**
2. ✅ **Sample data loaded**
3. ⏭️ **Create Repositories** (CRUD operations with raw SQL)
4. ⏭️ **Build demo script** (test all operations)
5. ⏭️ **Integrate with services** (PaymentProcessor, etc.)

---

**Ready to move to the next phase?** Let me know when you want to create the repository layer with raw SQL CRUD operations! 🚀
