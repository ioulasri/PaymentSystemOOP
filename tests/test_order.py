"""
Comprehensive unit tests for the Order class.

This module tests all functionality of the Order class including:
- Order initialization and UUID generation
- Status property with validation
- Adding and removing items with proper total calculation
- Item validation
- Order status restrictions
- Utility methods (get_item_count, is_empty, calculate_total)
- String representations
"""

import unittest
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path for absolute imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.order.order import Order
from src.order.item import Item
from src.user.customer import Customer
from src.payment.exceptions import OrderError, ProjectTypeError, ProjectValueError


class TestOrderInitialization(unittest.TestCase):
	"""Test Order initialization and default values."""

	def setUp(self):
		"""Create a customer for testing."""
		self.customer = Customer("John Doe", "john@example.com")

	def test_order_creation_with_customer(self):
		"""Test that an order can be created with a customer."""
		order = Order(self.customer)
		self.assertIsNotNone(order)
		self.assertEqual(order.customer, self.customer)

	def test_order_id_generated_automatically(self):
		"""Test that order_id is automatically generated with UUID."""
		order = Order(self.customer)
		self.assertIsNotNone(order.order_id)
		self.assertTrue(order.order_id.startswith("ORD-"))
		self.assertEqual(len(order.order_id), 12)  # "ORD-" + 8 hex chars

	def test_order_id_is_unique(self):
		"""Test that each order gets a unique ID."""
		order1 = Order(self.customer)
		order2 = Order(self.customer)
		self.assertNotEqual(order1.order_id, order2.order_id)

	def test_initial_items_list_empty(self):
		"""Test that items list is empty on initialization."""
		order = Order(self.customer)
		self.assertEqual(len(order.items), 0)
		self.assertTrue(order.is_empty())

	def test_initial_total_amount_zero(self):
		"""Test that total_amount starts at 0.0."""
		order = Order(self.customer)
		self.assertEqual(order.total_amount, 0.0)

	def test_initial_status_pending(self):
		"""Test that status is initialized to 'pending'."""
		order = Order(self.customer)
		self.assertEqual(order.status, "pending")

	def test_created_at_timestamp_set(self):
		"""Test that created_at timestamp is set."""
		order = Order(self.customer)
		self.assertIsInstance(order.created_at, datetime)
		self.assertLessEqual((datetime.now() - order.created_at).total_seconds(), 1)

	def test_payment_method_initially_empty(self):
		"""Test that payment_method is initially an empty string."""
		order = Order(self.customer)
		self.assertEqual(order.payment_method, "")

	def test_transaction_id_initially_empty(self):
		"""Test that transaction_id is initially an empty string."""
		order = Order(self.customer)
		self.assertEqual(order.transaction_id, "")


class TestOrderStatusProperty(unittest.TestCase):
	"""Test the status property with validation."""

	def setUp(self):
		"""Create an order for testing."""
		self.customer = Customer("Jane Doe", "jane@example.com")
		self.order = Order(self.customer)

	def test_valid_status_pending(self):
		"""Test setting status to 'pending'."""
		self.order.status = "pending"
		self.assertEqual(self.order.status, "pending")

	def test_valid_status_confirmed(self):
		"""Test setting status to 'confirmed'."""
		self.order.status = "confirmed"
		self.assertEqual(self.order.status, "confirmed")

	def test_valid_status_processing(self):
		"""Test setting status to 'processing'."""
		self.order.status = "processing"
		self.assertEqual(self.order.status, "processing")

	def test_valid_status_shipped(self):
		"""Test setting status to 'shipped'."""
		self.order.status = "shipped"
		self.assertEqual(self.order.status, "shipped")

	def test_valid_status_delivered(self):
		"""Test setting status to 'delivered'."""
		self.order.status = "delivered"
		self.assertEqual(self.order.status, "delivered")

	def test_valid_status_cancelled(self):
		"""Test setting status to 'cancelled'."""
		self.order.status = "cancelled"
		self.assertEqual(self.order.status, "cancelled")

	def test_invalid_status_raises_error(self):
		"""Test that invalid status raises ValueError."""
		with self.assertRaises(ProjectValueError):
			self.order.status = "invalid_status"

	def test_invalid_status_empty_string(self):
		"""Test that empty string status raises ValueError."""
		with self.assertRaises(ProjectValueError):
			self.order.status = ""

	def test_invalid_status_case_sensitive(self):
		"""Test that status validation is case-sensitive."""
		with self.assertRaises(ProjectValueError):
			self.order.status = "PENDING"

	def test_status_transition_from_pending_to_shipped(self):
		"""Test status can transition from pending to shipped."""
		self.order.status = "pending"
		self.order.status = "shipped"
		self.assertEqual(self.order.status, "shipped")


