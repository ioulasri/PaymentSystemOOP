from src.core.exceptions import ProjectValueError
from uuid import uuid4

class Item:
    """
    Represents an item in the inventory/order system.

	The Item class manages product information including pricing, stock levels,
	and discount percentages. Each item is assigned a unique ID.

	Attributes:
		name (str): The name of the item.
		id (str): Unique identifier for the item (auto-generated, format: ITEM-UUID).
		price (float): The price of the item (must be positive).
		stock (int): The quantity available in stock (must be non-negative).
		discount (float): Discount percentage as a decimal (0.0 to 1.0).
		quantity (int): The quantity of this item per order (must be positive, default is 1).
	"""
	
	def __init__(self, name: str):
		"""
		Initialize a new Item with default values.

        Args:
                name (str): The name of the item.

		Note:
			Price, stock, and discount are initialized to 0 and should be set
			using their respective property setters for validation.
		"""
		self.name = name
		self.id = f"ITEM-{uuid4().hex[:8].upper()}"
		self._quantity: int = 1
		self._price: float = 0
		self._stock: int = 0
		self._discount: float = 0
	
	@property
	def price(self) -> float:
		"""
		Get the current price of the item.

        Returns:
                float: The item's price.
        """
        return self._price

    @price.setter
    def price(self, value: float) -> None:
        """
        Set the item's price with validation.

        The price must be a positive value greater than zero.

        Args:
                value (float): The new price to set.

        Raises:
                ValueError: If the price is zero or negative.
        """
        if value <= 0:
            raise ProjectValueError("ValueError", "Price should be positive")
        self._price = value

    @property
    def quantity(self) -> int:
        """
        Get the quantity of this item per order.

        Returns:
                int: The quantity of items.
        """
        return self._quantity

    @quantity.setter
    def quantity(self, value: int) -> None:
        """
        Set the item's quantity with validation.

        The quantity must be a positive integer greater than zero.

        Args:
                value (int): The new quantity to set.

        Raises:
                ValueError: If the quantity is zero or negative.
        """
        if value <= 0:
            raise ProjectValueError("ValueError", "Quantity should be positive")
        self._quantity = value

    @property
    def stock(self) -> int:
        """
        Get the current stock quantity.

        Returns:
                int: The quantity of items available in stock.
        """
        return self._stock

    @stock.setter
    def stock(self, value: int) -> None:
        """
        Set the stock quantity with validation.

        The stock quantity must be non-negative (zero or positive).

        Args:
                value (int): The new stock quantity to set.

        Raises:
                ValueError: If the stock quantity is negative.
        """
        if value < 0:
            raise ProjectValueError("ValueError", "Stock amount should be positive")
        self._stock = value

    @property
    def discount(self) -> float:
        """
        Get the discount percentage.

        Returns:
                float: The discount as a decimal (0.0 = no discount, 1.0 = 100% discount).
        """
        return self._discount

    @discount.setter
    def discount(self, value: float) -> None:
        """
        Set the discount percentage with validation.

        The discount must be expressed as a decimal between 0.0 and 1.0,
        where 0.0 represents no discount and 1.0 represents a 100% discount.

        Examples:
                - 0.1 = 10% discount
                - 0.25 = 25% discount
                - 0.5 = 50% discount

        Args:
                value (float): The discount percentage as a decimal (0.0 to 1.0).

        Raises:
                ValueError: If the discount is not in the range [0.0, 1.0].
        """
        if value < 0 or value > 1:
            raise ValueError("ValueError", "discount amount should be in range(0, 1)")
        self._discount = value

    def in_stock(self) -> bool:
        """
        Check if the item is currently available in stock.

        Returns:
                bool: True if stock quantity is greater than 0, False otherwise.
        """
        return self._stock > 0

    def in_discount(self) -> bool:
        """
        Check if the item currently has a discount applied.

        Returns:
                bool: True if discount is greater than 0.0, False otherwise.
        """
        return self._discount > 0.0
