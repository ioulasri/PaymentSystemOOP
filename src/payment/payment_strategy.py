from abc import ABC, abstractmethod

class PaymentStrategy(ABC):
	@abstractmethod
	def validate(self) -> bool:
		pass

	@abstractmethod
	def execute(self, amount) -> dict:
		pass

	@abstractmethod
	def generate_receipt(self) -> dict:
		pass
