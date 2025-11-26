"""
Demo script to populate and display all tables for the Payment System OOP project.
Fills Users, Customers, Items, Orders, OrderItems, and Payments with sample data.
"""

import random
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from src.models.sqlalchemy_models import (
    Customer,
    Item,
    Order,
    OrderItem,
    Payment,
    PaymentMethod,
    User,
    UserRole,
)
from src.utils.db_session import SessionLocal


def main() -> None:
    """
    Populate all tables with demo data and print sample output.
    This script is for demonstration and development purposes only.
    """
    session = SessionLocal()
    try:
        # Clear all tables for a fresh demo (CAUTION: for demo/dev only!)
        # Only use __tablename__ for SQLAlchemy declarative classes
        for tbl in [Payment, OrderItem, Order, Customer, Item, User]:
            if hasattr(tbl, "__tablename__"):
                session.execute(
                    text(
                        f"TRUNCATE TABLE {tbl.__tablename__} RESTART IDENTITY CASCADE;"
                    )
                )
        session.commit()

        # Create users and customers
        users: list[User] = []
        customers: list[Customer] = []
        for i in range(1, 6):
            user = User(
                username=f"user{i}",
                email=f"user{i}@example.com",
                hashed_password="pass",
                role=UserRole.CUSTOMER,
            )
            session.add(user)
            session.flush()  # get user.id
            customer = Customer(
                user_id=user.id, address=f"{i} Main St", phone=f"555-000{i}"
            )
            session.add(customer)
            users.append(user)
            customers.append(customer)
        session.commit()
        for user in users:
            session.refresh(user)
        for customer in customers:
            session.refresh(customer)
        print("Created users and customers:")
        for user, customer in zip(users, customers):
            print(
                f"  User {user.id}: {user.username}, {user.email}"
                " | Customer {customer.id}: "
                f"{customer.address}, {customer.phone}"
            )
        # Create items
        items: list[Item] = [
            Item(name="Laptop", description="A fast laptop", price=1200.0, stock=10),
            Item(name="Mouse", description="Wireless mouse", price=25.0, stock=50),
            Item(
                name="Keyboard", description="Mechanical keyboard", price=80.0, stock=30
            ),
            Item(name="Monitor", description="24-inch monitor", price=200.0, stock=20),
            Item(name="USB Cable", description="USB-C cable", price=10.0, stock=100),
        ]
        session.add_all(items)
        session.commit()
        for item in items:
            session.refresh(item)
        print("Created items:")
        for item in items:
            print(f"  {item.id}: {item.name}, ${item.price}, " f"stock={item.stock}")

        # Create orders, order items, and payments
        payments: list[Payment] = []
        for customer in customers:
            for _ in range(2):  # Each customer gets 2 orders
                order = Order(
                    customer_id=customer.id,
                    created_at=datetime.utcnow(),
                    status="confirmed",
                    total=0.0,
                )
                session.add(order)
                session.flush()
                order_items: list[OrderItem] = []
                order_total = 0.0
                for item in random.sample(items, k=random.randint(2, 4)):
                    qty = random.randint(1, 3)
                    oi = OrderItem(
                        order_id=order.id,
                        item_id=item.id,
                        quantity=qty,
                        price=item.price,
                    )
                    order_items.append(oi)
                    order_total += item.price * qty
                session.add_all(order_items)
                order.total = order_total
                payment = Payment(
                    order_id=order.id,
                    amount=order_total,
                    method=random.choice(list(PaymentMethod)),
                    status="completed",
                    transaction_id=(f"TXN{order.id}{random.randint(1000, 9999)}"),
                )
                session.add(payment)
                payments.append(payment)
        session.commit()
        print("Created orders, order items, and payments for each customer.")

        # Query and print all tables
        print(f"\nAll Users: {session.query(User).count()}")
        print(f"All Customers: {session.query(Customer).count()}")
        print(f"All Items: {session.query(Item).count()}")
        print(f"All Orders: {session.query(Order).count()}")
        print(f"All OrderItems: {session.query(OrderItem).count()}")
        print(f"All Payments: {session.query(Payment).count()}")

        print("\nSample Orders:")
        orders = session.query(Order).limit(5).all()
        for o in orders:
            print(
                f"Order {o.id}: customer_id={o.customer_id}, "
                f"status={o.status}, total={o.total}"
            )
            for oi in o.items:
                print(f"  Item {oi.item_id}: qty={oi.quantity}, price={oi.price}")
            if o.payment:
                print(
                    f"  Payment: {o.payment.amount}, {o.payment.method}, "
                    f"{o.payment.status}, {o.payment.transaction_id}"
                )
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
