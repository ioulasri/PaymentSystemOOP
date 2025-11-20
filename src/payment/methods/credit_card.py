import re
from datetime import date

from src.core.base import PaymentStrategy
from src.core.exceptions import PaymentError, ValidationError


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
        self._card_holder: str = ""
        self._balance = 0.0
        self.__card_number: str = ""
        self.__expiration_date: str = ""
        self.__cvv: str = ""

    @property
    def balance(self) -> float:
        """
        Get the current balance available on the credit card.

        Returns:
                float: The current balance amount.
        """
        return self._balance

    @balance.setter
    def balance(self, value: float) -> None:
        """
        Set the balance available on the credit card.

        Args:
                value (float): The balance amount to set.

        Raises:
                ValidationError: If the balance value is negative.
        """
        if value < 0:
            raise ValidationError("ValidationError", "Balance cannot be negative")
        self._balance = value

    @property
    def cardholder(self) -> str:
        """
        Get the cardholder's name.

        Returns:
                str: The name of the cardholder as it appears on the card.
        """
        return self._card_holder

    @cardholder.setter
    def cardholder(self, value: str) -> None:
        """
        Set the cardholder's name with validation.

        The cardholder name must follow the format: "Prefix Firstname Lastname"
        (e.g., "Mr John Doe", "Mrs Jane Smith").

        Args:
                value (str): The cardholder name in the format
                    "Prefix Firstname Lastname".

        Raises:
                ValidationError: If the name doesn't follow the required
                    format or any component is missing.
        """
        parts = value.split(" ")
        if len(parts) != 3:
            raise ValidationError(
                "ValidationError",
                "Cardholder should follow format: Prefix Firstname Lastname",
            )
        prefix, firstname, lastname = parts
        if not firstname or not lastname or not prefix:
            raise ValidationError(
                "ValidationError",
                "Cardholder should follow format: Prefix Firstname Lastname",
            )
        self._card_holder = value

    @property
    def cardnumber(self) -> str:
        """
        Get the credit card number.

        Returns:
                str: The 16-digit credit card number.
        """
        return self.__card_number

    @cardnumber.setter
    def cardnumber(self, value: str) -> None:
        """
        Set the credit card number with validation.

        The card number must be exactly 16 digits with no spaces or special characters.

        Args:
                value (str): The 16-digit credit card number.

        Raises:
                ValidationError: If the card number contains non-digit
                    characters or is not 16 digits long.
        """
        if not self.check_cardnumber(value):
            raise ValidationError(
                "ValidationError", "card number has non digit or length is invalid"
            )
        self.__card_number = value

    @property
    def expirationdate(self) -> str:
        """
        Get the card expiration date.

        Returns:
                str: The card expiration date in MM-YY format.
        """
        return self.__expiration_date

    @expirationdate.setter
    def expirationdate(self, value: str) -> None:
        """
        Set the card expiration date with validation.

        The expiration date must be in MM-YY format (e.g., "12-25" for December 2025)
        and must not be in the past.

        Args:
                value (str): The expiration date in MM-YY format.

        Raises:
                ValidationError: If the date format is invalid or the card
                    has already expired.
        """
        if not self.check_expirationdate_format(value):
            raise ValidationError(
                "ValidationError", "expiration date format is invalid"
            )
        try:
            if not self.check_expirationdate(value):
                raise ValidationError(
                    "ValidationError", "expiration date is in the past"
                )
        except (ValueError, IndexError):
            raise ValidationError(
                "ValidationError", "expiration date format is invalid"
            )
        self.__expiration_date = value

    @property
    def cvv(self) -> str:
        """
        Get the card verification value (CVV).

        Returns:
                str: The CVV code, typically 3-4 digits.
        """
        return self.__cvv

    @cvv.setter
    def cvv(self, value: str) -> None:
        """
        Set the card verification value (CVV) with validation.

        The CVV must be 3 digits for most cards or 4 digits for American Express cards.

        Args:
                value (str): The CVV code (3-4 digits).

        Raises:
                ValidationError: If the CVV contains non-digit characters
                    or is not 3-4 digits long.
        """
        if not self.check_cvv(value):
            raise ValidationError(
                "ValidationError", "cvv has non digit or length is invalid"
            )
        self.__cvv = value

    def deposit(self, amount: float) -> bool:
        """
        Add funds to the credit card balance.

        Args:
                amount (float): The amount to deposit (must be positive).

        Returns:
                bool: True if deposit was successful.

        Raises:
                ValidationError: If the deposit amount is not positive.
        """
        if amount <= 0:
            raise ValidationError("ValidationError", "Deposit amount must be positive")

        self.balance += amount
        return True

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
                ValidationError: If any validation check fails with
                    specific error message.
        """
        if not self.cardholder:
            raise ValidationError("ValidationError", "card holder empty")
        if not self.check_cardnumber(self.cardnumber):
            raise ValidationError(
                "ValidationError", "card number has non digit or length is invalid"
            )
        if not self.check_expirationdate_format(self.expirationdate):
            raise ValidationError(
                "ValidationError", "expiration date format is invalid"
            )
        if not self.check_expirationdate(self.expirationdate):
            raise ValidationError("ValidationError", "expiration date is in the past")
        if not self.check_cvv(self.cvv):
            raise ValidationError(
                "ValidationError", "cvv has non digit or length is invalid"
            )
        return True

    def execute(self, amount: float) -> dict:
        """
        Process the credit card payment transaction.

        Args:
                amount (float): The payment amount to charge to the card.

        Returns:
                dict: Transaction details including status, transaction ID,
                    timestamp, and amount.

        Raises:
                PaymentError: If the payment processing fails.
                ValidationError: If validation fails before processing.
        """
        if amount > self.balance:
            self.status = "Failed"
            raise PaymentError("PaymentError", "Insufficient balance")
        self.status = "Success"
        self.balance -= amount
        return self.generate_receipt(amount)

    def generate_receipt(self, amount: float) -> dict:
        """
        Generate a payment receipt with transaction details.

        Args:
                amount (float): The payment amount for the receipt.

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
        receipt = {}
        receipt["TransactionID"] = self.transaction_id
        receipt["PaymentMethod"] = "Credit Card"
        receipt["CardNumber"] = self.masked_card(self.cardnumber)
        receipt["CardHolder"] = self.cardholder
        receipt["Amount"] = amount
        receipt["Timestamp"] = self.timestamp
        receipt["Transaction status"] = self.status
        return receipt

    def check_cardnumber(self, card_number: str) -> bool:
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
                bool: True if format is MM-YY, False otherwise.
        """
        return re.fullmatch(r"\d{2}-\d{2}", expiration_date) is not None

    def check_expirationdate(self, expiration_date: str) -> bool:
        """
        Validate that the expiration date is not in the past.

        Args:
                expiration_date (str): The expiration date in MM-YY format.

        Returns:
                bool: True if date is current or future, False if expired.

        Note:
                Cards are valid through the end of the expiration month.
        """
        month, year = expiration_date.split("-")
        full_year = 2000 + int(year)
        current_date = date.today()
        return current_date.year < full_year or (
            current_date.year == full_year and current_date.month <= int(month)
        )

    def check_cvv(self, cvv: str) -> bool:
        """
        Validate that the CVV has the correct length.

        Args:
                cvv (str): The card verification value to validate.

        Returns:
                bool: True if CVV is 3-4 digits, False otherwise.
        """
        return cvv.isdigit() and (len(cvv) == 3 or len(cvv) == 4)

    def masked_card(self, card_number: str) -> str:
        """
        Mask a card number showing only the last 4 digits.

        Args:
                card_number (str): The card number to mask.

        Returns:
                str: Masked card number with first 12 digits replaced by asterisks.
        """
        masked = ""
        digit_index = 0
        for c in card_number:
            if c.isdigit():
                if digit_index < 12:
                    masked += "*"
                else:
                    masked += c
                digit_index += 1
            else:
                masked += c
        return masked
