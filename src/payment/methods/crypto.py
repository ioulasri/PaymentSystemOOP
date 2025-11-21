"""Crypto payment strategy.

This module provides a lightweight, example implementation of a
cryptocurrency payment strategy used by the payment system. It is
intended for tests and local development only and deliberately avoids
integration with real blockchain networks.

The :class:`CryptoPayment` class below implements a small set of
behaviours:

- configuring a wallet address and network
- validating address formats (simple regex rules plus optional
    third-party validator)
- simulating payment execution and fee estimation
- a handful of convenience helpers (tracking, refunds, invoice
    generation, currency conversion and scheduling)

Note: This module is an example; do not use it as a production-grade
crypto payment implementation. It uses in-memory state and simple
heuristics so unit tests can exercise deterministic behaviour.
"""

import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from src.core.base import PaymentStrategy
from src.core.exceptions import PaymentError, ValidationError

# Optional import for enhanced crypto address validation
try:
    import coinaddrvalidator

    HAS_COINADDR_VALIDATOR = True
except ImportError:
    HAS_COINADDR_VALIDATOR = False


class CryptoPayment(PaymentStrategy):
    """Example PaymentStrategy for cryptocurrency payments.

    This class implements the abstract :class:`PaymentStrategy` API
    with a minimal, test-friendly behaviour set. It keeps a simple
    in-memory balance and wallet configuration and exposes methods
    to validate an address, execute simulated payments and return
    small dictionaries representing transactions, receipts and
    related objects.

    The implementation intentionally simplifies many aspects of
    real crypto payments (no network submission, no persistence,
    and deterministic fee calculation).
    """

    def __init__(self) -> None:
        """Initialize the payment strategy.

        The instance maintains a small amount of local state used by
        the example implementation:

        - ``_wallet_address``: optional string wallet address
        - ``_network``: optional network identifier (e.g. 'ethereum')
        - ``_balance``: in-memory float representing available funds

        Timestamp and a default transaction id are provided by the
        base :class:`PaymentStrategy` class.
        """
        super().__init__()
        self._wallet_address: Optional[str] = None
        self._network: Optional[str] = None
        self._balance: float = 0.0

    @property
    def balance(self) -> float:
        """Return the current in-memory balance.

        This value is for example/test purposes only and is not
        persisted to any external store.
        """
        return self._balance

    @balance.setter
    def balance(self, value: float) -> None:
        """Set the in-memory balance.

        A negative balance is invalid and raises :class:`ValueError`.
        """
        if value < 0:
            raise ValidationError("ValidationError", "Balance cannot be negative.")
        self._balance = value

    @property
    def wallet_address(self) -> Optional[str]:
        """Return the configured wallet address or ``None`` if unset."""
        return self._wallet_address

    @wallet_address.setter
    def wallet_address(self, value: str) -> None:
        """Set the configured wallet address.

        This setter does not validate the address format; call
        :meth:`validate` to perform checks after setting values.
        """
        self._wallet_address = value

    @property
    def network(self) -> Optional[str]:
        """Return the configured network identifier or ``None`` if unset."""
        return self._network

    @network.setter
    def network(self, value: str) -> None:
        """Set the configured network (e.g. 'ethereum' or 'bitcoin')."""
        self._network = value

    def validate(self) -> bool:
        """Validate the configured wallet and address format.

        This method performs a small set of checks:

        1. Ensure both a wallet address and network are configured.
        2. If the optional ``coinaddrvalidator`` package is available
           use it to validate the address; otherwise fall back to
           internal regex-based checks for Bitcoin and Ethereum.

        The method raises :class:`ValidationError` on missing or
        invalid configuration (this mirrors the behaviour used in the
        test-suite). It returns ``True`` when validation succeeds.
        """
        # Basic checks first
        if not self._wallet_address:
            raise ValidationError("ValidationError", "Wallet address is required.")
        if not self._network:
            raise ValidationError("ValidationError", "Network is required.")

        # Enhanced validation if coinaddrvalidator is available
        if HAS_COINADDR_VALIDATOR:
            if coinaddrvalidator.validate(
                self._network, self._wallet_address.encode()
            ).valid:
                raise ValidationError(
                    "ValidationError", "Invalid wallet address format."
                )
            return True
        # Basic regex validation for common address formats
        return self._validate_address_format()

    def _validate_address_format(self) -> bool:
        """Validate address format using simplistic regex rules.

        This helper contains lightweight regular expressions for a few
        common address types:

        - Bitcoin (legacy, segwit, bech32)
        - Ethereum (0x-prefixed 40-hex-char address)

        The method returns ``True`` when the address matches the
        expected pattern for the configured network and raises
        :class:`ValidationError` for unsupported networks or obvious
        invalid formats.
        """
        network = str(self._network)
        address = str(self._wallet_address)

        # Bitcoin-like addresses (legacy, segwit, bech32)
        if network in ["bitcoin", "BTC", "testnet"]:
            # Legacy: 1... (25-34 chars), Segwit: 3... (25-34 chars),
            # Bech32: bc1... (42-62 chars)
            pattern = r"^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$|^bc1[a-z0-9]{39,59}$"
            if bool(re.match(pattern, address)):
                return True
            raise ValidationError("ValidationError", "Invalid wallet address format.")

        # Ethereum-like addresses
        elif network in ["ethereum", "ETH"]:
            # 0x followed by 40 hex characters
            pattern = r"^0x[a-fA-F0-9]{40}$"
            if bool(re.match(pattern, address)):
                return True
            raise ValidationError("ValidationError", "Invalid wallet address format.")
        raise ValidationError(
            "ValidationError", "Unsupported network for address validation."
        )

    def execute(self, amount: float) -> Dict[str, Any]:
        """Execute a crypto payment and return a transaction record.

        The method performs basic validation and then simulates a
        payment by deducting the amount (minus the estimated fee)
        from the in-memory balance and returning a small transaction
        dictionary. Errors are surfaced via :class:`PaymentError`.
        """
        # set canonical metadata on the strategy instance
        tx_id = str(uuid4())
        ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self._transaction_id = tx_id
        self._timestamp = ts
        self.status = "completed"
        self.validate()
        if float(amount) <= 0:
            raise PaymentError("PaymentError", "Amount must be positive.")
        if float(amount) > self._balance:
            raise PaymentError("PaymentError", "Insufficient balance for payment.")

        # Simulate execution and include fee estimation
        try:
            fee = self.estimate_fees(float(amount))
            self._balance -= float(amount) + fee
            transaction = {
                "TransactionID": tx_id,
                "Transaction status": self.status,
                "TransactionType": "Crypto",
                "Amount": amount,
                "Fee": fee,
                "Timestamp": ts,
            }
            return transaction
        except Exception as exc:
            raise PaymentError(f"PaymentError: Failed to execute payment: {exc}")

    def estimate_fees(self, amount: float) -> float:
        """Estimate network fees for a given amount.

        This uses a simple percentage heuristic in the example.
        """
        fee_percentage = 0.01  # 1% fee
        return amount * fee_percentage

    def track_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """Return simple tracking information for a transaction id."""
        tracking_info = {
            "transaction_id": transaction_id,
            "status": "in_transit",
            "confirmations": 3,
        }
        return tracking_info

    def refund(self, transaction_id: str, amount: float) -> Dict[str, Any]:
        """Issue a refund for a transaction (dummy implementation)."""
        refund_info = {
            "transaction_id": transaction_id,
            "refunded_amount": amount,
            "status": "refunded",
        }
        return refund_info

    def convert_currency(
        self, amount: float, from_currency: str, to_currency: str
    ) -> float:
        """Convert between currencies using a placeholder rate."""
        conversion_rate = 0.000025  # Example rate
        return amount * conversion_rate

    def generate_invoice(self, amount: float, due_date: str) -> Dict[str, Any]:
        """Create a simple invoice-like dict for the requested amount."""
        invoice = {
            "invoice_id": str(uuid4()),
            "amount": amount,
            "due_date": due_date,
            "status": "unpaid",
        }
        return invoice

    def schedule_payment(
        self, amount: float, method: str, schedule_date: str
    ) -> Dict[str, Any]:
        """Schedule a payment for a future date (example only)."""
        scheduled_payment = {
            "payment_id": str(uuid4()),
            "amount": amount,
            "method": method,
            "schedule_date": schedule_date,
            "status": "scheduled",
        }
        return scheduled_payment

    def apply_discount(self, amount: float, discount_code: str) -> float:
        """Apply a discount to an amount using a placeholder rule."""
        discount_amount = 5.0  # Flat $5 discount for example
        return max(0.0, amount - discount_amount)

    def calculate_tax(self, amount: float, tax_rate: float) -> float:
        """Calculate tax for the given amount and tax rate (percent)."""
        return amount * tax_rate / 100

    def verify_identity(self, user_id: str, verification_data: Dict[str, Any]) -> bool:
        """Placeholder identity verification; always returns True here."""
        return True

    def link_bank_account(self, account_details: Dict[str, Any]) -> bool:
        """Pretend to link a bank account and return success."""
        return True

    def unlink_bank_account(self, account_id: str) -> bool:
        """Pretend to unlink a bank account and return success."""
        return True

    def get_linked_bank_accounts(self) -> List[Dict[str, Any]]:
        """Return a placeholder list of linked bank accounts."""
        return [{"account_id": "acc1", "bank_name": "Bank A"}]
