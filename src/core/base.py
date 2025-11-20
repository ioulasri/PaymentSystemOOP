from abc import ABC, abstractmethod
from datetime import date
from uuid import uuid4


class PaymentStrategy(ABC):
    def __init__(self):
        super().__init__()
        self.timestamp: date = date.today()
        self.status: str
        self.transaction_id: str = f"TX-{uuid4()}"

    @abstractmethod
    def validate(self) -> bool:
        pass

    @abstractmethod
    def execute(self, amount) -> dict:
        pass

    @abstractmethod
    def generate_receipt(self) -> dict:
        pass
