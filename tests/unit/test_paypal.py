import os
import sys
import unittest

from src.core.exceptions import ValidationError
from src.payment.methods.paypal import Paypal

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class TestPaypalPayment(unittest.TestCase):
    """Test suite for Paypal payment class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.payment = Paypal()
        # Valid test data
        self.valid_email = "user@example.com"
        self.valid_password = "Password123"
        self.valid_verified = True

    def tearDown(self):
        """Clean up after each test method."""
        self.payment = None


class TestEmailValidation(TestPaypalPayment):
    """Test cases for email validation."""

    def test_valid_email_simple(self):
        """Test that a simple valid email passes validation."""
        result = self.payment.check_email("user@example.com")
        self.assertTrue(result)

    def test_valid_email_with_dots(self):
        """Test that an email with dots passes validation."""
        result = self.payment.check_email("first.last@example.com")
        self.assertTrue(result)

    def test_valid_email_with_subdomain(self):
        """Test that an email with subdomain passes validation."""
        result = self.payment.check_email("user@mail.example.com")
        self.assertTrue(result)

    def test_valid_email_with_numbers(self):
        """Test that an email with numbers passes validation."""
        result = self.payment.check_email("user123@example.com")
        self.assertTrue(result)

    def test_invalid_email_no_at(self):
        """Test that an email without @ fails validation."""
        result = self.payment.check_email("userexample.com")
        self.assertFalse(result)

    def test_invalid_email_no_domain(self):
        """Test that an email without domain fails validation."""
        result = self.payment.check_email("user@")
        self.assertFalse(result)

    def test_invalid_email_no_username(self):
        """Test that an email without username fails validation."""
        result = self.payment.check_email("@example.com")
        self.assertFalse(result)

    def test_invalid_email_no_extension(self):
        """Test that an email without extension fails validation."""
        result = self.payment.check_email("user@example")
        self.assertFalse(result)

    def test_invalid_email_spaces(self):
        """Test that an email with spaces fails validation."""
        result = self.payment.check_email("user name@example.com")
        self.assertFalse(result)

    def test_invalid_email_empty(self):
        """Test that an empty email fails validation."""
        result = self.payment.check_email("")
        self.assertFalse(result)


class TestPasswordValidation(TestPaypalPayment):
    """Test cases for password validation."""

    def test_valid_password_letters_and_digits(self):
        """Test that a password with letters and digits passes validation."""
        result = self.payment.check_password("Password123")
        self.assertTrue(result)

    def test_valid_password_minimum_length(self):
        """Test that a password with exactly 8 characters passes validation."""
        result = self.payment.check_password("Pass1234")
        self.assertTrue(result)

    def test_valid_password_long(self):
        """Test that a long password passes validation."""
        result = self.payment.check_password("VeryLongPassword123456")
        self.assertTrue(result)

    def test_valid_password_mixed_case(self):
        """Test that a password with mixed case passes validation."""
        result = self.payment.check_password("PaSsWoRd123")
        self.assertTrue(result)

    def test_invalid_password_too_short(self):
        """Test that a password shorter than 8 characters fails validation."""
        result = self.payment.check_password("Pass12")
        self.assertFalse(result)

    def test_invalid_password_no_letters(self):
        """Test that a password without letters fails validation."""
        result = self.payment.check_password("12345678")
        self.assertFalse(result)

    def test_invalid_password_no_digits(self):
        """Test that a password without digits fails validation."""
        result = self.payment.check_password("Password")
        self.assertFalse(result)

    def test_invalid_password_empty(self):
        """Test that an empty password fails validation."""
        result = self.payment.check_password("")
        self.assertFalse(result)

    def test_invalid_password_only_spaces(self):
        """Test that a password with only spaces fails validation."""
        result = self.payment.check_password("        ")
        self.assertFalse(result)


class TestVerifiedValidation(TestPaypalPayment):
    """Test cases for verified status validation."""

    def test_valid_verified_true(self):
        """Test that True value passes validation."""
        result = self.payment.check_verified(True)
        self.assertTrue(result)

    def test_valid_verified_false(self):
        """Test that False value passes validation."""
        result = self.payment.check_verified(False)
        self.assertTrue(result)

    def test_invalid_verified_string(self):
        """Test that string value fails validation."""
        result = self.payment.check_verified("True")
        self.assertFalse(result)

    def test_invalid_verified_integer(self):
        """Test that integer value fails validation."""
        result = self.payment.check_verified(1)
        self.assertFalse(result)

    def test_invalid_verified_none(self):
        """Test that None value fails validation."""
        result = self.payment.check_verified(None)
        self.assertFalse(result)


class TestEmailaddressProperty(TestPaypalPayment):
    """Test cases for emailaddress property getter and setter."""

    def test_emailaddress_getter_default_value(self):
        """Test that emailaddress getter returns default empty string."""
        self.assertEqual(self.payment.emailaddress, "")

    def test_emailaddress_setter_valid_email(self):
        """Test that emailaddress setter accepts valid email."""
        self.payment.emailaddress = "user@example.com"
        self.assertEqual(self.payment.emailaddress, "user@example.com")

    def test_emailaddress_setter_different_valid_email(self):
        """Test that emailaddress setter accepts different valid email."""
        self.payment.emailaddress = "admin@test.org"
        self.assertEqual(self.payment.emailaddress, "admin@test.org")

    def test_emailaddress_setter_invalid_format(self):
        """Test that emailaddress setter raises ValidationError for invalid format."""
        with self.assertRaises(ValidationError):
            self.payment.emailaddress = "invalid-email"

    def test_emailaddress_setter_no_at_symbol(self):
        """Test that emailaddress setter raises ValidationError without @ symbol."""
        with self.assertRaises(ValidationError):
            self.payment.emailaddress = "userexample.com"

    def test_emailaddress_setter_empty(self):
        """Test that emailaddress setter raises ValidationError for empty string."""
        with self.assertRaises(ValidationError):
            self.payment.emailaddress = ""


class TestPasswordtokenProperty(TestPaypalPayment):
    """Test cases for passwordtoken property getter and setter."""

    def test_passwordtoken_getter_default_value(self):
        """Test that passwordtoken getter returns default empty string."""
        self.assertEqual(self.payment.passwordtoken, "")

    def test_passwordtoken_setter_valid_password(self):
        """Test that passwordtoken setter accepts valid password."""
        self.payment.passwordtoken = "Password123"
        self.assertEqual(self.payment.passwordtoken, "Password123")

    def test_passwordtoken_setter_different_valid_password(self):
        """Test that passwordtoken setter accepts different valid password."""
        self.payment.passwordtoken = "SecurePass456"
        self.assertEqual(self.payment.passwordtoken, "SecurePass456")

    def test_passwordtoken_setter_invalid_too_short(self):
        """Test that passwordtoken setter raises ValidationError for short password."""
        with self.assertRaises(ValidationError):
            self.payment.passwordtoken = "Pass12"

    def test_passwordtoken_setter_invalid_no_digits(self):
        """Test that passwordtoken setter raises ValidationError without digits."""
        with self.assertRaises(ValidationError):
            self.payment.passwordtoken = "Password"

    def test_passwordtoken_setter_invalid_no_letters(self):
        """Test that passwordtoken setter raises ValidationError without letters."""
        with self.assertRaises(ValidationError):
            self.payment.passwordtoken = "12345678"

    def test_passwordtoken_setter_empty(self):
        """Test that passwordtoken setter raises ValidationError for empty string."""
        with self.assertRaises(ValidationError):
            self.payment.passwordtoken = ""


class TestVerifiedProperty(TestPaypalPayment):
    """Test cases for verified property getter and setter."""

    def test_verified_getter_default_value(self):
        """Test that verified getter returns default False value."""
        self.assertFalse(self.payment.verified)

    def test_verified_setter_true(self):
        """Test that verified setter accepts True value."""
        self.payment.verified = True
        self.assertTrue(self.payment.verified)

    def test_verified_setter_false(self):
        """Test that verified setter accepts False value."""
        self.payment.verified = False
        self.assertFalse(self.payment.verified)

    def test_verified_setter_invalid_string(self):
        """Test that verified setter raises error for string value."""
        try:
            self.payment.verified = "True"
            self.fail("Should have raised ValidationError")
        except Exception as e:
            # Check either the str representation or the message attribute
            error_text = str(e) if str(e) else getattr(e, "message", "")
            self.assertIn("Verified must be", error_text)

    def test_verified_setter_invalid_integer(self):
        """Test that verified setter raises error for integer value."""
        try:
            self.payment.verified = 1
            self.fail("Should have raised ValidationError")
        except Exception as e:
            # Check either the str representation or the message attribute
            error_text = str(e) if str(e) else getattr(e, "message", "")
            self.assertIn("Verified must be", error_text)

    def test_verified_setter_invalid_none(self):
        """Test that verified setter raises error for None value."""
        try:
            self.payment.verified = None
            self.fail("Should have raised ValidationError")
        except Exception as e:
            # Check either the str representation or the message attribute
            error_text = str(e) if str(e) else getattr(e, "message", "")
            self.assertIn("Verified must be", error_text)


class TestValidateMethod(TestPaypalPayment):
    """Test cases for the main validate method."""

    def test_validate_all_valid_data(self):
        """Test that validate returns True when all data is valid."""
        self.payment.emailaddress = self.valid_email
        self.payment.passwordtoken = self.valid_password
        self.payment.verified = self.valid_verified

        result = self.payment.validate()
        self.assertTrue(result)

    def test_validate_invalid_email(self):
        """Test that validate raises ValidationError for invalid email."""
        self.payment.passwordtoken = self.valid_password
        self.payment.verified = self.valid_verified
        # Set invalid email directly to bypass setter validation
        self.payment._Paypal__emailaddress = "invalid-email"

        with self.assertRaises(ValidationError) as context:
            self.payment.validate()
        self.assertIn("Email format is invalid", context.exception.field)

    def test_validate_invalid_password(self):
        """Test that validate raises ValidationError for invalid password."""
        self.payment.emailaddress = self.valid_email
        self.payment.verified = self.valid_verified
        # Set invalid password directly to bypass setter validation
        self.payment._Paypal__passwordtoken = "weak"

        with self.assertRaises(ValidationError) as context:
            self.payment.validate()
        self.assertIn("Password is not strong", context.exception.field)

    def test_validate_invalid_verified_type(self):
        """Test that validate raises ValueError for invalid verified type."""
        self.payment.emailaddress = self.valid_email
        self.payment.passwordtoken = self.valid_password
        # Set invalid verified directly to bypass setter validation
        self.payment._verified = "True"

        try:
            self.payment.validate()
            self.fail("Should have raised ValueError")
        except Exception as e:
            # Check either the str representation or the message attribute
            error_text = str(e) if str(e) else getattr(e, "message", "")
            self.assertIn("Verified should be", error_text)

    def test_validate_empty_email(self):
        """Test that validate raises ValidationError for empty email."""
        self.payment.passwordtoken = self.valid_password
        self.payment.verified = self.valid_verified
        # Email is empty by default

        with self.assertRaises(ValidationError) as context:
            self.payment.validate()
        self.assertIn("Email format is invalid", context.exception.field)

    def test_validate_empty_password(self):
        """Test that validate raises ValidationError for empty password."""
        self.payment.emailaddress = self.valid_email
        self.payment.verified = self.valid_verified
        # Password is empty by default

        with self.assertRaises(ValidationError) as context:
            self.payment.validate()
        self.assertIn("Password is not strong", context.exception.field)


if __name__ == "__main__":
    unittest.main()
