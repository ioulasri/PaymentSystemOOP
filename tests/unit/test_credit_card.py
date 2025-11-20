import os
import sys
import unittest
from datetime import date

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import date

from src.core.exceptions import ValidationError
from src.payment.methods.credit_card import CreditCardPayment


class TestCreditCardPayment(unittest.TestCase):
    """Test suite for CreditCardPayment class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.payment = CreditCardPayment()
        # Valid test data
        self.valid_card_number = "1234567890123456"
        self.valid_card_holder = "John Doe"
        self.valid_expiration_date = "12-30"
        self.valid_cvv = "123"

    def tearDown(self):
        """Clean up after each test method."""
        self.payment = None


class TestCardNumberValidation(TestCreditCardPayment):
    """Test cases for card number validation."""

    def test_valid_card_number_16_digits(self):
        """Test that a valid 16-digit card number passes validation."""
        result = self.payment.check_cardnumber("1234567890123456")
        self.assertTrue(result)

    def test_invalid_card_number_too_short(self):
        """Test that a card number shorter than 16 digits fails validation."""
        result = self.payment.check_cardnumber("123456789012345")
        self.assertFalse(result)

    def test_invalid_card_number_too_long(self):
        """Test that a card number longer than 16 digits fails validation."""
        result = self.payment.check_cardnumber("12345678901234567")
        self.assertFalse(result)

    def test_invalid_card_number_with_letters(self):
        """Test that a card number with non-digit characters fails validation."""
        result = self.payment.check_cardnumber("123456789012345A")
        self.assertFalse(result)

    def test_invalid_card_number_with_spaces(self):
        """Test that a card number with spaces fails validation."""
        result = self.payment.check_cardnumber("1234 5678 9012 3456")
        self.assertFalse(result)

    def test_invalid_card_number_empty(self):
        """Test that an empty card number fails validation."""
        result = self.payment.check_cardnumber("")
        self.assertFalse(result)


class TestExpirationDateValidation(TestCreditCardPayment):
    """Test cases for expiration date validation."""

    def test_valid_expiration_date_format(self):
        """Test that a valid MM-YY format passes validation."""
        result = self.payment.check_expirationdate_format("12-25")
        self.assertTrue(result)

    def test_invalid_expiration_date_format_slash(self):
        """Test that MM/YY format fails validation (expects MM-YY)."""
        result = self.payment.check_expirationdate_format("12/25")
        self.assertFalse(result)

    def test_invalid_expiration_date_format_no_separator(self):
        """Test that MMYY format without separator fails validation."""
        result = self.payment.check_expirationdate_format("1225")
        self.assertFalse(result)

    def test_invalid_expiration_date_format_wrong_length(self):
        """Test that wrong length format fails validation."""
        result = self.payment.check_expirationdate_format("1-25")
        self.assertFalse(result)

    def test_invalid_expiration_date_format_letters(self):
        """Test that format with letters fails validation."""
        result = self.payment.check_expirationdate_format("AB-CD")
        self.assertFalse(result)

    def test_valid_future_expiration_date(self):
        """Test that a future expiration date passes validation."""
        result = self.payment.check_expirationdate("12-30")
        self.assertTrue(result)

    def test_invalid_past_expiration_date(self):
        """Test that a past expiration date fails validation."""
        result = self.payment.check_expirationdate("01-20")
        self.assertFalse(result)


class TestCVVValidation(TestCreditCardPayment):
    """Test cases for CVV validation."""

    def test_valid_cvv_three_digits(self):
        """Test that a 3-digit CVV passes validation."""
        result = self.payment.check_cvv("123")
        self.assertTrue(result)

    def test_valid_cvv_four_digits(self):
        """Test that a 4-digit CVV passes validation (AMEX)."""
        result = self.payment.check_cvv("1234")
        self.assertTrue(result)

    def test_invalid_cvv_too_short(self):
        """Test that a CVV shorter than 3 digits fails validation."""
        result = self.payment.check_cvv("12")
        self.assertFalse(result)

    def test_invalid_cvv_too_long(self):
        """Test that a CVV longer than 4 digits fails validation."""
        result = self.payment.check_cvv("12345")
        self.assertFalse(result)

    def test_invalid_cvv_with_letters(self):
        """Test that a CVV with letters fails validation."""
        result = self.payment.check_cvv("12A")
        self.assertFalse(result)

    def test_invalid_cvv_empty(self):
        """Test that an empty CVV fails validation."""
        result = self.payment.check_cvv("")
        self.assertFalse(result)


class TestValidateMethod(TestCreditCardPayment):
    """Test cases for the main validate method."""

    def test_validate_all_valid_data(self):
        """Test that validate returns True when all data is valid."""
        self.payment.cardnumber = self.valid_card_number
        self.payment.cardholder = "Mr John Doe"
        self.payment.expirationdate = self.valid_expiration_date
        self.payment.cvv = self.valid_cvv

        result = self.payment.validate()
        self.assertTrue(result)

    def test_validate_empty_card_holder(self):
        """Test that validate raises ValidationError for empty card holder."""
        self.payment.cardnumber = self.valid_card_number
        self.payment.cardholder = "Mr John Doe"
        self.payment.expirationdate = self.valid_expiration_date
        self.payment.cvv = self.valid_cvv
        # Set cardholder to empty after initial valid setup
        self.payment._card_holder = ""

        with self.assertRaises(ValidationError) as context:
            self.payment.validate()
        self.assertIn("card holder empty", str(context.exception))

    def test_validate_invalid_card_number(self):
        """Test that validate raises ValidationError for invalid card number."""
        self.payment.cardholder = "Mr John Doe"
        self.payment.expirationdate = self.valid_expiration_date
        self.payment.cvv = self.valid_cvv
        # Set invalid card number directly to bypass setter validation
        self.payment._CreditCardPayment__card_number = "123"

        with self.assertRaises(ValidationError) as context:
            self.payment.validate()
        self.assertIn("card number", str(context.exception))

    def test_validate_invalid_expiration_format(self):
        """Test that validate raises ValidationError for invalid expiration format."""
        self.payment.cardnumber = self.valid_card_number
        self.payment.cardholder = "Mr John Doe"
        self.payment.cvv = self.valid_cvv
        # Set invalid expiration date directly to bypass setter validation
        self.payment._CreditCardPayment__expiration_date = "12/30"

        with self.assertRaises(ValidationError) as context:
            self.payment.validate()
        self.assertIn("expiration date format is invalid", str(context.exception))

    def test_validate_expired_card(self):
        """Test that validate raises ValidationError for expired card."""
        self.payment.cardnumber = self.valid_card_number
        self.payment.cardholder = "Mr John Doe"
        self.payment.cvv = self.valid_cvv
        # Set expired date directly to bypass setter validation
        self.payment._CreditCardPayment__expiration_date = "01-20"

        with self.assertRaises(ValidationError) as context:
            self.payment.validate()
        self.assertIn("expiration date is in the past", str(context.exception))

    def test_validate_invalid_cvv(self):
        """Test that validate raises ValidationError for invalid CVV."""
        self.payment.cardnumber = self.valid_card_number
        self.payment.cardholder = "Mr John Doe"
        self.payment.expirationdate = self.valid_expiration_date
        # Set invalid CVV directly to bypass setter validation
        self.payment._CreditCardPayment__cvv = "12"

        with self.assertRaises(ValidationError) as context:
            self.payment.validate()
        self.assertIn("cvv", str(context.exception))


class TestBalanceProperty(TestCreditCardPayment):
    """Test cases for balance property getter and setter."""

    def test_balance_getter_default_value(self):
        """Test that balance getter returns default value of 0.0."""
        self.assertEqual(self.payment.balance, 0.0)

    def test_balance_setter_valid_value(self):
        """Test that balance setter accepts valid positive values."""
        self.payment.balance = 1000.0
        self.assertEqual(self.payment.balance, 1000.0)

    def test_balance_setter_zero_value(self):
        """Test that balance setter accepts zero value."""
        self.payment.balance = 0.0
        self.assertEqual(self.payment.balance, 0.0)

    def test_balance_setter_float_value(self):
        """Test that balance setter accepts float values."""
        self.payment.balance = 250.75
        self.assertEqual(self.payment.balance, 250.75)

    def test_balance_setter_negative_value(self):
        """Test that balance setter raises ValidationError for negative values."""
        with self.assertRaises(ValidationError) as context:
            self.payment.balance = -100.0
        self.assertEqual(context.exception.message, "ValidationError")
        self.assertEqual(context.exception.field, "Balance cannot be negative")


class TestCardholderProperty(TestCreditCardPayment):
    """Test cases for cardholder property getter and setter."""

    def test_cardholder_getter_default_value(self):
        """Test that cardholder getter returns default empty string."""
        self.assertEqual(self.payment.cardholder, "")

    def test_cardholder_setter_valid_mr(self):
        """Test that cardholder setter accepts valid 'Mr' format."""
        self.payment.cardholder = "Mr John Doe"
        self.assertEqual(self.payment.cardholder, "Mr John Doe")

    def test_cardholder_setter_valid_mrs(self):
        """Test that cardholder setter accepts valid 'Mrs' format."""
        self.payment.cardholder = "Mrs Jane Smith"
        self.assertEqual(self.payment.cardholder, "Mrs Jane Smith")

    def test_cardholder_setter_valid_ms(self):
        """Test that cardholder setter accepts valid 'Ms' format."""
        self.payment.cardholder = "Ms Sarah Johnson"
        self.assertEqual(self.payment.cardholder, "Ms Sarah Johnson")

    def test_cardholder_setter_invalid_no_prefix(self):
        """Test that cardholder setter raises ValidationError without prefix."""
        with self.assertRaises(ValidationError) as context:
            self.payment.cardholder = "John Doe"
        self.assertIn("Cardholder should follow format", context.exception.field)

    def test_cardholder_setter_invalid_no_lastname(self):
        """Test that cardholder setter raises ValidationError without lastname."""
        with self.assertRaises(ValidationError) as context:
            self.payment.cardholder = "Mr John"
        self.assertIn("Cardholder should follow format", context.exception.field)

    def test_cardholder_setter_invalid_single_word(self):
        """Test that cardholder setter raises ValidationError with single word."""
        with self.assertRaises(ValidationError) as context:
            self.payment.cardholder = "John"
        self.assertIn("Cardholder should follow format", context.exception.field)


class TestCardnumberProperty(TestCreditCardPayment):
    """Test cases for cardnumber property getter and setter."""

    def test_cardnumber_getter_default_value(self):
        """Test that cardnumber getter returns default empty string."""
        self.assertEqual(self.payment.cardnumber, "")

    def test_cardnumber_setter_valid_16_digits(self):
        """Test that cardnumber setter accepts valid 16-digit number."""
        self.payment.cardnumber = "1234567890123456"
        self.assertEqual(self.payment.cardnumber, "1234567890123456")

    def test_cardnumber_setter_different_valid_number(self):
        """Test that cardnumber setter accepts different valid 16-digit number."""
        self.payment.cardnumber = "9876543210987654"
        self.assertEqual(self.payment.cardnumber, "9876543210987654")

    def test_cardnumber_setter_invalid_too_short(self):
        """Test that cardnumber setter raises ValidationError for short number."""
        with self.assertRaises(ValidationError):
            self.payment.cardnumber = "123456789012345"

    def test_cardnumber_setter_invalid_too_long(self):
        """Test that cardnumber setter raises ValidationError for long number."""
        with self.assertRaises(ValidationError):
            self.payment.cardnumber = "12345678901234567"

    def test_cardnumber_setter_invalid_with_letters(self):
        """Test that cardnumber setter raises ValidationError for letters."""
        with self.assertRaises(ValidationError):
            self.payment.cardnumber = "123456789012345A"

    def test_cardnumber_setter_invalid_with_spaces(self):
        """Test that cardnumber setter raises ValidationError for spaces."""
        with self.assertRaises(ValidationError):
            self.payment.cardnumber = "1234 5678 9012 3456"

    def test_cardnumber_setter_invalid_empty(self):
        """Test that cardnumber setter raises ValidationError for empty string."""
        with self.assertRaises(ValidationError):
            self.payment.cardnumber = ""


class TestExpirationdateProperty(TestCreditCardPayment):
    """Test cases for expirationdate property getter and setter."""

    def test_expirationdate_getter_default_value(self):
        """Test that expirationdate getter returns default empty string."""
        self.assertEqual(self.payment.expirationdate, "")

    def test_expirationdate_setter_valid_future_date(self):
        """Test that expirationdate setter accepts valid future date."""
        self.payment.expirationdate = "12-30"
        self.assertEqual(self.payment.expirationdate, "12-30")

    def test_expirationdate_setter_valid_different_date(self):
        """Test that expirationdate setter accepts different valid future date."""
        self.payment.expirationdate = "06-28"
        self.assertEqual(self.payment.expirationdate, "06-28")

    def test_expirationdate_setter_invalid_past_date(self):
        """Test that expirationdate setter raises ValidationError for past date."""
        with self.assertRaises(ValidationError):
            self.payment.expirationdate = "01-20"

    def test_expirationdate_setter_invalid_format_slash(self):
        """Test that expirationdate setter raises ValidationError for slash format."""
        with self.assertRaises(ValidationError):
            self.payment.expirationdate = "12/30"

    def test_expirationdate_setter_invalid_format_no_separator(self):
        """Test that expirationdate setter raises ValidationError without separator."""
        with self.assertRaises(ValidationError):
            self.payment.expirationdate = "1230"

    def test_expirationdate_setter_invalid_format_letters(self):
        """Test that expirationdate setter raises ValidationError for letters."""
        with self.assertRaises(ValidationError):
            self.payment.expirationdate = "AB-CD"

    def test_expirationdate_setter_invalid_empty(self):
        """Test that expirationdate setter raises ValidationError for empty string."""
        with self.assertRaises(ValidationError):
            self.payment.expirationdate = ""


class TestCVVProperty(TestCreditCardPayment):
    """Test cases for CVV property getter and setter."""

    def test_cvv_getter_default_value(self):
        """Test that cvv getter returns default empty string."""
        self.assertEqual(self.payment.cvv, "")

    def test_cvv_setter_valid_three_digits(self):
        """Test that cvv setter accepts valid 3-digit CVV."""
        self.payment.cvv = "123"
        self.assertEqual(self.payment.cvv, "123")

    def test_cvv_setter_valid_four_digits(self):
        """Test that cvv setter accepts valid 4-digit CVV (AMEX)."""
        self.payment.cvv = "1234"
        self.assertEqual(self.payment.cvv, "1234")

    def test_cvv_setter_different_valid_cvv(self):
        """Test that cvv setter accepts different valid 3-digit CVV."""
        self.payment.cvv = "987"
        self.assertEqual(self.payment.cvv, "987")

    def test_cvv_setter_invalid_too_short(self):
        """Test that cvv setter raises ValidationError for short CVV."""
        with self.assertRaises(ValidationError):
            self.payment.cvv = "12"

    def test_cvv_setter_invalid_too_long(self):
        """Test that cvv setter raises ValidationError for long CVV."""
        with self.assertRaises(ValidationError):
            self.payment.cvv = "12345"

    def test_cvv_setter_invalid_with_letters(self):
        """Test that cvv setter raises ValidationError for letters."""
        with self.assertRaises(ValidationError):
            self.payment.cvv = "12A"

    def test_cvv_setter_invalid_empty(self):
        """Test that cvv setter raises ValidationError for empty string."""
        with self.assertRaises(ValidationError):
            self.payment.cvv = ""


if __name__ == "__main__":
    unittest.main()
