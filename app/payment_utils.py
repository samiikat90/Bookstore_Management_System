"""
Payment Method Validation and Error Handling Module

This module provides comprehensive payment validation including:
- Credit card validation using Luhn algorithm
- Email validation for PayPal
- Bank transfer validation
- Custom payment error handling
"""

import re
import random
from typing import Dict, Any

# =============================================================================
# PAYMENT VALIDATION FUNCTIONS
# =============================================================================

def luhn_check(card_number: str) -> bool:
    """
    Performs the Luhn algorithm check on a credit card number string.

    The Luhn algorithm is a simple checksum formula used to validate
    a variety of identification numbers, such as credit card numbers.
    It helps guard against accidental errors, but is not a security measure.
    """
    # 1. Clean the input: remove spaces and non-digit characters
    digits = ''.join(filter(str.isdigit, card_number))

    if not 13 <= len(digits) <= 19:
        return False  # Card numbers typically fall in this range

    # Convert string digits to integers
    digits_int = [int(d) for d in digits]

    # 2. Process digits from right to left
    #   - Double every second digit starting from the right (the second to last)
    #   - If the doubling results in a number > 9, subtract 9 from the result
    #   - Sum all digits

    total_sum = 0
    num_digits = len(digits_int)

    for i in range(num_digits):
        # Process from the right (index num_digits - 1 - i)
        digit = digits_int[num_digits - 1 - i]

        # Every second digit starting from the right (i % 2 == 1)
        if i % 2 == 1:
            doubled_digit = digit * 2
            if doubled_digit > 9:
                doubled_digit -= 9
            total_sum += doubled_digit
        else:
            total_sum += digit

    # 3. The number is valid if the total sum is divisible by 10
    return total_sum % 10 == 0

def validate_email(email_address: str) -> bool:
    """
    Performs basic regex validation for an email address format.
    Used for payment methods like PayPal.
    """
    # Simple regex for structure: user@domain.tld
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.fullmatch(email_regex, email_address) is not None

def validate_payment_method(method_type: str, details: dict) -> tuple[bool, str]:
    """
    Central function to validate different payment methods based on type.

    Args:
        method_type: The type of payment method ('credit_card', 'paypal', 'bank_transfer').
        details: A dictionary containing method-specific details.

    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    method_type = method_type.lower().strip()

    if method_type == 'credit_card':
        card_num = details.get('number', '').strip()
        expiry = details.get('expiry', '').strip()
        cvv = details.get('cvv', '').strip()

        if not card_num or not expiry or not cvv:
            return False, "Credit Card requires number, expiry, and CVV."

        # Basic format checks
        if not re.match(r'\d{2}/\d{2}$', expiry):
            return False, f"Invalid expiry format: {expiry} (expected MM/YY)"

        if not re.match(r'^\d{3,4}$', cvv):
            return False, f"Invalid CVV format: {cvv} (expected 3 or 4 digits)"

        # Luhn check (The primary number validation)
        if not luhn_check(card_num):
            return False, "Credit card number failed validation check."

        return True, "Credit Card validated successfully."

    elif method_type == 'paypal':
        email = details.get('email', '').strip()
        if not email:
            return False, "PayPal requires email address."

        if validate_email(email):
            return True, f"PayPal email validated successfully: {email}"
        else:
            return False, f"Invalid PayPal email format: {email}"

    elif method_type == 'bank_transfer':
        # Simple placeholder for bank details (e.g., routing/account number)
        routing = details.get('routing_number', '').strip()
        account = details.get('account_number', '').strip()

        if not routing or not account:
            return False, "Bank Transfer requires routing number and account number."

        if routing.isdigit() and len(routing) == 9 and account.isdigit() and 8 <= len(account) <= 12:
            return True, "Bank details validated successfully."
        else:
            return False, "Invalid bank detail formats."

    else:
        return False, f"Unknown payment method type: {method_type}"

# =============================================================================
# PAYMENT ERROR HANDLING
# =============================================================================

class PaymentError(Exception):
    """Base class for all custom payment exceptions."""
    def __init__(self, message: str, code: str = "GENERIC_ERROR"):
        self.message = message
        self.code = code
        super().__init__(f"[{self.code}] {self.message}")

class CardDeclinedError(PaymentError):
    """Raised when the card issuer explicitly declines the transaction."""
    def __init__(self, reason: str):
        super().__init__(
            message=f"Card declined by issuer. Reason: {reason}",
            code="CARD_DECLINED"
        )

class InvalidPaymentMethodError(PaymentError):
    """Raised when the payment details (e.g., card number, CVC) are invalid."""
    def __init__(self):
        super().__init__(
            message="The payment method details provided are invalid (e.g., expired card, bad CVC).",
            code="INVALID_DETAILS"
        )

class InsufficientFundsError(CardDeclinedError):
    """Raised when the card is declined due to lack of money."""
    def __init__(self):
        super().__init__(reason="Insufficient funds")
        self.code = "INSUFFICIENT_FUNDS"

class NetworkTimeoutError(PaymentError):
    """Raised when there's a connectivity issue or timeout with the payment gateway."""
    def __init__(self):
        super().__init__(
            message="Connection to payment gateway timed out. Please try again.",
            code="NETWORK_TIMEOUT"
        )

