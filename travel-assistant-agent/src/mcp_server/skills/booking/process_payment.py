"""ProcessPaymentSkill - Handle payment processing"""

from typing import Any, Dict
from datetime import datetime
import random
from ..base_skill import BaseSkill


class ProcessPaymentSkill(BaseSkill):
    """Process payment for a booking
    
    This skill handles payment processing including validation,
    authorization, and transaction confirmation.
    """
    
    name = "process_payment"
    agent_type = "booking"
    description = "Handle payment processing for bookings including validation and authorization"
    version = "1.0.0"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "booking_id": {
                    "type": "string",
                    "description": "Booking ID to process payment for"
                },
                "payment_method": {
                    "type": "string",
                    "description": "Payment method",
                    "enum": ["credit_card", "debit_card", "paypal", "bank_transfer"]
                },
                "payment_details": {
                    "type": "object",
                    "description": "Payment details (card number, etc.)",
                    "properties": {
                        "cardholder_name": {"type": "string"},
                        "card_number": {"type": "string"},
                        "expiry_date": {"type": "string"},
                        "cvv": {"type": "string"},
                        "billing_address": {"type": "object"}
                    }
                },
                "amount": {
                    "type": "number",
                    "description": "Amount to charge"
                },
                "currency": {
                    "type": "string",
                    "description": "Currency code",
                    "default": "USD"
                }
            },
            "required": ["booking_id", "payment_method", "amount"]
        }
    
    @property
    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "payment_status": {
                    "type": "string",
                    "enum": ["success", "failed", "pending", "requires_action"]
                },
                "transaction_id": {"type": "string"},
                "booking_id": {"type": "string"},
                "amount_charged": {"type": "number"},
                "currency": {"type": "string"},
                "payment_method": {"type": "string"},
                "processed_at": {"type": "string"},
                "receipt": {
                    "type": "object",
                    "properties": {
                        "receipt_number": {"type": "string"},
                        "receipt_url": {"type": "string"}
                    }
                },
                "message": {"type": "string"},
                "next_steps": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["payment_status", "transaction_id", "booking_id", "amount_charged"]
        }
    
    async def execute(
        self,
        booking_id: str,
        payment_method: str,
        amount: float,
        currency: str = "USD",
        payment_details: Dict[str, Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Process payment
        
        Args:
            booking_id: Booking to pay for
            payment_method: Payment method
            amount: Amount to charge
            currency: Currency code
            payment_details: Payment information
            
        Returns:
            Payment processing result
        """
        if not self.validate_input({
            "booking_id": booking_id,
            "payment_method": payment_method,
            "amount": amount
        }):
            raise ValueError("Invalid input: booking_id, payment_method, and amount are required")
        
        # Mock payment processing
        # In production, this would integrate with payment gateway (Stripe, PayPal, etc.)
        
        processed_at = datetime.now()
        
        # Simulate payment validation
        is_valid = self._validate_payment(payment_method, payment_details, amount)
        
        if not is_valid:
            return {
                "payment_status": "failed",
                "transaction_id": f"TXN-FAILED-{random.randint(10000, 99999)}",
                "booking_id": booking_id,
                "amount_charged": 0,
                "currency": currency,
                "payment_method": payment_method,
                "processed_at": processed_at.isoformat(),
                "receipt": None,
                "message": "Payment validation failed. Please check your payment details and try again.",
                "next_steps": [
                    "Verify payment information is correct",
                    "Ensure sufficient funds are available",
                    "Contact your bank if issue persists",
                    "Try alternative payment method"
                ]
            }
        
        # Simulate successful payment (95% success rate in demo)
        success = random.random() < 0.95
        
        if success:
            transaction_id = f"TXN-{datetime.now().strftime('%Y%m%d')}-{random.randint(100000, 999999)}"
            receipt_number = f"RCP-{transaction_id[4:]}"
            
            return {
                "payment_status": "success",
                "transaction_id": transaction_id,
                "booking_id": booking_id,
                "amount_charged": amount,
                "currency": currency,
                "payment_method": payment_method,
                "processed_at": processed_at.isoformat(),
                "receipt": {
                    "receipt_number": receipt_number,
                    "receipt_url": f"https://bookings.example.com/receipts/{receipt_number}"
                },
                "message": "Payment processed successfully!",
                "next_steps": [
                    "Booking is now confirmed",
                    "Confirmation email sent to registered email",
                    "Download receipt from link above",
                    "Check booking status anytime with booking ID"
                ]
            }
        else:
            return {
                "payment_status": "failed",
                "transaction_id": f"TXN-FAILED-{random.randint(10000, 99999)}",
                "booking_id": booking_id,
                "amount_charged": 0,
                "currency": currency,
                "payment_method": payment_method,
                "processed_at": processed_at.isoformat(),
                "receipt": None,
                "message": "Payment processing failed. Please try again.",
                "next_steps": [
                    "Try processing payment again",
                    "Check with your payment provider",
                    "Use alternative payment method if available"
                ]
            }
    
    def _validate_payment(
        self, payment_method: str, payment_details: Dict[str, Any], amount: float
    ) -> bool:
        """Validate payment details (mock validation)"""
        
        # Basic validation
        if amount <= 0:
            return False
        
        if payment_method in ["credit_card", "debit_card"]:
            if not payment_details:
                return False
            
            # Check required fields
            required_fields = ["card_number", "expiry_date", "cvv"]
            for field in required_fields:
                if not payment_details.get(field):
                    return False
            
            # Basic card number check (simplified)
            card_number = payment_details.get("card_number", "").replace(" ", "").replace("-", "")
            if len(card_number) < 13 or len(card_number) > 19:
                return False
        
        return True
