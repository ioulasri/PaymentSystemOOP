from abc import ABC, abstractmethod
from datetime import date
from uuid import uuid4


class PaymentStrategy(ABC):
    def __init__(self) -> None:
        super().__init__()
        self.timestamp: date = date.today()
        self.status: str
        self.transaction_id: str = f"TX-{uuid4()}"
        self._balance: float = 0.0

    @property
    @abstractmethod
    def balance(self) -> float:
        pass

    @abstractmethod
    def validate(self) -> bool:
        pass

    @abstractmethod
    def execute(self, amount: float) -> dict:
        pass

    @abstractmethod
    def generate_receipt(self, amount: float) -> dict:
        pass
