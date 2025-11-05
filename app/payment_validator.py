"""
Payment Method Validator Module

This module provides validation functions for different payment methods
including credit cards (using Luhn algorithm), PayPal email validation,
and bank transfer details validation.
"""

import re


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


def get_card_type(card_number: str) -> str:
    """
    Determine the credit card type based on the card number.
    """
    # Clean the input
    digits = ''.join(filter(str.isdigit, card_number))
    
    if not digits:
        return "Unknown"
    
    # Card type detection patterns
    if digits.startswith('4'):
        return "Visa"
    elif digits.startswith(('51', '52', '53', '54', '55')) or digits.startswith(('2221', '2222', '2223', '2224', '2225', '2226', '2227', '2228', '2229', '223', '224', '225', '226', '227', '228', '229', '23', '24', '25', '26', '270', '271', '2720')):
        return "Mastercard"
    elif digits.startswith(('34', '37')):
        return "American Express"
    elif digits.startswith('6011') or digits.startswith(('644', '645', '646', '647', '648', '649')) or digits.startswith('65'):
        return "Discover"
    else:
        return "Unknown"


def validate_payment_method(method_type: str, details: dict) -> dict:
    """
    Central function to validate different payment methods based on type.

    Args:
        method_type: The type of payment method ('credit_card', 'paypal', 'bank_transfer').
        details: A dictionary containing method-specific details.

    Returns:
        Dictionary with validation results including 'valid' (bool), 'message' (str), and 'card_type' (str, if applicable).
    """
    method_type = method_type.lower().strip()

    if method_type == 'credit_card':
        card_num = details.get('number', '').strip()
        expiry = details.get('expiry', '').strip()
        cvv = details.get('cvv', '').strip()
        cardholder_name = details.get('name', '').strip()

        # Check required fields
        if not card_num or not expiry or not cvv or not cardholder_name:
            return {
                'valid': False,
                'message': 'Credit Card requires card number, expiry date, CVV, and cardholder name.',
                'card_type': 'Unknown'
            }

        # Basic format checks
        if not re.match(r'^\d{2}/\d{2}$', expiry):
            return {
                'valid': False,
                'message': f'Invalid expiry format: {expiry}. Expected MM/YY format.',
                'card_type': get_card_type(card_num)
            }

        if not re.match(r'^\d{3,4}$', cvv):
            return {
                'valid': False,
                'message': f'Invalid CVV format: {cvv}. Expected 3 or 4 digits.',
                'card_type': get_card_type(card_num)
            }

        # Validate cardholder name (basic check)
        if not re.match(r'^[a-zA-Z\s]{2,50}$', cardholder_name):
            return {
                'valid': False,
                'message': 'Invalid cardholder name. Only letters and spaces allowed (2-50 characters).',
                'card_type': get_card_type(card_num)
            }

        # Luhn check (The primary number validation)
        card_type = get_card_type(card_num)
        if not luhn_check(card_num):
            return {
                'valid': False,
                'message': 'Credit card number failed validation check.',
                'card_type': card_type
            }

        return {
            'valid': True,
            'message': f'Valid {card_type} credit card.',
            'card_type': card_type
        }

    elif method_type == 'paypal':
        email = details.get('email', '').strip()
        if not email:
            return {
                'valid': False,
                'message': 'PayPal requires email address.'
            }

        if validate_email(email):
            return {
                'valid': True,
                'message': f'Valid PayPal email: {email}'
            }
        else:
            return {
                'valid': False,
                'message': f'Invalid PayPal email format: {email}'
            }

    elif method_type == 'bank_transfer':
        # Simple placeholder for bank details (e.g., routing/account number)
        routing = details.get('routing_number', '').strip()
        account = details.get('account_number', '').strip()
        bank_name = details.get('bank_name', '').strip()

        if not routing or not account or not bank_name:
            return {
                'valid': False,
                'message': 'Bank Transfer requires routing number, account number, and bank name.'
            }

        if not (routing.isdigit() and len(routing) == 9):
            return {
                'valid': False,
                'message': 'Invalid routing number format. Must be 9 digits.'
            }

        if not (account.isdigit() and 8 <= len(account) <= 17):
            return {
                'valid': False,
                'message': 'Invalid account number format. Must be 8-17 digits.'
            }

        if not re.match(r'^[a-zA-Z\s&]{2,50}$', bank_name):
            return {
                'valid': False,
                'message': 'Invalid bank name format.'
            }

        return {
            'valid': True,
            'message': 'Valid bank transfer details.'
        }

    else:
        return {
            'valid': False,
            'message': f'Unknown payment method type: {method_type}'
        }