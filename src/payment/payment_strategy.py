from abc import ABC, abstractmethod

class PaymentStrategy(ABC):
	def __init__(self):
		super().__init__()
		self._timestamp
		self._transaction_id
		self.status

	@abstractmethod
	def validate(self) -> bool:
		pass

	@abstractmethod
	def execute(self, amount) -> dict:
		pass

	@abstractmethod
	def generate_receipt(self) -> dict:
		pass