class TestAddItemMethod(unittest.TestCase):
	"""Test adding items to the order."""

	def setUp(self):
		"""Create order and items for testing."""
		self.customer = Customer("Alice", "alice@example.com")
		self.order = Order(self.customer)
		
		self.item1 = Item("Laptop")
		self.item1.price = 1000.0
		self.item1.stock = 10
		self.item1.discount = 0.0

		self.item2 = Item("Mouse")
		self.item2.price = 50.0
		self.item2.stock = 20
		self.item2.discount = 0.1  # 10% discount

	def test_add_single_item(self):
		"""Test adding a single item to the order."""
		self.order.add_item(self.item1)
		self.assertEqual(len(self.order.items), 1)
		self.assertIn(self.item1, self.order.items)

	def test_add_item_updates_total(self):
		"""Test that adding an item updates total_amount."""
		self.order.add_item(self.item1)
		self.assertEqual(self.order.total_amount, 1000.0)

	def test_add_item_with_discount_updates_total(self):
		"""Test that adding an item with discount calculates correctly."""
		self.order.add_item(self.item2)
		expected_total = 50.0 * (1 - 0.1)  # 45.0
		self.assertEqual(self.order.total_amount, expected_total)

	def test_add_multiple_items(self):
		"""Test adding multiple items to the order."""
		self.order.add_item(self.item1)
		self.order.add_item(self.item2)
		self.assertEqual(len(self.order.items), 2)
		expected_total = 1000.0 + (50.0 * 0.9)
		self.assertAlmostEqual(self.order.total_amount, expected_total, places=2)

	def test_add_item_with_quantity(self):
		"""Test adding an item with quantity > 1."""
		self.item1.quantity = 3
		self.order.add_item(self.item1)
		expected_total = 3 * 1000.0
		self.assertEqual(self.order.total_amount, expected_total)

	def test_add_item_with_quantity_and_discount(self):
		"""Test adding an item with both quantity and discount."""
		self.item2.quantity = 5
		self.order.add_item(self.item2)
		expected_total = 5 * 50.0 * (1 - 0.1)  # 225.0
		self.assertEqual(self.order.total_amount, expected_total)

	def test_add_item_with_zero_quantity_raises_error(self):
		"""Test that adding item with zero quantity raises ValueError."""
		self.item1.quantity = 1  # Reset to valid
		self.order.add_item(self.item1)  # Should work
		
		item3 = Item("Keyboard")
		item3.price = 100.0
		item3.stock = 5
		item3._quantity = 0  # Set directly to bypass property validation
		
		with self.assertRaises(ProjectValueError) as context:
			self.order.add_item(item3)
		self.assertEqual(context.exception.message, "ItemError")

	def test_add_item_with_negative_quantity_raises_error(self):
		"""Test that adding item with negative quantity raises ValueError."""
		item3 = Item("Keyboard")
		item3.price = 100.0
		item3.stock = 5
		item3._quantity = -1
		
		with self.assertRaises(ProjectValueError) as context:
			self.order.add_item(item3)
		self.assertEqual(context.exception.message, "ItemError")

	def test_add_invalid_item_type_raises_error(self):
		"""Test that adding non-Item object raises TypeError."""
		with self.assertRaises(ProjectTypeError) as context:
			self.order.add_item("not an item")
		self.assertEqual(context.exception.message, "TypeError")

	def test_add_item_with_zero_stock_raises_error(self):
		"""Test that adding item with zero stock raises OrderError."""
		item3 = Item("Out of Stock Item")
		item3.price = 100.0
		item3.stock = 0
		
		with self.assertRaises(OrderError) as context:
			self.order.add_item(item3)
		self.assertEqual(context.exception.message, "ItemError")
		self.assertEqual(context.exception.field, "0 items in stock")

	def test_add_item_to_shipped_order_raises_error(self):
		"""Test that adding item to shipped order raises OrderError."""
		self.order.add_item(self.item1)
		self.order.status = "shipped"
		
		with self.assertRaises(OrderError) as context:
			self.order.add_item(self.item2)
		self.assertEqual(context.exception.message, "OrderError")
		self.assertIn("Cannot modify", context.exception.field)

	def test_add_item_to_delivered_order_raises_error(self):
		"""Test that adding item to delivered order raises OrderError."""
		self.order.add_item(self.item1)
		self.order.status = "delivered"
		
		with self.assertRaises(OrderError) as context:
			self.order.add_item(self.item2)
		self.assertEqual(context.exception.message, "OrderError")

	def test_add_item_to_cancelled_order_raises_error(self):
		"""Test that adding item to cancelled order raises OrderError."""
		self.order.status = "cancelled"
		
		with self.assertRaises(OrderError) as context:
			self.order.add_item(self.item1)
		self.assertEqual(context.exception.message, "OrderError")

	def test_add_item_to_pending_order_allowed(self):
		"""Test that adding item to pending order is allowed."""
		self.order.status = "pending"
		self.order.add_item(self.item1)
		self.assertEqual(len(self.order.items), 1)

	def test_add_item_to_confirmed_order_allowed(self):
		"""Test that adding item to confirmed order is allowed."""
		self.order.status = "confirmed"
		self.order.add_item(self.item1)
		self.assertEqual(len(self.order.items), 1)

	def test_add_item_to_processing_order_allowed(self):
		"""Test that adding item to processing order is allowed."""
		self.order.status = "processing"
		self.order.add_item(self.item1)
		self.assertEqual(len(self.order.items), 1)


