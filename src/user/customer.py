"""Customer model for the payment system.

This module provides the ``Customer`` class which extends the abstract
base `User` class. The implementation stores simple in-memory structures
for wallets, transaction history and saved payment methods. The file is
documented so other developers understand the intent and the shape of
the data.

Notes
-----
This is a lightweight, example-style implementation intended for tests
and local runs. In production you'd replace wallet objects with proper
services or adapters and persist transaction history to a database.
"""

from typing import Any, Dict, List
from uuid import uuid4
import sys
from pathlib import Path

# Add parent directory to path to enable imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.user.user import User


class Customer(User):
    """Represents a customer using the payment system.

    Attributes
    ----------
    _user_id : str
        Unique identifier for the customer.
    _name : str
        Customer's name.
    _email : str
        Customer's contact email.
    _wallets : Dict[str, Any]
        Mapping of payment method identifiers to wallet-like objects or
        numeric balances. Wallet objects may implement helper methods
        like ``get_balance``, ``set_balance`` or ``deduct``; the
        Customer methods handle these cases heuristically.
    _transaction_history : List[Dict[str, Any]]
        In-memory append-only list of transaction records.
    _saved_payment_methods : List[Any]
        Stored payment method descriptors (tokens, IDs, etc.).
    _fraud_status : str
        Short string indicating fraud review state (for example,
        ``'clear'`` or ``'under_review'``).
    _failed_attempts : int
        Counter for recent failed attempts (useful for throttling).
    """

    def __init__(self, user_id: str, name: str, email: str):
        """Create a Customer instance.

        Parameters
        ----------
        user_id : str
            Unique identifier for the user.
        name : str
            Human-readable name.
        email : str
            Contact email.
        """
        super().__init__()
        self._user_id = user_id
        self._name = name
        self._email = email
        self._wallets: Dict[str, Any] = {}
        self._transaction_history: List[Dict[str, Any]] = []
        self._saved_payment_methods: List[Any] = []
        self._fraud_status: str = "clear"
        self._failed_attempts: int = 0
        # mark active by default
        self._is_active: bool = True

    def get_user_info(self) -> Dict[str, Any]:
        """Return a serializable mapping with basic user information."""
        return {
            "id": self._user_id,
            "name": self._name,
            "email": self._email,
            "role": getattr(self, "_role", "customer"),
            "is_active": bool(getattr(self, "_is_active", True)),
        }

    def deactivate(self) -> None:
        """Mark the user as inactive."""
        self._is_active = False

    def view_balance(self) -> float:
        """Return the aggregated balance across all wallets.

        The method attempts to coerce wallet entries to numeric balances.
        Wallet objects may provide helper methods (``get_balance``); if
        an entry cannot be converted to float it is ignored.
        """
        balance = 0.0
        for wallet in self._wallets.values():
            try:
                if hasattr(wallet, "get_balance"):
                    balance += float(wallet.get_balance())
                else:
                    balance += float(wallet)
            except Exception:
                # Ignore wallets that can't be interpreted as numbers
                continue
        return balance

    def add_transaction(self, transaction: Dict[str, Any]) -> None:
        """Append a transaction record to the customer's history.

        Parameters
        ----------
        transaction : dict
            A mapping describing the transaction (id, amount, status,
            optional error message, etc.).
        """
        self._transaction_history.append(transaction)

    def view_transaction_history(self) -> List[Dict[str, Any]]:
        """Return a shallow copy of the transaction history list.

        Returns a new list so callers cannot mutate the internal
        history accidentally.
        """
        return list(self._transaction_history)

    def initiate_payment(self, amount: float, method: str) -> Dict[str, Any]:
        """Attempt to pay `amount` using `method` and record the result.

        The method performs simple checks and updates in-memory wallet
        objects if present. It returns a transaction record describing
        the result and always appends that record to history.

        Parameters
        ----------
        amount : float
            Amount to charge.
        method : str
            Identifier of the payment method to use (must be present in
            ``_saved_payment_methods``).

        Returns
        -------
        dict
            Transaction record including ``id``, ``amount``, ``method``,
            ``status`` and optional ``error``.
        """
        if method not in self._saved_payment_methods:
            raise ValueError("Payment method not recognized")

        wallet = self._wallets.get(method)
        txn_id = str(uuid4())
        transaction = {
            "id": txn_id,
            "amount": amount,
            "method": method,
            "status": "failed",
        }

        if wallet is None:
            transaction["error"] = "no wallet configured for method"
            self.add_transaction(transaction)
            return transaction

        try:
            if hasattr(wallet, "deduct"):
                wallet.deduct(amount)
            elif hasattr(wallet, "get_balance") and hasattr(wallet, "set_balance"):
                new_balance = float(wallet.get_balance()) - float(amount)
                wallet.set_balance(new_balance)
            else:
                current = float(wallet)
                new = current - float(amount)
                self._wallets[method] = new
        except Exception as exc:
            transaction["error"] = str(exc)
            self.add_transaction(transaction)
            return transaction

        transaction["status"] = "success"
        self.add_transaction(transaction)
        return transaction

    def save_payment_method(self, method: Any) -> None:
        """Persist a payment method for future use.

        The stored descriptor is opaque to this class — it can be a
        string token, a payment-method object or any identifier used by
        payment backends.
        """
        if method not in self._saved_payment_methods:
            self._saved_payment_methods.append(method)

    def get_fraud_status(self) -> str:
        """Return the customer's fraud review status string."""
        return self._fraud_status