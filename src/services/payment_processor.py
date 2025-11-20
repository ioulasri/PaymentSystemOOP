from src.core.base import PaymentStrategy
from src.core.exceptions import OrderError, PaymentError
from src.models.customer import Customer
from src.models.order import Order


class PaymentProcessor:
    """Facade for processing payment transactions."""

    @staticmethod
    def process_payment(
        customer: Customer, order: Order, payment_method: PaymentStrategy
    ) -> dict:
        """
        Process a payment for an order using the specified payment method.

        Validates the order and payment method, executes the payment,
        updates order status and transaction details, and records the
        transaction in customer history.

        Args:
                customer: The customer making the payment
                order: The order to pay for (must be in 'pending' status)
                payment_method: The payment strategy to use

        Returns:
                dict: Payment receipt containing transaction_id, amount, timestamp, etc.

        Raises:
                OrderError: If order is empty or not in pending status
                ValidationError: If payment method validation fails
                PaymentError: If payment execution fails
        """
        if order.customer != customer:
            raise OrderError("Customer mismatch: order belongs to different customer")
        if order.is_empty():
            raise OrderError("Order list is empty")
        if order.status != "pending":
            raise OrderError(f"Order is {order.status}!")
        payment_method.validate()
        try:
            result = payment_method.execute(order.total_amount)
        except PaymentError as e:
            raise PaymentError(f"Payment failed for order {order.order_id}: {str(e)}")
        order.status = "confirmed"
        order.transaction_id = result["TransactionID"]
        order.payment_method = str(type(payment_method).__name__.replace("Payment", ""))
        customer.add_transaction(result)
        return result
