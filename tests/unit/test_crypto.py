import os
import sys
import unittest
from typing import Any, Dict

from src.core.exceptions import PaymentError, ValidationError
from src.payment.methods.crypto import CryptoPayment

# ensure project src is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class TestCryptoPayment(unittest.TestCase):
    def setUp(self):
        # Use a small concrete subclass for tests because the real
        # CryptoPayment is abstract (generate_receipt may be required
        # by the base class in some versions). We implement a tiny
        # concrete method here so tests can instantiate safely.
        class _T(CryptoPayment):
            def generate_receipt(self) -> Dict[str, Any]:
                return {
                    "transaction_id": getattr(self, "_transaction_id", None),
                    "status": getattr(self, "status", None),
                }

        self.cp = _T()

    def test_validate_missing_raises(self):
        # Current implementation raises ValidationError when wallet/network
        # are not configured.
        with self.assertRaises(ValidationError):
            self.cp.validate()

    def test_validate_success_ethereum(self):
        # valid 0x + 40 hex chars
        self.cp.wallet_address = "0x" + "1" * 40
        self.cp.network = "ethereum"
        self.assertTrue(self.cp.validate())

    def test_balance_setter_negative_raises(self):
        with self.assertRaises(ValidationError):
            self.cp.balance = -1.0

    def test_execute_invalid_amounts(self):
        # set valid wallet and network
        self.cp.wallet_address = "0x" + "a" * 40
        self.cp.network = "ethereum"
        self.cp.balance = 100.0
        # zero and negative amounts should raise PaymentError
        with self.assertRaises(PaymentError):
            self.cp.execute(0)
        with self.assertRaises(PaymentError):
            self.cp.execute(-10)

    def test_execute_insufficient_balance(self):
        self.cp.wallet_address = "0x" + "b" * 40
        self.cp.network = "ethereum"
        self.cp.balance = 50.0
        with self.assertRaises(PaymentError):
            self.cp.execute(100.0)

    def test_execute_success_and_balance_update(self):
        self.cp.wallet_address = "0x" + "c" * 40
        self.cp.network = "ethereum"
        self.cp.balance = 500.0
        amount = 100.0
        fee = self.cp.estimate_fees(amount)
        # balance decreased by amount + fee per implementation
        self.assertAlmostEqual(self.cp.balance, 500.0 - (amount + fee))

    def test_helpers(self):
        cp = self.cp
        cp.wallet_address = "0x" + "d" * 40
        cp.network = "ethereum"
        cp.balance = 1000.0
        fee = cp.estimate_fees(200.0)
        self.assertIsInstance(fee, float)
        txn = cp.execute(200.0)
        track = cp.track_transaction(str(txn.get("TransactionID")))
        refund = cp.refund(str(txn.get("TransactionID")), 50.0)
        self.assertEqual(track.get("transaction_id"), txn.get("TransactionID"))
        self.assertEqual(refund.get("status"), "refunded")
        inv = cp.generate_invoice(10.0, "2025-12-31")
        self.assertIn("invoice_id", inv)


if __name__ == "__main__":
    unittest.main()


class TestCryptoValidation(unittest.TestCase):
    def test_address_validation(self):
        """Test address validation for different formats."""

        # instantiate the same small concrete subclass used above
        class _T(CryptoPayment):
            def generate_receipt(self) -> Dict[str, Any]:
                return {
                    "transaction_id": getattr(self, "_transaction_id", None),
                    "status": getattr(self, "status", None),
                }

        cp = _T()

        # Valid Ethereum address should work
        cp.wallet_address = "0x1234567890123456789012345678901234567890"
        cp.network = "ethereum"
        self.assertTrue(cp.validate())

        # Invalid Ethereum address should fail validation
        cp.wallet_address = "0x123"
        cp.network = "ethereum"
        with self.assertRaises(ValidationError):
            cp.validate()

        # Bitcoin testnet address
        cp.wallet_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        cp.network = "bitcoin"
        self.assertTrue(cp.validate())

        # Unknown networks should raise (implementation does not accept unknown)
        cp.wallet_address = "some-valid-looking-address-12345"
        cp.network = "unknown-network"
        with self.assertRaises(ValidationError):
            cp.validate()
