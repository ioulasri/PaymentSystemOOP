"""Unit tests for the CryptoPayment class."""

import pytest

from src.core.exceptions import PaymentError, ValidationError
from src.payment.methods.crypto import CryptoPayment


class TestCryptoPaymentInitialization:
    """Test CryptoPayment initialization."""

    def test_initialization(self):
        """Test proper initialization of CryptoPayment."""
        crypto = CryptoPayment()
        assert crypto._wallet_address is None
        assert crypto._network is None
        assert crypto._balance == 0.0


class TestCryptoPaymentBalanceProperty:
    """Test CryptoPayment balance property."""

    def test_balance_getter_default(self):
        """Test balance property getter returns default value."""
        crypto = CryptoPayment()
        assert crypto.balance == 0.0

    def test_balance_setter_positive(self):
        """Test balance property setter with positive value."""
        crypto = CryptoPayment()
        crypto.balance = 100.0
        assert crypto.balance == 100.0

    def test_balance_setter_zero(self):
        """Test balance property setter with zero value."""
        crypto = CryptoPayment()
        crypto.balance = 0.0
        assert crypto.balance == 0.0

    def test_balance_setter_negative_raises_error(self):
        """Test that negative balance raises ValidationError."""
        crypto = CryptoPayment()
        with pytest.raises(ValidationError, match="Balance cannot be negative"):
            crypto.balance = -10.0

    def test_balance_setter_large_value(self):
        """Test balance setter with large value."""
        crypto = CryptoPayment()
        crypto.balance = 1_000_000.0
        assert crypto.balance == 1_000_000.0


class TestCryptoPaymentWalletAddressProperty:
    """Test CryptoPayment wallet_address property."""

    def test_wallet_address_getter_default(self):
        """Test wallet_address property getter returns None."""
        crypto = CryptoPayment()
        assert crypto.wallet_address is None

    def test_wallet_address_setter(self):
        """Test wallet_address property setter."""
        crypto = CryptoPayment()
        crypto.wallet_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        assert crypto.wallet_address == "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"

    def test_wallet_address_setter_overwrite(self):
        """Test wallet_address can be updated."""
        crypto = CryptoPayment()
        crypto.wallet_address = "address1"
        crypto.wallet_address = "address2"
        assert crypto.wallet_address == "address2"


class TestCryptoPaymentNetworkProperty:
    """Test CryptoPayment network property."""

    def test_network_getter_default(self):
        """Test network property getter returns None."""
        crypto = CryptoPayment()
        assert crypto.network is None

    def test_network_setter_bitcoin(self):
        """Test network property setter with bitcoin."""
        crypto = CryptoPayment()
        crypto.network = "bitcoin"
        assert crypto.network == "bitcoin"

    def test_network_setter_ethereum(self):
        """Test network property setter with ethereum."""
        crypto = CryptoPayment()
        crypto.network = "ethereum"
        assert crypto.network == "ethereum"

    def test_network_setter_overwrite(self):
        """Test network can be updated."""
        crypto = CryptoPayment()
        crypto.network = "bitcoin"
        crypto.network = "ethereum"
        assert crypto.network == "ethereum"


