import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.payment.credit_card import CreditCardPayment
from src.payment.exceptions import ValidationError
import unittest
from datetime import date


class TestCreditCardPayment(unittest.TestCase):
	"""Test suite for CreditCardPayment class."""

	def setUp(self):
		"""Set up test fixtures before each test method."""
		self.payment = CreditCardPayment()
		# Valid test data
		self.valid_card_number = "1234567890123456"
		self.valid_card_holder = "John Doe"
		self.valid_expiration_date = "12-30"  # December 2030
		self.valid_cvv = "123"

	def tearDown(self):
		"""Clean up after each test method."""
		self.payment = None


class TestCardNumberValidation(TestCreditCardPayment):
	"""Test cases for card number validation."""

	def test_valid_card_number_16_digits(self):
		"""Test that a valid 16-digit card number passes validation."""
		result = self.payment.check_cardnumber_length("1234567890123456")
		self.assertTrue(result)

	def test_invalid_card_number_too_short(self):
		"""Test that a card number shorter than 16 digits fails validation."""
		result = self.payment.check_cardnumber_length("123456789012345")
		self.assertFalse(result)

	def test_invalid_card_number_too_long(self):
		"""Test that a card number longer than 16 digits fails validation."""
		result = self.payment.check_cardnumber_length("12345678901234567")
		self.assertFalse(result)

	def test_invalid_card_number_with_letters(self):
		"""Test that a card number with non-digit characters fails validation."""
		result = self.payment.check_cardnumber_length("123456789012345A")
		self.assertFalse(result)

	def test_invalid_card_number_with_spaces(self):
		"""Test that a card number with spaces fails validation."""
		result = self.payment.check_cardnumber_length("1234 5678 9012 3456")
		self.assertFalse(result)

	def test_invalid_card_number_empty(self):
		"""Test that an empty card number fails validation."""
		result = self.payment.check_cardnumber_length("")
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
		result = self.payment.check_cvv_length("123")
		self.assertTrue(result)

	def test_valid_cvv_four_digits(self):
		"""Test that a 4-digit CVV passes validation (AMEX)."""
		result = self.payment.check_cvv_length("1234")
		self.assertTrue(result)

	def test_invalid_cvv_too_short(self):
		"""Test that a CVV shorter than 3 digits fails validation."""
		result = self.payment.check_cvv_length("12")
		self.assertFalse(result)

	def test_invalid_cvv_too_long(self):
		"""Test that a CVV longer than 4 digits fails validation."""
		result = self.payment.check_cvv_length("12345")
		self.assertFalse(result)

	def test_invalid_cvv_with_letters(self):
		"""Test that a CVV with letters fails validation."""
		result = self.payment.check_cvv_length("12A")
		self.assertFalse(result)

	def test_invalid_cvv_empty(self):
		"""Test that an empty CVV fails validation."""
		result = self.payment.check_cvv_length("")
		self.assertFalse(result)


class TestValidateMethod(TestCreditCardPayment):
	"""Test cases for the main validate method."""

	def test_validate_all_valid_data(self):
		"""Test that validate returns True when all data is valid."""
		self.payment.card_number = self.valid_card_number
		self.payment.card_holder = self.valid_card_holder
		self.payment.expiration_date = self.valid_expiration_date
		self.payment.cvv = self.valid_cvv
		
		result = self.payment.validate()
		self.assertTrue(result)

	def test_validate_empty_card_holder(self):
		"""Test that validate raises ValidationError for empty card holder."""
		self.payment.card_number = self.valid_card_number
		self.payment.card_holder = ""
		self.payment.expiration_date = self.valid_expiration_date
		self.payment.cvv = self.valid_cvv
		
		with self.assertRaises(ValidationError) as context:
			self.payment.validate()
		self.assertIn("card holder empty", str(context.exception))

	def test_validate_invalid_card_number(self):
		"""Test that validate raises ValidationError for invalid card number."""
		self.payment.card_number = "123"
		self.payment.card_holder = self.valid_card_holder
		self.payment.expiration_date = self.valid_expiration_date
		self.payment.cvv = self.valid_cvv
		
		with self.assertRaises(ValidationError) as context:
			self.payment.validate()
		self.assertIn("card number length is invalid", str(context.exception))

	def test_validate_invalid_expiration_format(self):
		"""Test that validate raises ValidationError for invalid expiration format."""
		self.payment.card_number = self.valid_card_number
		self.payment.card_holder = self.valid_card_holder
		self.payment.expiration_date = "12/30"
		self.payment.cvv = self.valid_cvv
		
		with self.assertRaises(ValidationError) as context:
			self.payment.validate()
		self.assertIn("expiration date format is invalid", str(context.exception))

	def test_validate_expired_card(self):
		"""Test that validate raises ValidationError for expired card."""
		self.payment.card_number = self.valid_card_number
		self.payment.card_holder = self.valid_card_holder
		self.payment.expiration_date = "01-20"
		self.payment.cvv = self.valid_cvv
		
		with self.assertRaises(ValidationError) as context:
			self.payment.validate()
		self.assertIn("expiration date is in the past", str(context.exception))

	def test_validate_invalid_cvv(self):
		"""Test that validate raises ValidationError for invalid CVV."""
		self.payment.card_number = self.valid_card_number
		self.payment.card_holder = self.valid_card_holder
		self.payment.expiration_date = self.valid_expiration_date
		self.payment.cvv = "12"
		
		with self.assertRaises(ValidationError) as context:
			self.payment.validate()
		self.assertIn("cvv length is invalid", str(context.exception))


if __name__ == "__main__":
	unittest.main()
