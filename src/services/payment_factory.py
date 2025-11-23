"""Payment factory module for creating payment method instances.

This module provides a factory class for instantiating and configuring
various payment method types (credit card, PayPal, cryptocurrency).
"""

from typing import Any

from src.core.base import PaymentStrategy
from src.core.exceptions import ValidationError
from src.payment.methods.credit_card import CreditCardPayment
from src.payment.methods.crypto import CryptoPayment
from src.payment.methods.paypal import Paypal
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PaymentFactory:
    """Factory for creating payment method instances.

    Centralizes payment method creation logic and ensures
    all required fields are provided and validated.
    """

    SUPPORTED_TYPES = {
        "credit_card": CreditCardPayment,
        "paypal": Paypal,
        "crypto": CryptoPayment,
    }

    @staticmethod
    def create(payment_type: str, **kwargs: Any) -> PaymentStrategy:
        """Create a payment method instance.

        Args:
            payment_type: Type of payment ("credit_card", "paypal", "crypto")
            **kwargs: Payment-specific parameters

        Returns:
            Configured PaymentStrategy instance

        Raises:
            ValidationError: If payment type is unsupported or parameters invalid
        """
        logger.info(
            "Creating payment method",
            extra={
                "payment_type": payment_type,
                "params_provided": list(kwargs.keys()),
            },
        )

        if payment_type not in PaymentFactory.SUPPORTED_TYPES:
            logger.error(
                "Unsupported payment type requested",
                extra={
                    "payment_type": payment_type,
                    "supported_types": list(PaymentFactory.SUPPORTED_TYPES.keys()),
                },
            )
            raise ValidationError(
                "ValidationError", f"Unsupported payment type: {payment_type}"
            )
        payment_class = PaymentFactory.SUPPORTED_TYPES[payment_type]
        payment_method = payment_class()  # type: ignore[abstract]
        logger.debug(
            "Payment method instance created",
            extra={"payment_type": payment_type, "class": payment_class.__name__},
        )
        if isinstance(payment_method, CreditCardPayment):
            PaymentFactory._configure_creditcard(payment_method, kwargs)
        elif isinstance(payment_method, Paypal):
            PaymentFactory._configure_paypal(payment_method, kwargs)
        elif isinstance(payment_method, CryptoPayment):
            PaymentFactory._configure_crypto(payment_method, kwargs)

        logger.debug("Payment method configured", extra={"payment_type": payment_type})

        try:
            is_valid = payment_method.validate()
            if not is_valid:
                logger.error(
                    "Payment validation failed",
                    extra={
                        "payment_type": payment_type,
                        "reason": "invalid configuration",
                    },
                )
                raise ValidationError(
                    "ValidationError",
                    "Payment validation failed: invalid payment configuration",
                )
        except ValidationError:
            raise
        except Exception as e:
            logger.error(
                "Payment validation exception",
                extra={"payment_type": payment_type, "error": str(e)},
                exc_info=True,
            )
            raise ValidationError(
                "ValidationError", f"Payment validation failed: {str(e)}"
            )

        logger.info(
            "Payment method created and validated successfully",
            extra={"payment_type": payment_type},
        )
        return payment_method

    @staticmethod
    def _configure_creditcard(payment: CreditCardPayment, params: dict) -> None:
        """Configure a CreditCardPayment instance with provided parameters."""
        if "cardholder" in params:
            payment.cardholder = params["cardholder"]
        if "cardnumber" in params:
            payment.cardnumber = params["cardnumber"]
        if "expirationdate" in params:
            payment.expirationdate = params["expirationdate"]
        if "cvv" in params:
            payment.cvv = params["cvv"]
        if "balance" in params:
            payment.balance = params["balance"]

    @staticmethod
    def _configure_paypal(payment: Paypal, params: dict) -> None:
        """Configure a PaypalPayment instance with provided parameters."""
        if "emailaddress" in params:
            payment.emailaddress = params["emailaddress"]
        if "passwordtoken" in params:
            payment.passwordtoken = params["passwordtoken"]
        if "verified" in params:
            payment.verified = params["verified"]
        if "balance" in params:
            payment.balance = params["balance"]

    @staticmethod
    def _configure_crypto(payment: CryptoPayment, params: dict) -> None:
        """Configure a CryptoPayment instance with provided parameters."""
        if "wallet_address" in params and "network" in params:
            try:
                payment.wallet_address = params["wallet_address"]
                payment.network = params["network"]
                logger.debug(
                    "Crypto payment configured",
                    extra={
                        "network": params["network"],
                        "wallet_address": params["wallet_address"][:10] + "...",
                    },
                )
            except ValueError as e:
                logger.error(
                    "Crypto configuration failed",
                    extra={"error": str(e), "network": params.get("network")},
                )
                raise ValidationError("ValidationError", str(e))
