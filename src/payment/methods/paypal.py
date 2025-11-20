from src.core.base import PaymentStrategy
from src.core.exceptions import *
import re
from datetime import date

class Paypal(PaymentStrategy):
	"""
	PayPal payment strategy implementation.

	Handles PayPal account-based payments with email verification,
	password/token authentication, and account verification status.

	Attributes:
		emailaddress (str): The PayPal account email address.
		passwordtoken (str): The password or authentication token.
		verified (bool): Whether the PayPal account is verified.
	"""

	def __init__(self):
		"""
		Initialize a new PayPal payment method.

		All attributes are initialized to default values:
		- emailaddress: empty string
		- passwordtoken: empty string
		- verified: False
		"""
		super().__init__()
		self.__emailaddress: str = ""
		self.__passwordtoken: str = ""
		self._verified: bool = False
		self._balance: float = 0

	@property
	def balance(self) -> float:
		"""
		Get the current balance available on the PayPal account.

		Returns:
			float: The current balance amount.
		"""
		return self._balance
	
	@balance.setter
	def balance(self, value: float) -> None:
		"""
		Set the balance available on the PayPal account.

		Args:
			value (float): The balance amount to set.

		Raises:
			ValidationError: If the balance value is negative.
		"""
		if value < 0:
			raise ValidationError("ValidationError", "Balance cannot be negative")
		self._balance = value

	@property
	def emailaddress(self) -> str:
		"""
		Get the PayPal account email address.

		Returns:
			str: The email address associated with the PayPal account.
		"""
		return self.__emailaddress
	
	@emailaddress.setter
	def emailaddress(self, value: str) -> None:
		"""
		Set the PayPal account email address with validation.

		The email must follow standard email format (e.g., user@domain.com).

		Args:
			value (str): The email address to set.

		Raises:
			ValidationError: If the email format is invalid.
		"""
		if not self.check_email(value):
			raise ValidationError("ValidationError", "Email format is invalid")
		self.__emailaddress = value

	@property
	def passwordtoken(self) -> str:
		"""
		Get the PayPal account password or authentication token.

		Returns:
			str: The password or token for authentication.
		"""
		return self.__passwordtoken
	
	@passwordtoken.setter
	def passwordtoken(self, value: str) -> None:
		"""
		Set the PayPal account password or authentication token with validation.

		The password must be at least 8 characters long and contain both
		letters and digits for security.

		Args:
			value (str): The password or token to set.

		Raises:
			ValidationError: If the password doesn't meet strength requirements.
		"""
		if not self.check_password(value):
			raise ValidationError("ValidationError", "Password is not strong")
		self.__passwordtoken = value

	@property
	def verified(self) -> bool:
		"""
		Get the PayPal account verification status.

		Returns:
			bool: True if the account is verified, False otherwise.
		"""
		return self._verified
	
	@verified.setter
	def verified(self, value: bool) -> None:
		"""
		Set the PayPal account verification status.

		Args:
			value (bool): The verification status (True for verified, False otherwise).

		Raises:
			ValidationError: If the value is not a boolean.
		"""
		if not isinstance(value, bool):
			raise ValidationError("ValidationError", "Verified must be a boolean value")
		self._verified = value

	def validate(self) -> bool:
		"""
		Validate PayPal account information before processing payment.

		Checks that all required fields are populated and properly formatted.

		Returns:
			bool: True if all validations pass.

		Raises:
			ValidationError: If any required field is empty or invalid.
			ValueError: If the verified status is not a boolean.

		Note:
			This method performs comprehensive validation including format checks
			for email and password strength.
		"""
		if not self.check_email(self.emailaddress):
			raise ValidationError("ValidationError", "Email format is invalid")
		if not self.check_password(self.passwordtoken):
			raise ValidationError("ValidationError", "Password is not strong")
		if not self.check_verified(self._verified):
			raise ProjectValueError("ValueError", "Verified should be a boolean")
		return True

	def execute(self, amount: float) -> dict:
		"""
		Process the PayPal payment transaction.

		Args:
			amount (float): The payment amount to charge to the PayPal account.

		Returns:
			dict: Transaction details including status, transaction ID, timestamp, and amount.

		Raises:
			PaymentError: If the payment processing fails due to insufficient balance or unverified account.
			ValidationError: If validation fails before processing.
		"""
		if not self.verified:
			self.status = "Failed"
			raise PaymentError("PaymentError", "Account not verified")
		if amount > self.balance:
			self.status = "Failed"
			raise PaymentError("PaymentError", "Insufficient balance")
		self.status = "Success"
		self.balance -= amount
		return self.generate_receipt(amount)

	def generate_receipt(self, amount: float) -> dict:
		"""
		Generate a payment receipt with transaction details.

		Returns:
			dict: Receipt information containing:
				- Transaction ID
				- Payment method (PayPal)
				- Email address
				- Amount charged
				- Timestamp
				- Transaction status
				- Verification status
		"""
		receipt = {}
		receipt["TransactionID"] = self.transaction_id
		receipt["PaymentMethod"] = "PayPal"
		receipt["EmailAddress"] = self.emailaddress
		receipt["Amount"] = amount
		receipt["Timestamp"] = self.timestamp
		receipt["Transaction status"] = self.status
		return receipt

	def check_email(self, value: str) -> bool:
		"""
		Validate email address format.

		Checks if the email follows standard format: username@domain.extension

		Args:
			value (str): The email address to validate.

		Returns:
			bool: True if email format is valid, False otherwise.
		"""
		return re.fullmatch(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", value) is not None

	def check_password(self, value: str) -> bool:
		"""
		Validate password strength.

		Password must meet the following requirements:
		- At least 8 characters long
		- Contains at least one letter (uppercase or lowercase)
		- Contains at least one digit

		Args:
			value (str): The password to validate.

		Returns:
			bool: True if password meets strength requirements, False otherwise.
		"""
		return re.fullmatch(r"(?=.*[A-Za-z])(?=.*\d).{8,}", value) is not None

	def check_verified(self, value) -> bool:
		"""
		Validate that the verification status is a boolean.

		Args:
			value: The value to check.

		Returns:
			bool: True if value is a boolean, False otherwise.
		"""
		return isinstance(value, bool)