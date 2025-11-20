"""
Payment System Demo - Showcasing the complete payment flow.

This demo demonstrates:
- Creating customers and orders
- Processing payments with different payment methods
- Error handling and validation
- The Facade and Strategy design patterns in action
"""

import sys
from pathlib import Path

# Add project root to path for absolute imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.models.item import Item
from src.models.order import Order
from src.models.customer import Customer
from src.payment.methods.credit_card import CreditCardPayment
from src.payment.methods.paypal import Paypal
from src.services.payment_processor import PaymentProcessor
from src.core.exceptions import PaymentError, OrderError, ValidationError


def demo_successful_payment():
	"""Demonstrate a successful credit card payment."""
	print("=" * 60)
	print("DEMO 1: Successful Credit Card Payment")
	print("=" * 60)
	
	# 1. Create a customer
	customer = Customer("Mr Imad Oulasri", "imad.oulasri01@gmail.com")
	print(f"\n✓ Customer created: {customer._name} ({customer._user_id})")
	
	# 2. Create order with items
	order = Order(customer=customer)
	print(f"✓ Order created: {order.order_id}")
	
	# Add items to order
	laptop = Item("MacBook Pro")
	laptop.price = 2499.99
	laptop.stock = 5
	
	mouse = Item("Magic Mouse")
	mouse.price = 79.99
	mouse.stock = 10
	
	order.add_item(laptop)
	order.add_item(mouse)
	print(f"✓ Added {len(order.items)} items to order")
	print(f"  - {laptop.name}: ${laptop.price}")
	print(f"  - {mouse.name}: ${mouse.price}")
	print(f"  Total: ${order.total_amount:.2f}")
	
	# 3. Set up credit card payment
	credit_card = CreditCardPayment()
	credit_card.cardholder = "Mr Imad Oulasri"
	credit_card.cardnumber = "4532123456789012"
	credit_card.expirationdate = "12-27"
	credit_card.cvv = "123"
	credit_card.balance = 5000.00
	print(f"\n✓ Credit card set up")
	print(f"  Balance: ${credit_card.balance:.2f}")
	
	# 4. Process payment
	print(f"\n⏳ Processing payment...")
	receipt = PaymentProcessor.process_payment(customer, order, credit_card)
	
	# 5. Show results
	print(f"\n✅ PAYMENT SUCCESSFUL!")
	print(f"  Transaction ID: {receipt['TransactionID']}")
	print(f"  Amount: ${receipt['Amount']:.2f}")
	print(f"  Payment Method: {receipt['PaymentMethod']}")
	print(f"  Card: {receipt['CardNumber']}")
	print(f"  Status: {receipt['Transaction status']}")
	print(f"\n  Order Status: {order.status}")
	print(f"  Remaining Balance: ${credit_card.balance:.2f}")
	print()


def demo_multiple_payment_methods():
	"""Demonstrate using different payment methods (Strategy Pattern)."""
	print("=" * 60)
	print("DEMO 2: Multiple Payment Methods (Strategy Pattern)")
	print("=" * 60)
	
	# Create customer and order
	customer = Customer("Mrs Jane Smith", "jane.smith@email.com")
	order = Order(customer=customer)
	
	phone = Item("iPhone 15 Pro")
	phone.price = 999.99
	phone.stock = 3
	order.add_item(phone)
	
	print(f"\n✓ Order: {order.order_id}")
	print(f"  Customer: {customer._name}")
	print(f"  Item: {phone.name}")
	print(f"  Total: ${order.total_amount:.2f}")
	
	# Payment with PayPal
	print(f"\n💳 Paying with PayPal...")
	paypal = Paypal()
	paypal.emailaddress = "jane.smith@email.com"
	paypal.passwordtoken = "SecurePass123!"
	paypal.verified = True
	paypal.balance = 2000.00
	
	receipt = PaymentProcessor.process_payment(customer, order, paypal)
	print(f"✅ Payment successful via {receipt['PaymentMethod']}")
	print(f"  Transaction: {receipt['TransactionID']}")
	print()


def demo_error_handling():
	"""Demonstrate error handling and validation."""
	print("=" * 60)
	print("DEMO 3: Error Handling & Validation")
	print("=" * 60)
	
	customer = Customer("Mr Bob Wilson", "bob@email.com")
	
	# Error 1: Empty order
	print(f"\n❌ Test 1: Empty Order")
	empty_order = Order(customer=customer)
	credit_card = CreditCardPayment()
	credit_card.cardholder = "Mr Bob Wilson"
	credit_card.cardnumber = "4532123456789012"
	credit_card.expirationdate = "12-26"
	credit_card.cvv = "456"
	credit_card.balance = 1000.00
	
	try:
		PaymentProcessor.process_payment(customer, empty_order, credit_card)
	except OrderError as e:
		print(f"  Caught: {e.message}")
		print(f"  ✓ Validation working correctly!")
	
	# Error 2: Insufficient balance
	print(f"\n❌ Test 2: Insufficient Balance")
	order = Order(customer=customer)
	expensive_item = Item("Luxury Watch")
	expensive_item.price = 5000.00
	expensive_item.stock = 1
	order.add_item(expensive_item)
	
	credit_card.balance = 100.00  # Not enough!
	
	try:
		PaymentProcessor.process_payment(customer, order, credit_card)
	except PaymentError as e:
		print(f"  Caught: {e.message}")
		print(f"  ✓ Payment validation working correctly!")
	
	# Error 3: Wrong customer
	print(f"\n❌ Test 3: Customer Mismatch")
	different_customer = Customer("Mr Alice Brown", "alice@email.com")
	
	try:
		PaymentProcessor.process_payment(different_customer, order, credit_card)
	except OrderError as e:
		print(f"  Caught: {e.message}")
		print(f"  ✓ Customer validation working correctly!")
	
	print()


def main():
	"""Run all demos."""
	print("\n")
	print("╔" + "═" * 58 + "╗")
	print("║" + " " * 58 + "║")
	print("║" + "    PAYMENT SYSTEM DEMONSTRATION".center(58) + "║")
	print("║" + "    OOP Design Patterns in Action".center(58) + "║")
	print("║" + " " * 58 + "║")
	print("╚" + "═" * 58 + "╝")
	print()
	
	# Run all demos
	demo_successful_payment()
	demo_multiple_payment_methods()
	demo_error_handling()
	
	# Summary
	print("=" * 60)
	print("SUMMARY")
	print("=" * 60)
	print("✓ Strategy Pattern: Multiple payment methods")
	print("✓ Facade Pattern: PaymentProcessor orchestrates the flow")
	print("✓ Validation: Pre-payment checks prevent errors")
	print("✓ Error Handling: Graceful failure with clear messages")
	print("✓ Complete Flow: Customer → Order → Payment → Receipt")
	print("=" * 60)
	print("\n✅ All demos completed successfully!\n")


if __name__ == "__main__":
	main()