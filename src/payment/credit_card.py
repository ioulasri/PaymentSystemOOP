from payment.payment_strategy import PaymentStrategy
from payment.exceptions import *
import re
from datetime import date

class CreditCardPayment(PaymentStrategy):
	def __init__(self):
		"""
		Initialize a new Credit Card payment method.

		Attributes:
			card_number (str): The 16-digit credit card number.
			card_holder (str): The name of the cardholder as it appears on the card.
			expiration_date (str): The card expiration date in MM/YY format.
			cvv (str): The card verification value, typically 3-4 digits.
		"""
		super().__init__()
		self.card_number: str
		self.card_holder: str 
		self.expiration_date: str
		self.cvv: str
	


	def validate(self) -> bool:
		"""
		Validate credit card information before processing payment.

		Performs comprehensive validation including:
		- Cardholder name presence
		- Card number length (16 digits)
		- Expiration date format (MM/YY)
		- Expiration date validity (not expired)
		- CVV length (3-4 digits)

		Returns:
			bool: True if all validations pass.

		Raises:
			ValidationError: If any validation check fails with specific error message.
		"""
		if not self.card_holder:
			raise ValidationError("ValidationError", "card holder empty")
		if not self.check_cardnumber_length(self.card_number):
			raise ValidationError("ValidationError", "card number length is invalid")
		if not self.check_expirationdate_format(self.expiration_date):
			raise ValidationError("ValidationError", "expiration date format is invalid")
		if not self.check_expirationdate(self.expiration_date):
			raise ValidationError("ValidationError", "expiration date is in the past")
		if not self.check_cvv_length(self.cvv):
			raise ValidationError("ValidationError", "cvv length is invalid")
		return True
	
	
	def execute(self, amount: float) -> dict:
		"""
		Process the credit card payment transaction.

		Args:
			amount (float): The payment amount to charge to the card.

		Returns:
			dict: Transaction details including status, transaction ID, timestamp, and amount.

		Raises:
			PaymentError: If the payment processing fails.
			ValidationError: If validation fails before processing.
		"""
		pass


	def generate_receipt(self) -> dict:
		"""
		Generate a payment receipt with transaction details.

		Returns:
			dict: Receipt information containing:
				- Transaction ID
				- Payment method (Credit Card)
				- Masked card number (last 4 digits only)
				- Cardholder name
				- Amount charged
				- Timestamp
				- Transaction status
		"""
		pass

	def check_cardnumber_length(self, card_number: str) -> bool:
		"""
		Validate that the card number has the correct length.

		Args:
			card_number (str): The credit card number to validate.

		Returns:
			bool: True if card number is 16 digits, False otherwise.
		"""
		return card_number.isdigit() and len(card_number) == 16

	def check_expirationdate_format(self, expiration_date: str) -> bool:
		"""
		Validate the expiration date format.

		Args:
			expiration_date (str): The expiration date to validate.

		Returns:
			bool: True if format is MM/YY, False otherwise.
		"""
		return re.fullmatch(r"^\d{2}-\d{2}$", expiration_date)

	def check_expirationdate(self, expiration_date: str) -> bool:
		"""
		Validate that the expiration date is not in the past.

		Args:
			expiration_date (str): The expiration date in MM/YY format.

		Returns:
			bool: True if date is current or future, False if expired.
		"""
		expired_date = date(int(expiration_date[3:]), int(expiration_date[:3]), 1)
		current_date = date.today()
		return current_date < expired_date

	def check_cvv_length(self, cvv: str) -> bool:
		"""
		Validate that the CVV has the correct length.

		Args:
			cvv (str): The card verification value to validate.

		Returns:
			bool: True if CVV is 3-4 digits, False otherwise.
		"""
		return cvv.isdigit() and (len(cvv) == 3 or len(cvv) == 4)