class TestCryptoPaymentValidation:
    """Test CryptoPayment validation."""

    def test_validate_missing_wallet_address(self):
        """Test validation raises error when wallet address is missing."""
        crypto = CryptoPayment()
        crypto.network = "bitcoin"
        with pytest.raises(ValidationError, match="Wallet address is required"):
            crypto.validate()

    def test_validate_missing_network(self):
        """Test validation raises error when network is missing."""
        crypto = CryptoPayment()
        crypto.wallet_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        with pytest.raises(ValidationError, match="Network is required"):
            crypto.validate()

    def test_validate_both_missing(self):
        """Test validation raises error when both wallet and network are missing."""
        crypto = CryptoPayment()
        with pytest.raises(ValidationError):
            crypto.validate()

    def test_validate_invalid_bitcoin_address(self):
        """Test validation with invalid Bitcoin address."""
        crypto = CryptoPayment()
        crypto.wallet_address = "invalid_address"
        crypto.network = "bitcoin"
        with pytest.raises(ValidationError, match="Invalid wallet address format"):
            crypto.validate()

    def test_validate_invalid_ethereum_address(self):
        """Test validation with invalid Ethereum address."""
        crypto = CryptoPayment()
        crypto.wallet_address = "invalid_ethereum"
        crypto.network = "ethereum"
        with pytest.raises(ValidationError, match="Invalid wallet address format"):
            crypto.validate()

    def test_validate_valid_bitcoin_legacy(self):
        """Test validation with valid Bitcoin legacy address."""
        crypto = CryptoPayment()
        crypto.wallet_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        crypto.network = "bitcoin"
        assert crypto.validate() is True

    def test_validate_valid_bitcoin_segwit(self):
        """Test validation with valid Bitcoin segwit address."""
        crypto = CryptoPayment()
        crypto.wallet_address = "3J98t1WpEZ73CNmYviecrnyiWrnqRhWNLy"
        crypto.network = "bitcoin"
        assert crypto.validate() is True

    def test_validate_valid_bitcoin_bech32(self):
        """Test validation with valid Bitcoin bech32 address."""
        crypto = CryptoPayment()
        crypto.wallet_address = "bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq"
        crypto.network = "bitcoin"
        assert crypto.validate() is True

    def test_validate_valid_ethereum(self):
        """Test validation with valid Ethereum address."""
        crypto = CryptoPayment()
        crypto.wallet_address = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7"
        crypto.network = "ethereum"
        assert crypto.validate() is True

    def test_validate_unsupported_network(self):
        """Test validation with unsupported network."""
        crypto = CryptoPayment()
        crypto.wallet_address = "some_address"
        crypto.network = "unsupported_network"
        with pytest.raises(ValidationError, match="Unsupported network"):
            crypto.validate()

    def test_validate_btc_alias(self):
        """Test validation with BTC alias."""
        crypto = CryptoPayment()
        crypto.wallet_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        crypto.network = "BTC"
        assert crypto.validate() is True

    def test_validate_eth_alias(self):
        """Test validation with ETH alias."""
        crypto = CryptoPayment()
        crypto.wallet_address = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7"
        crypto.network = "ETH"
        assert crypto.validate() is True