class TestValidItemMethod(unittest.TestCase):
	"""Test the valid_item validation method."""

	def setUp(self):
		"""Create order and items for testing."""
		self.customer = Customer("Bob", "bob@example.com")
		self.order = Order(self.customer)
		
		self.valid_item = Item("Valid Item")
		self.valid_item.price = 100.0
		self.valid_item.stock = 5

	def test_valid_item_returns_true(self):
		"""Test that a valid item returns True."""
		result = self.order.valid_item(self.valid_item)
		self.assertTrue(result)

	def test_invalid_item_type_raises_error(self):
		"""Test that non-Item object raises TypeError."""
		with self.assertRaises(ProjectTypeError) as context:
			self.order.valid_item("not an item")
		self.assertEqual(context.exception.message, "TypeError")
		self.assertEqual(context.exception.field, "Item type is invalid")

	def test_item_with_zero_stock_raises_error(self):
		"""Test that item with zero stock raises OrderError."""
		zero_stock_item = Item("Zero Stock")
		zero_stock_item.price = 100.0
		zero_stock_item.stock = 0
		
		with self.assertRaises(OrderError) as context:
			self.order.valid_item(zero_stock_item)
		self.assertEqual(context.exception.message, "ItemError")
		self.assertEqual(context.exception.field, "0 items in stock")

	def test_none_raises_error(self):
		"""Test that None raises TypeError."""
		with self.assertRaises(ProjectTypeError):
			self.order.valid_item(None)

	def test_dict_raises_error(self):
		"""Test that dict raises TypeError."""
		with self.assertRaises(ProjectTypeError):
			self.order.valid_item({"name": "item"})

	def test_list_raises_error(self):
		"""Test that list raises TypeError."""
		with self.assertRaises(ProjectTypeError):
			self.order.valid_item([self.valid_item])


