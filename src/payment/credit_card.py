from payment.payment_strategy import PaymentStrategy

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
		self.card_number: str
		self.card_holder: str 
		self.expiration_date: str
		self.cvv: str

	
	def validate(self):
		if not self.card_holder:
			return False
		valid = self.check_cardnumber_length(self.card_number)
		valid = self.check_expirationdate_format(self.expiration_date)
		valid = self.check_expirationdate(self.expiration_date)
		valid = self.check_cvv_length(self.cvv)
		return valid