class TestCryptoPaymentExecution:
    """Test CryptoPayment execute method."""

    def test_execute_success(self):
        """Test successful payment execution."""
        crypto = CryptoPayment()
        crypto.wallet_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        crypto.network = "bitcoin"
        crypto.balance = 100.0

        result = crypto.execute(50.0)

        assert result["TransactionType"] == "Crypto"
        assert result["Amount"] == 50.0
        assert result["Fee"] == 0.5  # 1% of 50
        assert result["Transaction status"] == "completed"
        assert "TransactionID" in result
        assert "Timestamp" in result

    def test_execute_updates_balance(self):
        """Test that execute deducts amount and fee from balance."""
        crypto = CryptoPayment()
        crypto.wallet_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        crypto.network = "bitcoin"
        crypto.balance = 100.0

        crypto.execute(50.0)

        # Balance should be 100 - 50 - 0.5 = 49.5
        assert crypto.balance == 49.5

    def test_execute_negative_amount_raises_error(self):
        """Test that negative amount raises PaymentError."""
        crypto = CryptoPayment()
        crypto.wallet_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        crypto.network = "bitcoin"
        crypto.balance = 100.0

        with pytest.raises(PaymentError, match="Amount must be positive"):
            crypto.execute(-10.0)

    def test_execute_zero_amount_raises_error(self):
        """Test that zero amount raises PaymentError."""
        crypto = CryptoPayment()
        crypto.wallet_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        crypto.network = "bitcoin"
        crypto.balance = 100.0

        with pytest.raises(PaymentError, match="Amount must be positive"):
            crypto.execute(0.0)

    def test_execute_insufficient_balance_raises_error(self):
        """Test that insufficient balance raises PaymentError."""
        crypto = CryptoPayment()
        crypto.wallet_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        crypto.network = "bitcoin"
        crypto.balance = 10.0

        with pytest.raises(PaymentError, match="Insufficient balance"):
            crypto.execute(50.0)

    def test_execute_without_validation_raises_error(self):
        """Test that execute without valid config raises ValidationError."""
        crypto = CryptoPayment()
        crypto.balance = 100.0

        with pytest.raises(ValidationError):
            crypto.execute(50.0)

    def test_execute_sets_status_completed(self):
        """Test that execute sets status to completed."""
        crypto = CryptoPayment()
        crypto.wallet_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        crypto.network = "bitcoin"
        crypto.balance = 100.0

        crypto.execute(50.0)

        assert crypto.status == "completed"

    def test_execute_sets_transaction_id(self):
        """Test that execute sets a transaction ID."""
        crypto = CryptoPayment()
        crypto.wallet_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        crypto.network = "bitcoin"
        crypto.balance = 100.0

        result = crypto.execute(50.0)

        assert crypto._transaction_id is not None
        assert result["TransactionID"] == crypto._transaction_id

    def test_execute_sets_timestamp(self):
        """Test that execute sets a timestamp."""
        crypto = CryptoPayment()
        crypto.wallet_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        crypto.network = "bitcoin"
        crypto.balance = 100.0

        result = crypto.execute(50.0)

        assert crypto._timestamp is not None
        assert result["Timestamp"] == crypto._timestamp


class TestCryptoPaymentEstimateFees:
    """Test CryptoPayment estimate_fees method."""

    def test_estimate_fees_returns_one_percent(self):
        """Test that estimate_fees returns 1% of amount."""
        crypto = CryptoPayment()
        fee = crypto.estimate_fees(100.0)
        assert fee == 1.0

    def test_estimate_fees_small_amount(self):
        """Test estimate_fees with small amount."""
        crypto = CryptoPayment()
        fee = crypto.estimate_fees(10.0)
        assert fee == 0.1

    def test_estimate_fees_large_amount(self):
        """Test estimate_fees with large amount."""
        crypto = CryptoPayment()
        fee = crypto.estimate_fees(10000.0)
        assert fee == 100.0

    def test_estimate_fees_zero(self):
        """Test estimate_fees with zero amount."""
        crypto = CryptoPayment()
        fee = crypto.estimate_fees(0.0)
        assert fee == 0.0


class TestCryptoPaymentGenerateReceipt:
    """Test CryptoPayment generate_receipt method."""

    def test_generate_receipt_success(self):
        """Test successful receipt generation."""
        crypto = CryptoPayment()
        crypto.wallet_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        crypto.network = "bitcoin"
        crypto.balance = 100.0

        # Execute to set transaction data
        crypto.execute(50.0)

        receipt = crypto.generate_receipt(50.0)

        assert receipt["PaymentMethod"] == "Crypto"
        assert receipt["Amount"] == 50.0
        assert receipt["WalletAddress"] == "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        assert receipt["Transaction status"] == "completed"
        assert "TransactionID" in receipt
        assert "Timestamp" in receipt

    def test_generate_receipt_contains_all_fields(self):
        """Test that receipt contains all required fields."""
        crypto = CryptoPayment()
        crypto.wallet_address = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7"
        crypto.network = "ethereum"
        crypto.balance = 200.0

        crypto.execute(75.0)
        receipt = crypto.generate_receipt(75.0)

        required_fields = [
            "TransactionID",
            "PaymentMethod",
            "WalletAddress",
            "Amount",
            "Timestamp",
            "Transaction status",
        ]
        for field in required_fields:
            assert field in receipt