class TestRemoveItemMethod(unittest.TestCase):
	"""Test removing items from the order."""

	def setUp(self):
		"""Create order with items for testing."""
		self.customer = Customer("Charlie", "charlie@example.com")
		self.order = Order(self.customer)
		
		self.item1 = Item("Item 1")
		self.item1.price = 100.0
		self.item1.stock = 10
		self.item1.discount = 0.0
		
		self.item2 = Item("Item 2")
		self.item2.price = 200.0
		self.item2.stock = 5
		self.item2.discount = 0.2  # 20% discount

	def test_remove_existing_item_returns_true(self):
		"""Test that removing an existing item returns True."""
		self.order.add_item(self.item1)
		result = self.order.remove_item(self.item1)
		self.assertTrue(result)

	def test_remove_item_removes_from_list(self):
		"""Test that removing an item removes it from items list."""
		self.order.add_item(self.item1)
		self.order.add_item(self.item2)
		self.order.remove_item(self.item1)
		self.assertEqual(len(self.order.items), 1)
		self.assertNotIn(self.item1, self.order.items)
		self.assertIn(self.item2, self.order.items)

	def test_remove_item_updates_total(self):
		"""Test that removing an item updates total_amount."""
		self.order.add_item(self.item1)
		self.order.add_item(self.item2)
		initial_total = self.order.total_amount
		
		self.order.remove_item(self.item1)
		expected_total = initial_total - 100.0
		self.assertAlmostEqual(self.order.total_amount, expected_total, places=2)

	def test_remove_item_with_discount_updates_total(self):
		"""Test that removing item with discount calculates correctly."""
		self.order.add_item(self.item1)
		self.order.add_item(self.item2)
		
		self.order.remove_item(self.item2)
		expected_remaining = 100.0
		self.assertAlmostEqual(self.order.total_amount, expected_remaining, places=2)

	def test_remove_item_with_quantity(self):
		"""Test that removing item with quantity > 1 calculates correctly."""
		self.item1.quantity = 3
		self.order.add_item(self.item1)
		self.assertEqual(self.order.total_amount, 300.0)
		
		self.order.remove_item(self.item1)
		self.assertEqual(self.order.total_amount, 0.0)

	def test_remove_item_with_quantity_and_discount(self):
		"""Test removing item with both quantity and discount."""
		self.item2.quantity = 2
		self.order.add_item(self.item2)
		expected = 2 * 200.0 * (1 - 0.2)  # 320.0
		self.assertEqual(self.order.total_amount, expected)
		
		self.order.remove_item(self.item2)
		self.assertEqual(self.order.total_amount, 0.0)

	def test_remove_nonexistent_item_returns_false(self):
		"""Test that removing non-existent item returns False."""
		self.order.add_item(self.item1)
		
		item3 = Item("Item 3")
		item3.price = 50.0
		item3.stock = 10
		
		result = self.order.remove_item(item3)
		self.assertFalse(result)

	def test_remove_from_empty_order_returns_false(self):
		"""Test that removing from empty order returns False."""
		result = self.order.remove_item(self.item1)
		self.assertFalse(result)

	def test_remove_all_items_makes_order_empty(self):
		"""Test that removing all items results in empty order."""
		self.order.add_item(self.item1)
		self.order.add_item(self.item2)
		
		self.order.remove_item(self.item1)
		self.order.remove_item(self.item2)
		
		self.assertTrue(self.order.is_empty())
		self.assertEqual(self.order.total_amount, 0.0)

	def test_remove_item_by_id_matching(self):
		"""Test that item is removed by ID matching."""
		self.order.add_item(self.item1)
		
		# Create another item with same properties but different ID
		item_copy = Item("Item 1")
		item_copy.price = 100.0
		item_copy.stock = 10
		item_copy.id = self.item1.id  # Same ID
		
		result = self.order.remove_item(item_copy)
		self.assertTrue(result)
		self.assertEqual(len(self.order.items), 0)


