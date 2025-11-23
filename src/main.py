"""
Payment System Demo - Showcasing the complete payment flow.

This demo demonstrates:
- Creating customers and orders
- Using the PaymentFactory to create payment methods
- Processing payments with different payment methods
- Error handling and validation
- The Factory, Facade, and Strategy design patterns in action
"""

import sys
from pathlib import Path

# Add project root to path for absolute imports (MUST come before other imports)
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Now we can import from src (E402 is intentional - path must be set first)
from src.core.exceptions import OrderError, PaymentError  # noqa: E402
from src.models.customer import Customer  # noqa: E402
from src.models.item import Item  # noqa: E402
from src.models.order import Order  # noqa: E402
from src.services.payment_factory import PaymentFactory  # noqa: E402
from src.services.payment_processor import PaymentProcessor  # noqa: E402


def demo_successful_payment() -> None:
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

    # 3. Set up credit card payment using Factory
    print("\n⚙️  Creating credit card payment with Factory...")
    credit_card = PaymentFactory.create(
        "credit_card",
        cardholder="Mr Imad Oulasri",
        cardnumber="4532123456789012",
        expirationdate="12-27",
        cvv="123",
        balance=5000.00,
    )
    print("✓ Credit card payment created and validated")
    # Type assertion: we know it's a CreditCardPayment with balance attribute
    from src.payment.methods.credit_card import CreditCardPayment

    if not isinstance(credit_card, CreditCardPayment):
        raise TypeError("Expected CreditCardPayment instance")
    print(f"  Balance: ${credit_card.balance:.2f}")

    # 4. Process payment
    print("\n⏳ Processing payment...")
    receipt = PaymentProcessor.process_payment(customer, order, credit_card)

    # 5. Show results
    print("\n✅ PAYMENT SUCCESSFUL!")
    print(f"  Transaction ID: {receipt['TransactionID']}")
    print(f"  Amount: ${receipt['Amount']:.2f}")
    print(f"  Payment Method: {receipt['PaymentMethod']}")
    print(f"  Card: {receipt['CardNumber']}")
    print(f"  Status: {receipt['Transaction status']}")
    print(f"\n  Order Status: {order.status}")
    print(f"  Remaining Balance: ${credit_card.balance:.2f}")
    print()


def demo_payment_factory() -> None:
    """Demonstrate the Payment Factory pattern."""
    print("=" * 60)
    print("DEMO 2: Payment Factory Pattern")
    print("=" * 60)

    customer = Customer("Mr David Chen", "david.chen@email.com")
    order = Order(customer=customer)

    headphones = Item("AirPods Pro")
    headphones.price = 249.99
    headphones.stock = 15
    order.add_item(headphones)

    print(f"\n✓ Order: {order.order_id}")
    print(f"  Customer: {customer._name}")
    print(f"  Item: {headphones.name}")
    print(f"  Total: ${order.total_amount:.2f}")

    # Test Factory with different payment types
    print("\n⚙️  Testing Factory Pattern with Multiple Payment Types:")

    # 1. Credit Card via Factory
    print("\n  1️⃣  Creating Credit Card payment...")
    cc_payment = PaymentFactory.create(
        "credit_card",
        cardholder="Mr David Chen",
        cardnumber="5500000000000004",
        expirationdate="06-28",
        cvv="789",
        balance=1000.00,
    )
    print(f"     ✓ Type: {cc_payment.__class__.__name__}")

    # 2. PayPal via Factory
    print("\n  2️⃣  Creating PayPal payment...")
    pp_payment = PaymentFactory.create(
        "paypal",
        emailaddress="david.chen@email.com",
        passwordtoken="SecureToken456",
        verified=True,
        balance=500.00,
    )
    print(f"     ✓ Type: {pp_payment.__class__.__name__}")

    # 3. Crypto via Factory
    print("\n  3️⃣  Creating Crypto payment...")
    crypto_payment = PaymentFactory.create(
        "crypto",
        wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
        network="ethereum",
    )
    print(f"     ✓ Type: {crypto_payment.__class__.__name__}")

    print("\n✅ Factory successfully created all payment types!")
    print("   All payments are validated automatically by the factory.")
    print()


def demo_multiple_payment_methods() -> None:
    """Demonstrate using different payment methods (Strategy Pattern)."""
    print("=" * 60)
    print("DEMO 3: Multiple Payment Methods (Strategy Pattern)")
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

    # Payment with PayPal using Factory
    print("\n⚙️  Creating PayPal payment with Factory...")
    paypal = PaymentFactory.create(
        "paypal",
        emailaddress="jane.smith@email.com",
        passwordtoken="SecurePass123!",
        verified=True,
        balance=2000.00,
    )
    print("✓ PayPal payment created and validated")

    receipt = PaymentProcessor.process_payment(customer, order, paypal)
    print(f"✅ Payment successful via {receipt['PaymentMethod']}")
    print(f"  Transaction: {receipt['TransactionID']}")
    print()


def demo_error_handling() -> None:
    """Demonstrate error handling and validation."""
    print("=" * 60)
    print("DEMO 4: Error Handling & Validation")
    print("=" * 60)

    customer = Customer("Mr Bob Wilson", "bob@email.com")

    # Error 1: Empty order
    print("\n❌ Test 1: Empty Order")
    empty_order = Order(customer=customer)
    credit_card = PaymentFactory.create(
        "credit_card",
        cardholder="Mr Bob Wilson",
        cardnumber="4532123456789012",
        expirationdate="12-26",
        cvv="456",
        balance=1000.00,
    )

    try:
        PaymentProcessor.process_payment(customer, empty_order, credit_card)
    except OrderError as e:
        print(f"  Caught: {e.message}")
        print("  ✓ Validation working correctly!")

    # Error 2: Insufficient balance
    print("\n❌ Test 2: Insufficient Balance")
    order = Order(customer=customer)
    expensive_item = Item("Luxury Watch")
    expensive_item.price = 5000.00
    expensive_item.stock = 1
    order.add_item(expensive_item)

    # Type assertion for balance access
    from src.payment.methods.credit_card import CreditCardPayment

    if not isinstance(credit_card, CreditCardPayment):
        raise TypeError("Expected CreditCardPayment instance")
    credit_card.balance = 100.00  # Not enough!

    try:
        PaymentProcessor.process_payment(customer, order, credit_card)
    except PaymentError as e:
        print(f"  Caught: {e.message}")
        print("  ✓ Payment validation working correctly!")

    # Error 3: Wrong customer
    print("\n❌ Test 3: Customer Mismatch")
    different_customer = Customer("Mr Alice Brown", "alice@email.com")

    try:
        PaymentProcessor.process_payment(different_customer, order, credit_card)
    except OrderError as e:
        print(f"  Caught: {e.message}")
        print("  ✓ Customer validation working correctly!")

    print()


def main() -> None:
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
    demo_payment_factory()
    demo_multiple_payment_methods()
    demo_error_handling()

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("✓ Factory Pattern: Centralized payment creation with validation")
    print("✓ Strategy Pattern: Multiple payment methods")
    print("✓ Facade Pattern: PaymentProcessor orchestrates the flow")
    print("✓ Validation: Pre-payment checks prevent errors")
    print("✓ Error Handling: Graceful failure with clear messages")
    print("✓ Complete Flow: Customer → Order → Payment → Receipt")
    print("=" * 60)
    print("\n✅ All demos completed successfully!\n")


if __name__ == "__main__":
    main()