class TestCryptoPaymentTrackTransaction:
    """Test CryptoPayment track_transaction method."""

    def test_track_transaction_returns_info(self):
        """Test that track_transaction returns tracking info."""
        crypto = CryptoPayment()
        tracking = crypto.track_transaction("tx123")

        assert tracking["transaction_id"] == "tx123"
        assert tracking["status"] == "in_transit"
        assert tracking["confirmations"] == 3

    def test_track_transaction_different_ids(self):
        """Test track_transaction with different IDs."""
        crypto = CryptoPayment()
        tracking1 = crypto.track_transaction("tx_abc")
        tracking2 = crypto.track_transaction("tx_xyz")

        assert tracking1["transaction_id"] == "tx_abc"
        assert tracking2["transaction_id"] == "tx_xyz"


class TestCryptoPaymentRefund:
    """Test CryptoPayment refund method."""

    def test_refund_returns_info(self):
        """Test that refund returns refund info."""
        crypto = CryptoPayment()
        refund = crypto.refund("tx123", 50.0)

        assert refund["transaction_id"] == "tx123"
        assert refund["refunded_amount"] == 50.0
        assert refund["status"] == "refunded"

    def test_refund_different_amounts(self):
        """Test refund with different amounts."""
        crypto = CryptoPayment()
        refund1 = crypto.refund("tx1", 25.0)
        refund2 = crypto.refund("tx2", 100.0)

        assert refund1["refunded_amount"] == 25.0
        assert refund2["refunded_amount"] == 100.0


class TestCryptoPaymentConvertCurrency:
    """Test CryptoPayment convert_currency method."""

    def test_convert_currency_returns_converted_amount(self):
        """Test that convert_currency returns converted amount."""
        crypto = CryptoPayment()
        converted = crypto.convert_currency(100.0, "USD", "BTC")
        assert converted == 0.0025  # 100 * 0.000025

    def test_convert_currency_different_amounts(self):
        """Test convert_currency with different amounts."""
        crypto = CryptoPayment()
        converted1 = crypto.convert_currency(1000.0, "USD", "BTC")
        converted2 = crypto.convert_currency(500.0, "USD", "ETH")

        assert converted1 == 0.025
        assert converted2 == 0.0125


class TestCryptoPaymentSchedulePayment:
    """Test CryptoPayment schedule_payment method."""

    def test_schedule_payment_returns_info(self):
        """Test that schedule_payment returns scheduled info."""
        crypto = CryptoPayment()
        scheduled = crypto.schedule_payment(100.0, "crypto", "2024-12-31")

        assert scheduled["amount"] == 100.0
        assert scheduled["method"] == "crypto"
        assert scheduled["schedule_date"] == "2024-12-31"
        assert scheduled["status"] == "scheduled"
        assert "payment_id" in scheduled

    def test_schedule_payment_unique_ids(self):
        """Test that schedule_payment generates unique IDs."""
        crypto = CryptoPayment()
        scheduled1 = crypto.schedule_payment(50.0, "crypto", "2024-12-31")
        scheduled2 = crypto.schedule_payment(75.0, "crypto", "2025-01-15")

        assert scheduled1["payment_id"] != scheduled2["payment_id"]


class TestCryptoPaymentApplyDiscount:
    """Test CryptoPayment apply_discount method."""

    def test_apply_discount_reduces_amount(self):
        """Test that apply_discount reduces amount by $5."""
        crypto = CryptoPayment()
        discounted = crypto.apply_discount(100.0, "CODE123")
        assert discounted == 95.0

    def test_apply_discount_minimum_zero(self):
        """Test that discount cannot result in negative amount."""
        crypto = CryptoPayment()
        discounted = crypto.apply_discount(3.0, "CODE123")
        assert discounted == 0.0

    def test_apply_discount_exact_discount(self):
        """Test discount with exact amount."""
        crypto = CryptoPayment()
        discounted = crypto.apply_discount(5.0, "CODE123")
        assert discounted == 0.0