class TestCalculateTotalMethod(unittest.TestCase):
	"""Test the calculate_total method."""

	def setUp(self):
		"""Create order with items for testing."""
		self.customer = Customer("Diana", "diana@example.com")
		self.order = Order(self.customer)

	def test_calculate_total_empty_order(self):
		"""Test calculating total for empty order returns 0."""
		total = self.order.calculate_total()
		self.assertEqual(total, 0.0)

	def test_calculate_total_single_item(self):
		"""Test calculating total with single item."""
		item = Item("Item")
		item.price = 150.0
		item.stock = 10
		self.order.add_item(item)
		
		total = self.order.calculate_total()
		self.assertEqual(total, 150.0)

	def test_calculate_total_multiple_items(self):
		"""Test calculating total with multiple items."""
		item1 = Item("Item 1")
		item1.price = 100.0
		item1.stock = 10
		
		item2 = Item("Item 2")
		item2.price = 200.0
		item2.stock = 5
		
		self.order.add_item(item1)
		self.order.add_item(item2)
		
		total = self.order.calculate_total()
		self.assertEqual(total, 300.0)

	def test_calculate_total_with_discounts(self):
		"""Test calculating total with discounted items."""
		item1 = Item("Item 1")
		item1.price = 100.0
		item1.stock = 10
		item1.discount = 0.1  # 10% off
		
		item2 = Item("Item 2")
		item2.price = 200.0
		item2.stock = 5
		item2.discount = 0.25  # 25% off
		
		self.order.add_item(item1)
		self.order.add_item(item2)
		
		total = self.order.calculate_total()
		expected = (100.0 * 0.9) + (200.0 * 0.75)  # 90 + 150 = 240
		self.assertEqual(total, expected)

	def test_calculate_total_with_quantities(self):
		"""Test calculating total with item quantities."""
		item1 = Item("Item 1")
		item1.price = 50.0
		item1.stock = 20
		item1.quantity = 3
		
		item2 = Item("Item 2")
		item2.price = 100.0
		item2.stock = 10
		item2.quantity = 2
		
		self.order.add_item(item1)
		self.order.add_item(item2)
		
		total = self.order.calculate_total()
		expected = (3 * 50.0) + (2 * 100.0)  # 150 + 200 = 350
		self.assertEqual(total, expected)

	def test_calculate_total_with_quantities_and_discounts(self):
		"""Test calculating total with quantities and discounts."""
		item = Item("Item")
		item.price = 100.0
		item.stock = 20
		item.quantity = 4
		item.discount = 0.2  # 20% off
		
		self.order.add_item(item)
		
		total = self.order.calculate_total()
		expected = 4 * 100.0 * (1 - 0.2)  # 320
		self.assertEqual(total, expected)

	def test_calculate_total_updates_total_amount_attribute(self):
		"""Test that calculate_total updates the total_amount attribute."""
		item = Item("Item")
		item.price = 100.0
		item.stock = 10
		self.order.add_item(item)
		
		# Manually corrupt the total
		self.order.total_amount = 999.0
		
		total = self.order.calculate_total()
		self.assertEqual(self.order.total_amount, 100.0)
		self.assertEqual(total, 100.0)

	def test_calculate_total_returns_float(self):
		"""Test that calculate_total returns a float."""
		item = Item("Item")
		item.price = 100.0
		item.stock = 10
		self.order.add_item(item)
		
		total = self.order.calculate_total()
		self.assertIsInstance(total, float)