def process_payment(amount: float, payment_method: str, payment_details: Dict[str, Any]) -> str:
    """
    Simulates a payment attempt and raises specific exceptions on failure.

    Args:
        amount: The monetary value to charge.
        payment_method: The type of payment method.
        payment_details: Dictionary containing payment details.

    Returns:
        A success message if the payment goes through.

    Raises:
        PaymentError (and its subclasses) on failure.
    """
    # First validate the payment method
    is_valid, validation_message = validate_payment_method(payment_method, payment_details)
    if not is_valid:
        raise InvalidPaymentMethodError()

    # Simulate success or a specific failure mode
    outcome = random.choices(
        ['success', 'declined', 'invalid', 'funds', 'timeout', 'generic'],
        weights=[75, 8, 5, 5, 4, 3],  # Higher success rate for demo
        k=1
    )[0]

    if outcome == 'success':
        return f"Payment successful! Transaction ID: TRN-{random.randint(100000, 999999)}"
    elif outcome == 'declined':
        raise CardDeclinedError(reason="General decline, contact bank.")
    elif outcome == 'invalid':
        raise InvalidPaymentMethodError()
    elif outcome == 'funds':
        raise InsufficientFundsError()
    elif outcome == 'timeout':
        raise NetworkTimeoutError()
    elif outcome == 'generic':
        # Simulate an unexpected server-side or unhandled error
        raise PaymentError(
            message="An unexpected error occurred processing the transaction.",
            code="P001_SERVER_FAIL"
        )
    else:
        # Should not happen, but good practice to handle all paths
        raise PaymentError("Unknown simulation outcome.")

def handle_payment_error(error: Exception) -> tuple[str, str, str]:
    """
    Handle payment errors and return appropriate user messages and actions.
    
    Returns:
        Tuple of (error_type, user_message, suggested_action)
    """
    if isinstance(error, InsufficientFundsError):
        return (
            "critical",
            "Payment declined due to insufficient funds.",
            "Please use a different card or check your account balance."
        )
    elif isinstance(error, CardDeclinedError):
        return (
            "warning", 
            f"Card was declined: {error.message}",
            "Please verify your card details or contact your bank."
        )
    elif isinstance(error, InvalidPaymentMethodError):
        return (
            "danger",
            "Invalid payment details provided.",
            "Please check your card number, expiry date, and CVV."
        )
    elif isinstance(error, NetworkTimeoutError):
        return (
            "info",
            "Connection timeout occurred.",
            "Please try again. If the problem persists, contact support."
        )
    elif isinstance(error, PaymentError):
        return (
            "danger",
            f"Payment error: {error.message}",
            "Please contact support with error code: " + error.code
        )
    else:
        return (
            "danger",
            "An unexpected error occurred.",
            "Please contact support for assistance."
        )

# =============================================================================
# CARD TYPE DETECTION
# =============================================================================

def detect_card_type(card_number: str) -> str:
    """
    Detect the card type based on the card number prefix.
    
    Args:
        card_number: The credit card number
        
    Returns:
        String indicating the card type
    """
    # Clean the card number
    cleaned_number = ''.join(filter(str.isdigit, card_number))
    
    if not cleaned_number:
        return "Unknown"
    
    # Card type detection based on prefixes
    if cleaned_number.startswith('4'):
        return "Visa"
    elif cleaned_number.startswith(('51', '52', '53', '54', '55')) or cleaned_number.startswith(tuple(str(i) for i in range(2221, 2721))):
        return "Mastercard"
    elif cleaned_number.startswith(('34', '37')):
        return "American Express"
    elif cleaned_number.startswith('6011') or cleaned_number.startswith(tuple(str(i) for i in range(644, 650))) or cleaned_number.startswith('65'):
        return "Discover"
    else:
        return "Unknown"