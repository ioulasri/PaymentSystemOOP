from src.core.base import PaymentStrategy
from src.core.exceptions import OrderError, PaymentError
from src.models.customer import Customer
from src.models.order import Order
from src.utils.logger import get_logger

# Create logger at module level (more Pythonic)
logger = get_logger(__name__)


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
        # Log entry point with context
        logger.info(
            "Processing payment",
            extra={
                "order_id": order.order_id,
                "customer_email": customer.email,
                "amount": order.total_amount,
                "payment_method": type(payment_method).__name__,
            },
        )

        # Validate order ownership
        if order.customer != customer:
            logger.error(
                "Customer mismatch during payment",
                extra={
                    "order_id": order.order_id,
                    "order_customer_email": order.customer.email,
                    "requesting_customer_email": customer.email,
                },
            )
            raise OrderError("Customer mismatch: order belongs to different customer")

        # Validate order not empty
        if order.is_empty():
            logger.warning(
                "Payment attempted on empty order", extra={"order_id": order.order_id}
            )
            raise OrderError("Order list is empty")

        # Validate order status
        if order.status != "pending":
            logger.warning(
                "Payment attempted on non-pending order",
                extra={"order_id": order.order_id, "current_status": order.status},
            )
            raise OrderError(f"Order is {order.status}!")

        # Validate payment method
        logger.debug("Validating payment method")
        payment_method.validate()

        # Execute payment
        try:
            logger.info(
                "Executing payment",
                extra={"order_id": order.order_id, "amount": order.total_amount},
            )
            result = payment_method.execute(order.total_amount)

            # Update order and customer
            order.status = "confirmed"
            order.transaction_id = result["TransactionID"]
            order.payment_method = str(
                type(payment_method).__name__.replace("Payment", "")
            )
            customer.add_transaction(result)

            # Log success
            logger.info(
                "Payment processed successfully",
                extra={
                    "order_id": order.order_id,
                    "transaction_id": result["TransactionID"],
                    "amount": result["Amount"],
                    "payment_method": type(payment_method).__name__,
                },
            )

            return result

        except PaymentError as e:
            # Log failure with details
            logger.error(
                "Payment execution failed",
                extra={
                    "order_id": order.order_id,
                    "amount": order.total_amount,
                    "payment_method": type(payment_method).__name__,
                    "error": str(e),
                },
                exc_info=True,  # Include stack trace
            )
            raise PaymentError(f"Payment failed for order {order.order_id}: {str(e)}")
