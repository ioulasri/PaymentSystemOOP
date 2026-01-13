"""
Pydantic schemas for Payment API endpoints.
Validates API input and converts to PaymentFactory parameters.
Uses your existing PaymentFactory, PaymentProcessor, and payment method classes.
"""

from pydantic import BaseModel, Field
from typing import Literal, Optional, Union
from decimal import Decimal

# Your existing payment classes are used by the routes
# from src.payment.methods.credit_card import CreditCardPayment
# from src.payment.methods.paypal import PayPalPayment
# from src.payment.methods.crypto import CryptoPayment
# from src.services.payment_factory import PaymentFactory


class CreditCardPaymentInput(BaseModel):
    """Credit card payment details (API input)."""
    payment_type: Literal["credit_card"] = "credit_card"
    cardholder: str = Field(..., min_length=3)
    cardnumber: str = Field(..., pattern=r"^\d{13,19}$")
    expirationdate: str = Field(..., pattern=r"^\d{2}-\d{2}$")  # MM-YY
    cvv: str = Field(..., pattern=r"^\d{3,4}$")


class PayPalPaymentInput(BaseModel):
    """PayPal payment details (API input)."""
    payment_type: Literal["paypal"] = "paypal"
    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    password: str = Field(..., min_length=6)


class CryptoPaymentInput(BaseModel):
    """Cryptocurrency payment details (API input)."""
    payment_type: Literal["crypto"] = "crypto"
    wallet_address: str = Field(..., min_length=26, max_length=62)
    crypto_type: Literal["BTC", "ETH", "USDT"] = "BTC"


class PaymentRequest(BaseModel):
    """Payment processing request (API input)."""
    order_id: str
    payment_details: Union[CreditCardPaymentInput, PayPalPaymentInput, CryptoPaymentInput] = Field(..., discriminator='payment_type')


class PaymentResponse(BaseModel):
    """Payment processing response (API output)."""
    success: bool
    transaction_id: str
    amount: Decimal
    payment_method: str
    card_number: Optional[str] = None
    status: str
    message: str

    @staticmethod
    def from_receipt(receipt: dict) -> "PaymentResponse":
        """
        Convert receipt from PaymentProcessor.process_payment() to API response.
        
        Your existing PaymentProcessor returns a dict with:
        - TransactionID
        - Amount
        - PaymentMethod
        - CardNumber (optional)
        - Transaction status
        """
        return PaymentResponse(
            success=receipt.get("Transaction status") == "completed",
            transaction_id=receipt.get("TransactionID", ""),
            amount=Decimal(str(receipt.get("Amount", 0))),
            payment_method=receipt.get("PaymentMethod", ""),
            card_number=receipt.get("CardNumber"),
            status=receipt.get("Transaction status", "failed"),
            message="Payment processed successfully" if receipt.get("Transaction status") == "completed" else "Payment failed"
        )