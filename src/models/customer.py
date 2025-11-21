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

import sys
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from src.models.user import User

# Add parent directory to path to enable imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


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

    def __init__(self, name: str, email: str):
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
        self._user_id = f"USR-{uuid4()}"
        self._name = name
        self._email = email
        self._wallets: Dict[str, Any] = {}
        self._transaction_history: List[Dict[str, Any]] = []
        self._saved_payment_methods: List[Any] = []
        self._fraud_status: str = "clear"
        self._failed_attempts: int = 0
        # mark active by default
        self._is_active: bool = True
        # Lock to protect wallet/transaction updates in multithreaded use
        # (RLock allows reentrant calls inside the same thread).
        from threading import RLock

        self._lock = RLock()

    @property
    def name(self) -> str:
        """Return the customer's name."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Set the customer's name."""
        self._name = value

    @property
    def email(self) -> str:
        """Return the customer's email."""
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        """Set the customer's email."""
        self._email = value

    @property
    def is_active(self) -> bool:
        """Return whether the customer is active."""
        return self._is_active

    @is_active.setter
    def is_active(self, value: bool) -> None:
        """Set whether the customer is active."""
        self._is_active = value

    @property
    def user_id(self) -> str:
        """Return the customer's user ID."""
        return self._user_id

    @property
    def failed_attempts(self) -> int:
        """Return the number of recent failed attempts."""
        return self._failed_attempts

    @failed_attempts.setter
    def failed_attempts(self, value: int) -> None:
        """Set the number of recent failed attempts."""
        self._failed_attempts = value

    @property
    def fraud_status(self) -> str:
        """Return the current fraud status."""
        return self._fraud_status

    @fraud_status.setter
    def fraud_status(self, value: str) -> None:
        """Set the current fraud status."""
        self._fraud_status = value

    @property
    def saved_payment_methods(self) -> List[Any]:
        """Return the list of saved payment methods."""
        return self._saved_payment_methods

    @property
    def wallets(self) -> Dict[str, Any]:
        """Return the dictionary of wallets."""
        return self._wallets

    @property
    def transaction_history(self) -> List[Dict[str, Any]]:
        """Return the transaction history list."""
        return self._transaction_history

    @property
    def balance(self) -> float:
        """Return the aggregated balance across all wallets.

        The method attempts to coerce wallet entries to numeric balances.
        Wallet objects may provide helper methods (``get_balance``); if
        an entry cannot be converted to float it is ignored.
        """
        # Prefer the view_balance method for a robust aggregation. Keep
        # the property for convenience but implement via the same logic.
        return self.view_balance()

    def deactivate(self) -> None:
        """Mark the user as inactive.

        Exposed as a method (not a property) to match common usage and
        to avoid accidental deactivation via attribute access.
        """
        self._is_active = False

    def get_user_info(self) -> Dict[str, Any]:
        """Return a JSON-serializable mapping with basic user info.

        This mirrors the shape returned by :class:`Admin` so callers can
        treat different user types uniformly.
        """
        return {
            "id": self._user_id,
            "name": self._name,
            "email": self._email,
            "role": getattr(self, "_role", "customer"),
            "is_active": bool(getattr(self, "_is_active", True)),
        }

    def view_balance(self) -> float:
        """Return the aggregated numeric balance across all wallets.

        The method is defensive: it supports wallet objects that expose a
        `get_balance()` method, objects with a numeric `balance` attr, or
        plain numeric values. Any non-coercible entries are ignored. A
        lock protects concurrent access/modification of wallets.
        """
        total: float = 0.0
        with self._lock:
            for wallet in self._wallets.values():
                try:
                    if hasattr(wallet, "get_balance"):
                        total += float(wallet.get_balance())
                    elif hasattr(wallet, "balance"):
                        total += float(getattr(wallet, "balance"))
                    else:
                        total += float(wallet)
                except (TypeError, ValueError, AttributeError):
                    # Ignore non-coercible wallet entries
                    continue

        return total

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

        # Basic validation
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            raise ValueError("Amount must be a number")
        if amount <= 0:
            raise ValueError("Amount must be positive")

        # Perform wallet update inside the lock to avoid races.
        try:
            with self._lock:
                if hasattr(wallet, "deduct"):
                    wallet.deduct(amount)
                elif hasattr(wallet, "get_balance") and hasattr(wallet, "set_balance"):
                    new_balance = float(wallet.get_balance()) - amount
                    wallet.set_balance(new_balance)
                else:
                    current = float(wallet)
                    new = current - amount
                    self._wallets[method] = new
        except (TypeError, ValueError, AttributeError) as exc:
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
