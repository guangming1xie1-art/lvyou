"""ProcessPaymentSkill - Handle payment processing"""

from typing import Any, Dict
from datetime import datetime
import random
from ..base_skill import BaseSkill

try:
    from utils.java_api_client import java_api_client, JavaAPIError
except ModuleNotFoundError:
    from src.utils.java_api_client import java_api_client, JavaAPIError

try:
    from utils.logger import app_logger
except ModuleNotFoundError:
    from src.utils.logger import app_logger


class ProcessPaymentSkill(BaseSkill):
    """Process payment for a booking
    
    This skill handles payment processing including validation,
    authorization, and transaction confirmation.
    """
    
    name = "process_payment"
    agent_type = "booking"
    description = "Handle payment processing for bookings including validation and authorization"
    version = "2.0.0"
    
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
            app_logger.error(f"ProcessPaymentSkill: Invalid input for booking {booking_id}")
            return {
                "payment_status": "failed",
                "transaction_id": None,
                "booking_id": booking_id,
                "amount_charged": 0,
                "currency": currency,
                "payment_method": payment_method,
                "processed_at": datetime.now().isoformat(),
                "message": "Invalid input: booking_id, payment_method, and amount are required",
                "next_steps": ["Check your input and try again"]
            }
        
        # Validation
        if amount <= 0:
            return {
                "payment_status": "failed",
                "transaction_id": None,
                "booking_id": booking_id,
                "amount_charged": 0,
                "currency": currency,
                "payment_method": payment_method,
                "processed_at": datetime.now().isoformat(),
                "message": "Amount must be greater than zero",
                "next_steps": ["Enter a valid amount"]
            }

        app_logger.info(f"Processing payment for booking {booking_id}, amount: {amount} {currency}")
        
        try:
            # Prepare payment details for API
            # The API expects payment_method and payment_data (which is the details)
            api_payment_data = payment_details or {}
            api_payment_data["amount"] = amount
            api_payment_data["currency"] = currency
            
            # Call Java API
            result = await java_api_client.process_payment(
                booking_id=booking_id,
                payment_method=payment_method,
                payment_data=api_payment_data
            )
            
            transaction_id = result.get("payment_id")
            app_logger.info(f"Payment processed successfully for booking {booking_id}: {transaction_id}")
            
            processed_at = result.get("transaction_time") or datetime.now().isoformat()
            
            # Match output_schema
            return {
                "payment_status": result.get("status", "success"),
                "transaction_id": transaction_id,
                "booking_id": booking_id,
                "amount_charged": result.get("amount", amount),
                "currency": currency,
                "payment_method": payment_method,
                "processed_at": processed_at,
                "receipt": {
                    "receipt_number": f"RCP-{transaction_id}",
                    "receipt_url": f"https://bookings.example.com/receipts/{transaction_id}"
                },
                "message": "Payment processed successfully!",
                "next_steps": [
                    "Booking is now confirmed",
                    "Confirmation email sent to registered email",
                    "Check booking status anytime with booking ID"
                ]
            }

        except JavaAPIError as e:
            app_logger.error(f"ProcessPaymentSkill: Java API error for booking {booking_id} - {e}")
            # If it's a 5xx error or timeout, the payment status is unknown
            status = "pending" if e.status_code and (e.status_code >= 500 or e.status_code == 408) else "failed"
            
            return {
                "payment_status": status,
                "transaction_id": None,
                "booking_id": booking_id,
                "amount_charged": 0,
                "currency": currency,
                "payment_method": payment_method,
                "processed_at": datetime.now().isoformat(),
                "message": f"Payment processing error: {str(e)}",
                "next_steps": [
                    "Check your booking status before trying again" if status == "pending" else "Try again with correct details",
                    "Contact support if the issue persists"
                ]
            }
        except Exception as e:
            app_logger.error(f"ProcessPaymentSkill: Unexpected error for booking {booking_id} - {e}", exc_info=True)
            return {
                "payment_status": "pending", # Assume pending on unexpected error to be safe
                "transaction_id": None,
                "booking_id": booking_id,
                "amount_charged": 0,
                "currency": currency,
                "payment_method": payment_method,
                "processed_at": datetime.now().isoformat(),
                "message": "支付处理时发生未知错误，请检查预订状态",
                "next_steps": ["Check booking status to verify if payment was successful"]
            }
