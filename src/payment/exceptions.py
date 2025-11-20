
class ProjectError(Exception):
	"""Raised when input validation fails."""

	def __init__(self, message, field=None):
		self.message = message
		self.field = field
		super().__init__(f"{message}" + (f" (Field): {field}") if field else "")

class ValidationError(ProjectError):
	"""Raised when input validation fails."""

	def __init__(self, message, field=None):
		super().__init__(message, field)
		
class PaymentError(ProjectError):
	"""Raised when payment fails."""

	def __init__(self, message, field=None):
		super().__init__(message, field)

class ProjectValueError(ProjectError):
	"""Raised when value validation fails."""

	def __init__(self, message, field=None):
		super().__init__(message, field)

class OrderError(ProjectError):
	"""Raised when order fails"""

	def __init__(self, message, field=None):
		super().__init__(message, field)

class ProjectTypeError(ProjectError):
	"""Raised when type validation fails."""

	def __init__(self, message, field=None):
		super().__init__(message, field)