class TestUtilityMethods(unittest.TestCase):
	"""Test utility methods like get_item_count and is_empty."""

	def setUp(self):
		"""Create order for testing."""
		self.customer = Customer("Eve", "eve@example.com")
		self.order = Order(self.customer)

	def test_is_empty_true_for_new_order(self):
		"""Test that is_empty returns True for new order."""
		self.assertTrue(self.order.is_empty())

	def test_is_empty_false_after_adding_item(self):
		"""Test that is_empty returns False after adding item."""
		item = Item("Item")
		item.price = 100.0
		item.stock = 10
		self.order.add_item(item)
		
		self.assertFalse(self.order.is_empty())

	def test_is_empty_true_after_removing_all_items(self):
		"""Test that is_empty returns True after removing all items."""
		item = Item("Item")
		item.price = 100.0
		item.stock = 10
		self.order.add_item(item)
		self.order.remove_item(item)
		
		self.assertTrue(self.order.is_empty())

	def test_get_item_count_zero_for_empty_order(self):
		"""Test that get_item_count returns 0 for empty order."""
		self.assertEqual(self.order.get_item_count(), 0)

	def test_get_item_count_single_item(self):
		"""Test that get_item_count returns 1 for single item."""
		item = Item("Item")
		item.price = 100.0
		item.stock = 10
		self.order.add_item(item)
		
		self.assertEqual(self.order.get_item_count(), 1)

	def test_get_item_count_multiple_items(self):
		"""Test that get_item_count returns correct count for multiple items."""
		item1 = Item("Item 1")
		item1.price = 100.0
		item1.stock = 10
		
		item2 = Item("Item 2")
		item2.price = 200.0
		item2.stock = 5
		
		item3 = Item("Item 3")
		item3.price = 50.0
		item3.stock = 20
		
		self.order.add_item(item1)
		self.order.add_item(item2)
		self.order.add_item(item3)
		
		self.assertEqual(self.order.get_item_count(), 3)

	def test_get_item_count_after_removal(self):
		"""Test that get_item_count updates after item removal."""
		item1 = Item("Item 1")
		item1.price = 100.0
		item1.stock = 10
		
		item2 = Item("Item 2")
		item2.price = 200.0
		item2.stock = 5
		
		self.order.add_item(item1)
		self.order.add_item(item2)
		self.order.remove_item(item1)
		
		self.assertEqual(self.order.get_item_count(), 1)


class TestStringRepresentations(unittest.TestCase):
	"""Test __repr__ and __str__ methods."""

	def setUp(self):
		"""Create order for testing."""
		self.customer = Customer("Frank", "frank@example.com")
		self.order = Order(self.customer)

	def test_repr_contains_order_id(self):
		"""Test that __repr__ contains order_id."""
		repr_str = repr(self.order)
		self.assertIn(self.order.order_id, repr_str)

	def test_repr_contains_customer_name(self):
		"""Test that __repr__ contains customer name."""
		repr_str = repr(self.order)
		self.assertIn("Frank", repr_str)

	def test_repr_contains_item_count(self):
		"""Test that __repr__ contains item count."""
		item = Item("Item")
		item.price = 100.0
		item.stock = 10
		self.order.add_item(item)
		
		repr_str = repr(self.order)
		self.assertIn("items=1", repr_str)

	def test_repr_contains_total(self):
		"""Test that __repr__ contains total amount."""
		item = Item("Item")
		item.price = 100.0
		item.stock = 10
		self.order.add_item(item)
		
		repr_str = repr(self.order)
		self.assertIn("total=100.00", repr_str)

	def test_repr_format(self):
		"""Test __repr__ format is correct."""
		repr_str = repr(self.order)
		self.assertTrue(repr_str.startswith("Order("))
		self.assertTrue(repr_str.endswith(")"))

	def test_str_contains_order_id(self):
		"""Test that __str__ contains order_id."""
		str_repr = str(self.order)
		self.assertIn(self.order.order_id, str_repr)

	def test_str_contains_item_count(self):
		"""Test that __str__ contains item count."""
		item = Item("Item")
		item.price = 100.0
		item.stock = 10
		self.order.add_item(item)
		
		str_repr = str(self.order)
		self.assertIn("1 items", str_repr)

	def test_str_contains_total_with_dollar_sign(self):
		"""Test that __str__ contains total with dollar sign."""
		item = Item("Item")
		item.price = 100.0
		item.stock = 10
		self.order.add_item(item)
		
		str_repr = str(self.order)
		self.assertIn("$100.00", str_repr)

	def test_str_format_user_friendly(self):
		"""Test that __str__ format is user-friendly."""
		str_repr = str(self.order)
		self.assertTrue(str_repr.startswith("Order"))
		self.assertIn("Total:", str_repr)