class TestCryptoPaymentCalculateTax:
    """Test CryptoPayment calculate_tax method."""

    def test_calculate_tax_returns_tax_amount(self):
        """Test that calculate_tax returns correct tax."""
        crypto = CryptoPayment()
        tax = crypto.calculate_tax(100.0, 10.0)  # 10% tax
        assert tax == 10.0

    def test_calculate_tax_different_rates(self):
        """Test calculate_tax with different rates."""
        crypto = CryptoPayment()
        tax1 = crypto.calculate_tax(100.0, 5.0)  # 5%
        tax2 = crypto.calculate_tax(200.0, 8.5)  # 8.5%

        assert tax1 == 5.0
        assert tax2 == 17.0

    def test_calculate_tax_zero_rate(self):
        """Test calculate_tax with zero rate."""
        crypto = CryptoPayment()
        tax = crypto.calculate_tax(100.0, 0.0)
        assert tax == 0.0


class TestCryptoPaymentVerifyIdentity:
    """Test CryptoPayment verify_identity method."""

    def test_verify_identity_returns_true(self):
        """Test that verify_identity returns True."""
        crypto = CryptoPayment()
        result = crypto.verify_identity("user123", {"name": "John Doe"})
        assert result is True

    def test_verify_identity_different_users(self):
        """Test verify_identity with different user IDs."""
        crypto = CryptoPayment()
        result1 = crypto.verify_identity("user1", {"data": "value1"})
        result2 = crypto.verify_identity("user2", {"data": "value2"})

        assert result1 is True
        assert result2 is True


class TestCryptoPaymentBankAccountManagement:
    """Test CryptoPayment bank account management methods."""

    def test_link_bank_account_returns_true(self):
        """Test that link_bank_account returns True."""
        crypto = CryptoPayment()
        result = crypto.link_bank_account({"account": "123456789"})
        assert result is True

    def test_unlink_bank_account_returns_true(self):
        """Test that unlink_bank_account returns True."""
        crypto = CryptoPayment()
        result = crypto.unlink_bank_account("acc123")
        assert result is True

    def test_get_linked_bank_accounts_returns_list(self):
        """Test that get_linked_bank_accounts returns accounts list."""
        crypto = CryptoPayment()
        accounts = crypto.get_linked_bank_accounts()

        assert isinstance(accounts, list)
        assert len(accounts) > 0
        assert accounts[0]["account_id"] == "acc1"
        assert accounts[0]["bank_name"] == "Bank A"


class TestCryptoPaymentIntegration:
    """Integration tests for CryptoPayment workflows."""

    def test_full_payment_workflow(self):
        """Test complete payment workflow from setup to receipt."""
        crypto = CryptoPayment()

        # Setup
        crypto.wallet_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        crypto.network = "bitcoin"
        crypto.balance = 1000.0

        # Validate
        assert crypto.validate() is True

        # Execute
        transaction = crypto.execute(100.0)
        assert transaction["Amount"] == 100.0
        assert transaction["Transaction status"] == "completed"

        # Generate receipt
        receipt = crypto.generate_receipt(100.0)
        assert receipt["Amount"] == 100.0
        assert receipt["PaymentMethod"] == "Crypto"

        # Check balance
        assert crypto.balance == 899.0  # 1000 - 100 - 1

    def test_ethereum_payment_workflow(self):
        """Test payment workflow with Ethereum."""
        crypto = CryptoPayment()

        crypto.wallet_address = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7"
        crypto.network = "ethereum"
        crypto.balance = 500.0

        assert crypto.validate() is True

        transaction = crypto.execute(50.0)
        assert transaction["TransactionType"] == "Crypto"

        receipt = crypto.generate_receipt(50.0)
        assert receipt["WalletAddress"] == "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7"

        assert crypto.balance == 449.5  # 500 - 50 - 0.5
