from datetime import datetime
from typing import List
import sys
from pathlib import Path
from payment.exceptions import *
from customer.customer import Customer
from item.item import Item
import uuid

sys.path.append(str(Path(__file__).parent.parent))

class Order:
	"""
	Represents a customer order in the payment system.

	The Order class manages the lifecycle of a customer's purchase, including
	item management, order status tracking, and payment processing coordination.

	Attributes:
		order_id (str): Unique identifier for the order.
		customer (Customer): The customer who placed the order.
		items (List[Item]): List of items included in the order.
		total_amount (float): Total cost of the order (auto-calculated by add_item/remove_item).
		status (str): Current order status (default: "pending").
		created_at (datetime): Timestamp when the order was created.
		payment_method (str): Payment method used for the order.
		transaction_id (str): Transaction identifier from payment processing.
	"""

	def __init__(self, customer: Customer):
		"""
		Initialize a new Order.

		Creates a new order with pending status and current timestamp.
		The total_amount is initialized to 0.0 and will be automatically
		updated when items are added or removed using add_item() and remove_item().

		Args:
			customer (Customer): The customer placing the order.

		Note:
			The order is created with:
			- Order ID: Auto-generated using UUID format "ORD-XXXXXXXX"
			- Status: "pending"
			- Total amount: 0.0 (auto-calculated by add_item/remove_item methods)
			- Created timestamp: current time
			- Empty items list
			- Empty payment_method and transaction_id
		"""
		self.order_id: str = f"ORD-{uuid.uuid4().hex[:8].upper()}"
		self.customer: Customer = customer
		self.items: List[Item] = []
		self.total_amount: float = 0.0
		self._status: str = "pending"
		self.created_at: datetime = datetime.now()
		self.payment_method: str = ""
		self.transaction_id: str = ""

	VALID_STATUSES = ["pending", "confirmed", "processing", "shipped", "delivered", "cancelled"]

	@property
	def status(self) -> str:
		return self._status

	@status.setter
	def status(self, value: str) -> None:
		if value not in Order.VALID_STATUSES:
			raise ValueError(f"Invalid status. Must be one of: {Order.VALID_STATUSES}")
		self._status = value

	def add_item(self, item: Item) -> None:
		"""
		Add an item to the order and update the total amount.

		Validates the item before adding it to the order's item list.
		The item must be a valid Item instance and have stock available.
		Automatically calculates and adds the item's final price (after discount)
		to the order's total amount.

		Args:
			item (Item): The item to add to the order.

		Raises:
			OrderError: If the item validation fails.
			TypeError: If the item is not an Item instance.

		Note:
			The total_amount is automatically updated using the formula:
			item.price * (1 - item.discount)
		"""
		if self.status in ["shipped", "delivered", "cancelled"]:
			raise OrderError("OrderError", "Cannot modify completed/cancelled orders.")
		if item.quantity <= 0:
			raise ValueError("ItemError", "Quantity should be 1 or more")
		if not self.valid_item(item):
			raise OrderError("OrderError", "Invalid Item")
		self.items.append(item)
		self.total_amount += item.quantity * (item.price - item.price * item.discount)

	def valid_item(self, item) -> bool:
		"""
		Validate that an item can be added to the order.

		Performs validation checks:
		1. Verifies the item is an instance of the Item class
		2. Checks that the item has stock available (stock > 0)

		Args:
			item: The item to validate.

		Returns:
			bool: True if the item is valid.

		Raises:
			TypeError: If the item is not an Item instance.
			OrderError: If the item has zero stock.

		Note:
			This method raises exceptions for invalid items rather than
			returning False, so it always returns True if no exception is raised.
		"""
		if not isinstance(item, Item):
			raise TypeError("TypeError", "Item type is invalid")
		if item.stock == 0:
			raise OrderError("ItemError", "0 items in stock")
		return True
	
	def remove_item(self, item: 'Item') -> bool:
		"""
		Remove an item from the order.

		Args:
			item (Item): The item to remove from the order.

		Returns:
			bool: True if the item was found and removed, False otherwise.

		Note:
			Also updates the total amount when an item is removed.
			Accounts for item quantity in the total deduction.
		"""
		for i in self.items:
			if i.id == item.id:
				self.items.remove(i)
				self.total_amount -= (item.quantity * (item.price - item.price * item.discount))
				return True
		return False

	def calculate_total(self) -> float:
		"""
		Recalculate the total amount from all items in the order.

		Returns:
			float: The total amount after applying all discounts.

		Note:
			This method recalculates from scratch using all items currently in the order.
			Useful for verification or after bulk modifications.
		"""
		self.total_amount = sum(
			item.quantity * (item.price - item.price * item.discount)
			for item in self.items
		)
		return self.total_amount

	def get_item_count(self) -> int:
		"""Get total number of items in the order."""
		return len(self.items)

	def is_empty(self) -> bool:
		"""Check if order has no items."""
		return len(self.items) == 0
	
	def __repr__(self) -> str:
		return f"Order(id={self.order_id}, customer={self.customer.name}, items={len(self.items)}, total={self.total_amount:.2f})"

	def __str__(self) -> str:
		return f"Order {self.order_id}: {len(self.items)} items, Total: ${self.total_amount:.2f}"