from payment.payment_strategy import PaymentStrategy

class CreditCardPayment(PaymentStrategy):
	def __init__(self):
		super().__init__()
		