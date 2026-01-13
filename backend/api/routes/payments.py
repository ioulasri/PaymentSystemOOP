"""
Payment processing routes.
Uses your existing PaymentFactory, PaymentProcessor, and payment method classes.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from schemas.payment import PaymentRequest, PaymentResponse
from api.routes.auth import get_current_user
from src.services.payment_factory import PaymentFactory  # YOUR existing factory
from src.services.payment_processor import PaymentProcessor  # YOUR existing processor
from src.models.customer import Customer  # YOUR existing model

router = APIRouter()


@router.post("/process", response_model=PaymentResponse)
async def process_payment(
    payment_data: PaymentRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Process a payment for an order.
    
    - Validates payment details
    - Uses existing PaymentFactory and PaymentProcessor
    - Returns transaction receipt
    """
    try:
        # TODO: Fetch order from database
        # order_repo = OrderRepository()
        # order = order_repo.get(payment_data.order_id)
        
        # Create customer using YOUR existing Customer model
        customer = Customer(current_user["email"], current_user["email"])
        
        # Create payment method using YOUR existing PaymentFactory
        payment_details = payment_data.payment_details
        
        if payment_details.payment_type == "credit_card":
            payment_method = PaymentFactory.create(
                "credit_card",
                cardholder=payment_details.cardholder,
                cardnumber=payment_details.cardnumber,
                expirationdate=payment_details.expirationdate,
                cvv=payment_details.cvv,
                balance=10000.00  # TODO: Get from database
            )
        elif payment_details.payment_type == "paypal":
            payment_method = PaymentFactory.create(
                "paypal",
                email=payment_details.email,
                password=payment_details.password,
                balance=10000.00  # TODO: Get from database
            )
        elif payment_details.payment_type == "crypto":
            payment_method = PaymentFactory.create(
                "crypto",
                wallet_address=payment_details.wallet_address,
                crypto_type=payment_details.crypto_type,
                balance=10.0  # TODO: Get from database
            )
        else:
            raise ValueError("Invalid payment type")
        
        # Process with YOUR existing PaymentProcessor
        # receipt = PaymentProcessor.process_payment(customer, order, payment_method)
        # return PaymentResponse.from_receipt(receipt)
        
        # For now, mock response until order is fetched from DB
        mock_receipt = {
            "TransactionID": "TXN-MOCK-12345",
            "Amount": 100.00,
            "PaymentMethod": payment_details.payment_type,
            "CardNumber": getattr(payment_details, 'cardnumber', None),
            "Transaction status": "completed"
        }
        return PaymentResponse.from_receipt(mock_receipt)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment processing failed: {str(e)}"
        )