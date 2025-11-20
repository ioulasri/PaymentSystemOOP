"""
Unit tests for PaymentProcessor.

Tests the payment processing facade including:
- Successful payment flow
- Order validation (empty, wrong status)
- Customer validation (mismatch)
- Payment method validation failures
- Payment execution failures
- Order and customer updates after payment
"""

import unittest
import sys
from pathlib import Path

# Add project root to path for absolute imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.services.payment_processor import PaymentProcessor
from src.models.customer import Customer
from src.models.order import Order
from src.models.item import Item
from src.payment.methods.credit_card import CreditCardPayment
from src.core.exceptions import OrderError, PaymentError, ValidationError


class TestPaymentProcessorSuccess(unittest.TestCase):
	"""Test successful payment processing."""

	def setUp(self):
		"""Set up test data."""
		self.customer = Customer("John Doe", "john@example.com")
		self.order = Order(self.customer)
		
		# Add an item to the order
		self.item = Item("Laptop")
		self.item.price = 1200.0
		self.item.stock = 10
		self.order.add_item(self.item)
		
		# Set up payment method
		self.payment = CreditCardPayment()
		self.payment.cardholder = "Mr John Doe"
		self.payment.cardnumber = "4532123456789012"
		self.payment.expirationdate = "12-25"
		self.payment.cvv = "123"
		self.payment.balance = 5000.0

	def test_successful_payment(self):
		"""Test complete successful payment flow."""
		result = PaymentProcessor.process_payment(
			self.customer,
			self.order,
			self.payment
		)
		
		# Check result contains transaction info
		self.assertIn("TransactionID", result)
		self.assertIn("Amount", result)
		self.assertEqual(result["Amount"], 1200.0)
		
	def test_order_status_updated(self):
		"""Test that order status is updated to confirmed."""
		initial_status = self.order.status
		self.assertEqual(initial_status, "pending")
		
		PaymentProcessor.process_payment(
			self.customer,
			self.order,
			self.payment
		)
		
		self.assertEqual(self.order.status, "confirmed")
		
	def test_order_transaction_id_set(self):
		"""Test that order transaction_id is set."""
		self.assertEqual(self.order.transaction_id, "")
		
		result = PaymentProcessor.process_payment(
			self.customer,
			self.order,
			self.payment
		)
		
		self.assertNotEqual(self.order.transaction_id, "")
		self.assertEqual(self.order.transaction_id, result["TransactionID"])
		
	def test_order_payment_method_set(self):
		"""Test that order payment_method is set correctly."""
		self.assertEqual(self.order.payment_method, "")
		
		PaymentProcessor.process_payment(
			self.customer,
			self.order,
			self.payment
		)
		
		self.assertEqual(self.order.payment_method, "CreditCard")
		
	def test_customer_transaction_history_updated(self):
		"""Test that transaction is added to customer history."""
		initial_count = len(self.customer._transaction_history)
		
		PaymentProcessor.process_payment(
			self.customer,
			self.order,
			self.payment
		)
		
		self.assertEqual(len(self.customer._transaction_history), initial_count + 1)


class TestPaymentProcessorValidation(unittest.TestCase):
	"""Test payment processor validation logic."""

	def setUp(self):
		"""Set up test data."""
		self.customer = Customer("Jane Doe", "jane@example.com")
		self.order = Order(self.customer)
		
		self.item = Item("Phone")
		self.item.price = 800.0
		self.item.stock = 5
		
		self.payment = CreditCardPayment()
		self.payment.cardholder = "Mrs Jane Doe"
		self.payment.cardnumber = "4532123456789012"
		self.payment.expirationdate = "12-25"
		self.payment.cvv = "123"
		self.payment.balance = 2000.0

	def test_empty_order_raises_error(self):
		"""Test that processing empty order raises OrderError."""
		# Order has no items
		with self.assertRaises(OrderError) as context:
			PaymentProcessor.process_payment(
				self.customer,
				self.order,
				self.payment
			)
		self.assertIn("empty", context.exception.message.lower())
		
	def test_non_pending_order_raises_error(self):
		"""Test that processing non-pending order raises OrderError."""
		self.order.add_item(self.item)
		self.order.status = "confirmed"
		
		with self.assertRaises(OrderError) as context:
			PaymentProcessor.process_payment(
				self.customer,
				self.order,
				self.payment
			)
		self.assertIn("confirmed", context.exception.message.lower())
		
	def test_customer_mismatch_raises_error(self):
		"""Test that customer mismatch raises OrderError."""
		self.order.add_item(self.item)
		different_customer = Customer("Bob Smith", "bob@example.com")
		
		with self.assertRaises(OrderError) as context:
			PaymentProcessor.process_payment(
				different_customer,
				self.order,
				self.payment
			)
		self.assertIn("mismatch", context.exception.message.lower())


class TestPaymentProcessorPaymentFailures(unittest.TestCase):
	"""Test payment execution failures."""

	def setUp(self):
		"""Set up test data."""
		self.customer = Customer("Alice Brown", "alice@example.com")
		self.order = Order(self.customer)
		
		self.item = Item("Tablet")
		self.item.price = 500.0
		self.item.stock = 3
		self.order.add_item(self.item)
		
		self.payment = CreditCardPayment()
		self.payment.cardholder = "Ms Alice Brown"
		self.payment.cardnumber = "4532123456789012"
		self.payment.expirationdate = "12-25"
		self.payment.cvv = "123"

	def test_insufficient_balance_raises_error(self):
		"""Test that insufficient balance raises PaymentError."""
		self.payment.balance = 100.0  # Less than order total (500)
		
		with self.assertRaises(PaymentError) as context:
			PaymentProcessor.process_payment(
				self.customer,
				self.order,
				self.payment
			)
		self.assertIn("insufficient", context.exception.message.lower())
		
	def test_invalid_payment_method_raises_error(self):
		"""Test that invalid payment method raises ValidationError."""
		# Create a new payment with expired date
		expired_payment = CreditCardPayment()
		expired_payment.cardholder = "Ms Alice Brown"
		expired_payment.cardnumber = "4532123456789012"
		expired_payment.cvv = "123"
		expired_payment.balance = 1000.0
		# Set expired date - this will raise when validate() is called
		expired_payment._CreditCardPayment__expiration_date = "12-20"  # Bypass setter
		
		with self.assertRaises(ValidationError):
			PaymentProcessor.process_payment(
				self.customer,
				self.order,
				expired_payment
			)


class TestPaymentProcessorErrorContext(unittest.TestCase):
	"""Test that error messages include proper context."""

	def setUp(self):
		"""Set up test data."""
		self.customer = Customer("Test User", "test@example.com")
		self.order = Order(self.customer)
		
		self.item = Item("Item")
		self.item.price = 100.0
		self.item.stock = 5
		self.order.add_item(self.item)
		
		self.payment = CreditCardPayment()
		self.payment.cardholder = "Mr Test User"
		self.payment.cardnumber = "4532123456789012"
		self.payment.expirationdate = "12-25"
		self.payment.cvv = "123"
		self.payment.balance = 50.0  # Insufficient

	def test_payment_error_includes_order_id(self):
		"""Test that payment error includes order ID for context."""
		with self.assertRaises(PaymentError) as context:
			PaymentProcessor.process_payment(
				self.customer,
				self.order,
				self.payment
			)
		
		# Error message should include the order ID
		self.assertIn(self.order.order_id, context.exception.message)


if __name__ == "__main__":
	unittest.main()
