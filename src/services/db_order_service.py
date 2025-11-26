# Service for Order CRUD operations using SQLAlchemy
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from src.models.sqlalchemy_models import Item, Order, OrderItem
from src.utils.db_session import SessionLocal


class OrderDBService:
    @staticmethod
    def create_order(customer_id: int, item_ids: list[int]) -> Order:
        session: Session = SessionLocal()
        try:
            order = Order(
                customer_id=customer_id,
                created_at=datetime.utcnow(),
                status="pending",
                total=0.0,
            )
            session.add(order)
            session.flush()  # Get order.id
            total = 0.0
            for item_id in item_ids:
                item = session.query(Item).filter(Item.id == item_id).first()
                if not item:
                    raise ValueError(f"Item {item_id} not found")
                order_item = OrderItem(
                    order_id=order.id, item_id=item.id, quantity=1, price=item.price
                )
                session.add(order_item)
                total += item.price
            order.total = total
            session.commit()
            session.refresh(order)
            return order
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def get_order(order_id: int) -> Optional[Order]:
        """Get an order by ID. Returns Order or None."""
        session: Session = SessionLocal()
        try:
            result = session.query(Order).filter(Order.id == order_id).first()
            return result if isinstance(result, Order) or result is None else None
        finally:
            session.close()

    @staticmethod
    def update_order_status(order_id: int, status: str) -> None:
        session: Session = SessionLocal()
        try:
            order = session.query(Order).filter(Order.id == order_id).first()
            if not order:
                raise ValueError("Order not found")
            order.status = status
            session.commit()
        finally:
            session.close()

    @staticmethod
    def delete_order(order_id: int) -> None:
        session: Session = SessionLocal()
        try:
            order = session.query(Order).filter(Order.id == order_id).first()
            if not order:
                raise ValueError("Order not found")
            session.delete(order)
            session.commit()
        finally:
            session.close()
