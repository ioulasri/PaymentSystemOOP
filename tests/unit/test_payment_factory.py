import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path for absolute imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.core.exceptions import ValidationError
from src.services.payment_factory import PaymentFactory
from src.payment.methods.credit_card import CreditCardPayment
from src.payment.methods.paypal import Paypal
from src.payment.methods.crypto import CryptoPayment


class TestPaymentFactory(unittest.TestCase):
    """Test suite for PaymentFactory class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Valid test data for credit card
        self.valid_credit_card_params = {
            "cardholder": "Mr John Doe",
            "cardnumber": "4532123456789012",
            "expirationdate": "12-25",
            "cvv": "123",
            "balance": 1000.0
        }
        
        # Valid test data for PayPal
        self.valid_paypal_params = {
            "emailaddress": "user@example.com",
            "passwordtoken": "SecurePass123",
            "verified": True,
            "balance": 500.0
        }
        
        # Valid test data for Crypto
        self.valid_crypto_params = {
            "wallet_address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
            "network": "BTC"
        }

    def tearDown(self):
        """Clean up after each test method."""
        pass


class TestSupportedTypes(TestPaymentFactory):
    """Test cases for SUPPORTED_TYPES dictionary."""

    def test_supported_types_contains_credit_card(self):
        """Test that SUPPORTED_TYPES includes credit_card."""
        self.assertIn("credit_card", PaymentFactory.SUPPORTED_TYPES)
        self.assertEqual(PaymentFactory.SUPPORTED_TYPES["credit_card"], CreditCardPayment)

    def test_supported_types_contains_paypal(self):
        """Test that SUPPORTED_TYPES includes paypal."""
        self.assertIn("paypal", PaymentFactory.SUPPORTED_TYPES)
        self.assertEqual(PaymentFactory.SUPPORTED_TYPES["paypal"], Paypal)

    def test_supported_types_contains_crypto(self):
        """Test that SUPPORTED_TYPES includes crypto."""
        self.assertIn("crypto", PaymentFactory.SUPPORTED_TYPES)
        self.assertEqual(PaymentFactory.SUPPORTED_TYPES["crypto"], CryptoPayment)

    def test_supported_types_count(self):
        """Test that SUPPORTED_TYPES has exactly 3 payment types."""
        self.assertEqual(len(PaymentFactory.SUPPORTED_TYPES), 3)


class TestCreateCreditCard(TestPaymentFactory):
    """Test cases for creating CreditCardPayment instances."""

    def test_create_credit_card_with_valid_params(self):
        """Test creating a credit card payment with valid parameters."""
        payment = PaymentFactory.create("credit_card", **self.valid_credit_card_params)
        
        self.assertIsInstance(payment, CreditCardPayment)
        self.assertEqual(payment.cardholder, "Mr John Doe")
        self.assertEqual(payment.cardnumber, "4532123456789012")
        self.assertEqual(payment.expirationdate, "12-25")
        self.assertEqual(payment.cvv, "123")
        self.assertEqual(payment.balance, 1000.0)

    def test_create_credit_card_with_partial_params(self):
        """Test creating a credit card payment with partial parameters."""
        partial_params = {
            "cardholder": "Jane Doe",
            "cardnumber": "4532123456789012",
            "balance": 500.0
        }
        
        # Should fail validation because required fields are missing
        with self.assertRaises(ValidationError):
            PaymentFactory.create("credit_card", **partial_params)

    def test_create_credit_card_with_invalid_card_number(self):
        """Test creating a credit card payment with invalid card number."""
        invalid_params = self.valid_credit_card_params.copy()
        invalid_params["cardnumber"] = "123"  # Too short
        
        with self.assertRaises(ValidationError):
            PaymentFactory.create("credit_card", **invalid_params)

    def test_create_credit_card_with_invalid_cvv(self):
        """Test creating a credit card payment with invalid CVV."""
        invalid_params = self.valid_credit_card_params.copy()
        invalid_params["cvv"] = "12"  # Too short
        
        with self.assertRaises(ValidationError):
            PaymentFactory.create("credit_card", **invalid_params)

    def test_create_credit_card_with_invalid_expiration_date(self):
        """Test creating a credit card payment with invalid expiration date."""
        invalid_params = self.valid_credit_card_params.copy()
        invalid_params["expirationdate"] = "13-25"  # Invalid month
        
        with self.assertRaises(ValidationError):
            PaymentFactory.create("credit_card", **invalid_params)

    def test_create_credit_card_with_negative_balance(self):
        """Test creating a credit card payment with negative balance."""
        invalid_params = self.valid_credit_card_params.copy()
        invalid_params["balance"] = -100.0
        
        with self.assertRaises(ValidationError):
            PaymentFactory.create("credit_card", **invalid_params)

    def test_create_credit_card_without_balance(self):
        """Test creating a credit card payment without balance parameter."""
        params_without_balance = self.valid_credit_card_params.copy()
        del params_without_balance["balance"]
        
        payment = PaymentFactory.create("credit_card", **params_without_balance)
        
        self.assertIsInstance(payment, CreditCardPayment)
        self.assertEqual(payment.balance, 0.0)  # Default balance


class TestCreatePayPal(TestPaymentFactory):
    """Test cases for creating Paypal instances."""

    def test_create_paypal_with_valid_params(self):
        """Test creating a PayPal payment with valid parameters."""
        payment = PaymentFactory.create("paypal", **self.valid_paypal_params)
        
        self.assertIsInstance(payment, Paypal)
        self.assertEqual(payment.emailaddress, "user@example.com")
        self.assertEqual(payment.passwordtoken, "SecurePass123")
        self.assertEqual(payment.verified, True)
        self.assertEqual(payment.balance, 500.0)

    def test_create_paypal_with_invalid_email(self):
        """Test creating a PayPal payment with invalid email."""
        invalid_params = self.valid_paypal_params.copy()
        invalid_params["emailaddress"] = "invalid-email"
        
        with self.assertRaises(ValidationError):
            PaymentFactory.create("paypal", **invalid_params)

    def test_create_paypal_with_weak_password(self):
        """Test creating a PayPal payment with weak password."""
        invalid_params = self.valid_paypal_params.copy()
        invalid_params["passwordtoken"] = "weak"
        
        with self.assertRaises(ValidationError):
            PaymentFactory.create("paypal", **invalid_params)

    def test_create_paypal_with_partial_params(self):
        """Test creating a PayPal payment with partial parameters."""
        partial_params = {
            "emailaddress": "user@example.com",
            "balance": 100.0
        }
        
        # Should fail validation because required fields are missing
        with self.assertRaises(ValidationError):
            PaymentFactory.create("paypal", **partial_params)

    def test_create_paypal_without_balance(self):
        """Test creating a PayPal payment without balance parameter."""
        params_without_balance = self.valid_paypal_params.copy()
        del params_without_balance["balance"]
        
        payment = PaymentFactory.create("paypal", **params_without_balance)
        
        self.assertIsInstance(payment, Paypal)
        self.assertEqual(payment.balance, 0.0)  # Default balance

    def test_create_paypal_unverified_account(self):
        """Test creating an unverified PayPal payment."""
        params = self.valid_paypal_params.copy()
        params["verified"] = False
        
        payment = PaymentFactory.create("paypal", **params)
        
        self.assertIsInstance(payment, Paypal)
        self.assertEqual(payment.verified, False)


class TestCreateCrypto(TestPaymentFactory):
    """Test cases for creating CryptoPayment instances."""

    def test_create_crypto_with_valid_params(self):
        """Test creating a crypto payment with valid parameters."""
        payment = PaymentFactory.create("crypto", **self.valid_crypto_params)
        
        self.assertIsInstance(payment, CryptoPayment)

    def test_create_crypto_with_missing_wallet_address(self):
        """Test creating a crypto payment with missing wallet address."""
        invalid_params = {
            "network": "BTC"
        }
        
        with self.assertRaises(ValidationError):
            PaymentFactory.create("crypto", **invalid_params)

    def test_create_crypto_with_missing_network(self):
        """Test creating a crypto payment with missing network."""
        invalid_params = {
            "wallet_address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        }
        
        with self.assertRaises(ValidationError):
            PaymentFactory.create("crypto", **invalid_params)

    def test_create_crypto_with_invalid_wallet_address(self):
        """Test creating a crypto payment with invalid wallet address."""
        invalid_params = self.valid_crypto_params.copy()
        invalid_params["wallet_address"] = "invalid"
        
        with self.assertRaises(ValidationError):
            PaymentFactory.create("crypto", **invalid_params)

    def test_create_crypto_with_minimal_params(self):
        """Test creating a crypto payment with minimal required parameters."""
        payment = PaymentFactory.create("crypto", **self.valid_crypto_params)
        
        self.assertIsInstance(payment, CryptoPayment)

    def test_create_crypto_with_different_networks(self):
        """Test creating crypto payments with different blockchain networks."""
        # Use valid addresses for each network
        test_cases = [
            ("BTC", "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"),
            ("ETH", "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0"),
            ("LTC", "LM2WMpR1Rp6j3Sa59roXGgQu5jSvFo1o1c"),
        ]
        
        for network, wallet_address in test_cases:
            params = self.valid_crypto_params.copy()
            params["network"] = network
            params["wallet_address"] = wallet_address
            
            payment = PaymentFactory.create("crypto", **params)
            self.assertIsInstance(payment, CryptoPayment)


class TestUnsupportedPaymentType(TestPaymentFactory):
    """Test cases for unsupported payment types."""

    def test_create_with_invalid_payment_type(self):
        """Test creating a payment with invalid payment type."""
        with self.assertRaises(ValidationError) as context:
            PaymentFactory.create("invalid_type", balance=100.0)
        
        self.assertIn("Unsupported payment type", str(context.exception))

    def test_create_with_empty_payment_type(self):
        """Test creating a payment with empty payment type."""
        with self.assertRaises(ValidationError) as context:
            PaymentFactory.create("", balance=100.0)
        
        self.assertIn("Unsupported payment type", str(context.exception))

    def test_create_with_none_payment_type(self):
        """Test creating a payment with None as payment type."""
        with self.assertRaises(ValidationError):
            PaymentFactory.create(None, balance=100.0)

    def test_create_with_wrong_case_payment_type(self):
        """Test creating a payment with wrong case payment type."""
        with self.assertRaises(ValidationError):
            PaymentFactory.create("Credit_Card", **self.valid_credit_card_params)


class TestConfigurationMethods(TestPaymentFactory):
    """Test cases for internal configuration methods."""

    def test_configure_credit_card_method(self):
        """Test _configure_creditcard method sets all attributes."""
        payment = CreditCardPayment()
        PaymentFactory._configure_creditcard(payment, self.valid_credit_card_params)
        
        self.assertEqual(payment.cardholder, "Mr John Doe")
        self.assertEqual(payment.cardnumber, "4532123456789012")
        self.assertEqual(payment.expirationdate, "12-25")
        self.assertEqual(payment.cvv, "123")
        self.assertEqual(payment.balance, 1000.0)

    def test_configure_credit_card_with_empty_params(self):
        """Test _configure_creditcard method with empty parameters."""
        payment = CreditCardPayment()
        PaymentFactory._configure_creditcard(payment, {})
        
        # Should not raise an error, just not set any attributes
        self.assertEqual(payment.cardholder, "")

    def test_configure_paypal_method(self):
        """Test _configure_paypal method sets all attributes."""
        payment = Paypal()
        PaymentFactory._configure_paypal(payment, self.valid_paypal_params)
        
        self.assertEqual(payment.emailaddress, "user@example.com")
        self.assertEqual(payment.passwordtoken, "SecurePass123")
        self.assertEqual(payment.verified, True)
        self.assertEqual(payment.balance, 500.0)

    def test_configure_paypal_with_empty_params(self):
        """Test _configure_paypal method with empty parameters."""
        payment = Paypal()
        PaymentFactory._configure_paypal(payment, {})
        
        # Should not raise an error, just not set any attributes
        self.assertEqual(payment.emailaddress, "")

    def test_configure_crypto_method(self):
        """Test _configure_crypto method sets wallet configuration."""
        payment = CryptoPayment()
        PaymentFactory._configure_crypto(payment, self.valid_crypto_params)
        
        # Wallet should be configured
        self.assertTrue(payment.validate())

    def test_configure_crypto_with_empty_params(self):
        """Test _configure_crypto method with empty parameters."""
        payment = CryptoPayment()
        PaymentFactory._configure_crypto(payment, {})
        
        # Should not raise an error, wallet should remain unconfigured
        self.assertFalse(payment.validate())


class TestValidationFlow(TestPaymentFactory):
    """Test cases for validation flow in the factory."""

    def test_validation_is_called_during_creation(self):
        """Test that validate() is called during payment creation."""
        with patch.object(CreditCardPayment, 'validate') as mock_validate:
            mock_validate.return_value = True
            PaymentFactory.create("credit_card", **self.valid_credit_card_params)
            mock_validate.assert_called_once()

    def test_validation_error_is_propagated(self):
        """Test that ValidationError from validate() is propagated."""
        with patch.object(CreditCardPayment, 'validate') as mock_validate:
            mock_validate.side_effect = ValidationError("ValidationError", "Invalid card")
            
            with self.assertRaises(ValidationError) as context:
                PaymentFactory.create("credit_card", **self.valid_credit_card_params)
            
            self.assertIn("Invalid card", str(context.exception))

    def test_generic_exception_wrapped_in_validation_error(self):
        """Test that generic exceptions are wrapped in ValidationError."""
        with patch.object(CreditCardPayment, 'validate') as mock_validate:
            mock_validate.side_effect = Exception("Unexpected error")
            
            with self.assertRaises(ValidationError) as context:
                PaymentFactory.create("credit_card", **self.valid_credit_card_params)
            
            self.assertIn("Payment validation failed", str(context.exception))


class TestEdgeCases(TestPaymentFactory):
    """Test cases for edge cases and boundary conditions."""

    def test_create_with_extra_parameters(self):
        """Test creating a payment with extra unknown parameters."""
        params_with_extra = self.valid_credit_card_params.copy()
        params_with_extra["unknown_param"] = "value"
        
        # Should ignore extra parameters and create successfully
        payment = PaymentFactory.create("credit_card", **params_with_extra)
        self.assertIsInstance(payment, CreditCardPayment)

    def test_create_with_none_values(self):
        """Test creating a payment with None values."""
        params_with_none = {
            "cardholder": None,
            "cardnumber": None,
            "expirationdate": None,
            "cvv": None,
            "balance": 100.0
        }
        
        # Should fail validation
        with self.assertRaises((ValidationError, AttributeError, TypeError)):
            PaymentFactory.create("credit_card", **params_with_none)

    def test_create_credit_card_with_zero_balance(self):
        """Test creating a payment with zero balance."""
        params = self.valid_credit_card_params.copy()
        params["balance"] = 0.0
        
        payment = PaymentFactory.create("credit_card", **params)
        self.assertIsInstance(payment, CreditCardPayment)
        self.assertEqual(payment.balance, 0.0)

    def test_create_paypal_with_maximum_balance(self):
        """Test creating a payment with very large balance."""
        params = self.valid_paypal_params.copy()
        params["balance"] = 999999999.99
        
        payment = PaymentFactory.create("paypal", **params)
        self.assertIsInstance(payment, Paypal)
        self.assertEqual(payment.balance, 999999999.99)


class TestFactoryReturnTypes(TestPaymentFactory):
    """Test cases for verifying return types."""

    def test_create_returns_payment_strategy_interface(self):
        """Test that create() returns an object implementing PaymentStrategy."""
        from src.core.base import PaymentStrategy
        
        payment = PaymentFactory.create("credit_card", **self.valid_credit_card_params)
        self.assertIsInstance(payment, PaymentStrategy)

    def test_all_payment_types_return_correct_instances(self):
        """Test that all payment types return their respective instances."""
        credit_card = PaymentFactory.create("credit_card", **self.valid_credit_card_params)
        paypal = PaymentFactory.create("paypal", **self.valid_paypal_params)
        crypto = PaymentFactory.create("crypto", **self.valid_crypto_params)
        
        self.assertIsInstance(credit_card, CreditCardPayment)
        self.assertIsInstance(paypal, Paypal)
        self.assertIsInstance(crypto, CryptoPayment)


if __name__ == "__main__":
    unittest.main()
