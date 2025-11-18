from datetime import datetime
from typing import List
import sys
from pathlib import Path
from payment.exceptions import *
from customer.customer import Customer
from item.item import Item

sys.path.append(str(Path(__file__).parent.parent))

class Order:
	def __init__(self, customer: Customer, items: List[Item]):
		self.order_id: str = ""
		self.customer: Customer = customer
		self.items: List[Item] = items
		self.total_amount: float = 0.0
		self.status: str = "pending"
		self.created_at: datetime = datetime.now()
		self.payment_method: str = ""
		self.transaction_id: str = ""

	def add_item(self, item) -> None:
		if not self.valid_item(item):
			raise OrderError("OrderError", "Invalid Item")
		self.items.append(item)

	def valid_item(self, item) -> bool:
		if not isinstance(item, Item):
			raise TypeError("TypeError", "Item type is invalid")
		if item.stock == 0:
			raise OrderError("ItemError", "0 items in stock")
		return True
	
	def remove_item(self, item_id) -> None:
		for item in self.items:
			if item.id == item_id:
				self.items.remove(item)
				break

	