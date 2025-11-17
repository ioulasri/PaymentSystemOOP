
class ValidationError(Exception):
	"""Raised when input validation fails."""

	def __init__(self, message, field=None):
		self.message = message
		self.field = field
		super().__init__(f"{message}" + (f" (Field): {field}") if field else "")