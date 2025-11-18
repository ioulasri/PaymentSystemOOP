class Item:
	_next_id = 1000
	def __init__(self, name):
		self.name = name
		self.id = Item._next_id
		self._price: float = 0
		self._stock: int = 0
		self._discount: float = 0
		Item._next_id += 1
	
	@property
	def price(self):
		return self.price
	
	@price.setter
	def price(self, value):
		if value <= 0:
			raise ValueError("ValueError", "Price should be positive")
		self._price = value

	@property
	def stock(self):
		return self.stock
	
	@stock.setter
	def stock(self, value):
		if value < 0:
			raise ValueError("ValueError", "Stock amount should be positive")
		self._stock = value
	
	@property
	def discount(self):
		return self.discount
	
	@discount.setter
	def discount(self, value):
		if value < 0 or value > 1:
			raise ValueError("ValueError", "discount amount should be in range(0, 1)")
		self._discount = value

	def in_stock(self) -> bool:
		return self.stock > 0
	
	def in_discount(self) -> bool:
		return self.discount > 0.0