class TestOrderIntegration(unittest.TestCase):
	"""Integration tests for complex order scenarios."""

	def setUp(self):
		"""Create order with various items for testing."""
		self.customer = Customer("Grace", "grace@example.com")
		self.order = Order(self.customer)

	def test_complete_order_workflow(self):
		"""Test a complete order workflow from creation to completion."""
		# Add items
		item1 = Item("Laptop")
		item1.price = 1200.0
		item1.stock = 5
		item1.discount = 0.1  # 10% off
		item1.quantity = 1
		
		item2 = Item("Mouse")
		item2.price = 30.0
		item2.stock = 50
		item2.quantity = 2
		
		self.order.add_item(item1)
		self.order.add_item(item2)
		
		# Verify order state
		self.assertEqual(self.order.get_item_count(), 2)
		expected_total = (1200.0 * 0.9) + (2 * 30.0)  # 1080 + 60 = 1140
		self.assertAlmostEqual(self.order.total_amount, expected_total, places=2)
		
		# Update status
		self.order.status = "confirmed"
		self.assertEqual(self.order.status, "confirmed")
		
		# Cannot modify after shipping
		self.order.status = "shipped"
		item3 = Item("Keyboard")
		item3.price = 100.0
		item3.stock = 10
		
		with self.assertRaises(OrderError):
			self.order.add_item(item3)

	def test_order_with_mixed_items_and_recalculation(self):
		"""Test order with mixed items and verify recalculation."""
		items = []
		for i in range(5):
			item = Item(f"Item {i}")
			item.price = 100.0 * (i + 1)
			item.stock = 10
			item.discount = i * 0.05  # 0%, 5%, 10%, 15%, 20%
			item.quantity = i + 1
			items.append(item)
			self.order.add_item(item)
		
		# Manually corrupt the total
		self.order.total_amount = 0.0
		
		# Recalculate
		total = self.order.calculate_total()
		
		# Verify calculation
		expected = sum(
			(i + 1) * 100.0 * (i + 1) * (1 - i * 0.05)
			for i in range(5)
		)
		self.assertAlmostEqual(total, expected, places=2)

	def test_order_state_consistency_after_operations(self):
		"""Test that order state remains consistent after multiple operations."""
		# Add items
		item1 = Item("Item 1")
		item1.price = 100.0
		item1.stock = 10
		
		item2 = Item("Item 2")
		item2.price = 200.0
		item2.stock = 5
		item2.discount = 0.5
		
		self.order.add_item(item1)
		self.order.add_item(item2)
		
		# Remove and re-add
		self.order.remove_item(item1)
		self.order.add_item(item1)
		
		# Verify consistency
		self.assertEqual(self.order.get_item_count(), 2)
		expected = 100.0 + (200.0 * 0.5)  # 100 + 100 = 200
		self.assertAlmostEqual(self.order.total_amount, expected, places=2)
		
		# Recalculate and verify
		recalc_total = self.order.calculate_total()
		self.assertAlmostEqual(recalc_total, expected, places=2)


if __name__ == '__main__':
	unittest.main()
