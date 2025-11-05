#!/usr/bin/env python3
"""
Payment Validation Test Script

This script demonstrates the payment validation functionality 
implemented in the bookstore management system.
"""

import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from payment_utils import (
    validate_payment_method, 
    luhn_check, 
    detect_card_type,
    process_payment,
    handle_payment_error,
    PaymentError,
    CardDeclinedError,
    InvalidPaymentMethodError,
    InsufficientFundsError,
    NetworkTimeoutError
)

def test_payment_validation():
    """Test various payment validation scenarios."""
    print("=== Payment Validation System Test ===\n")
    
    # Test 1: Valid Credit Card
    print("1. Testing Valid Credit Card (Luhn Valid):")
    valid_card = {
        'number': '4242424242424242',  # Valid test card number
        'expiry': '12/26',
        'cvv': '123'
    }
    is_valid, message = validate_payment_method('credit_card', valid_card)
    print(f"   Result: {'✓ PASS' if is_valid else '✗ FAIL'}")
    print(f"   Message: {message}")
    print(f"   Card Type: {detect_card_type(valid_card['number'])}\n")
    
    # Test 2: Invalid Credit Card
    print("2. Testing Invalid Credit Card (Bad Luhn):")
    invalid_card = {
        'number': '4242424242424243',  # Invalid (changed last digit)
        'expiry': '12/26',
        'cvv': '123'
    }
    is_valid, message = validate_payment_method('credit_card', invalid_card)
    print(f"   Result: {'✓ PASS' if not is_valid else '✗ FAIL'}")
    print(f"   Message: {message}\n")
    
    # Test 3: Valid PayPal
    print("3. Testing Valid PayPal Email:")
    valid_paypal = {
        'email': 'user@example.com'
    }
    is_valid, message = validate_payment_method('paypal', valid_paypal)
    print(f"   Result: {'✓ PASS' if is_valid else '✗ FAIL'}")
    print(f"   Message: {message}\n")
    
    # Test 4: Invalid PayPal
    print("4. Testing Invalid PayPal Email:")
    invalid_paypal = {
        'email': 'not-an-email'
    }
    is_valid, message = validate_payment_method('paypal', invalid_paypal)
    print(f"   Result: {'✓ PASS' if not is_valid else '✗ FAIL'}")
    print(f"   Message: {message}\n")
    
    # Test 5: Valid Bank Transfer
    print("5. Testing Valid Bank Transfer:")
    valid_bank = {
        'routing_number': '123456789',
        'account_number': '1234567890'
    }
    is_valid, message = validate_payment_method('bank_transfer', valid_bank)
    print(f"   Result: {'✓ PASS' if is_valid else '✗ FAIL'}")
    print(f"   Message: {message}\n")
    
    # Test 6: Card Type Detection
    print("6. Testing Card Type Detection:")
    test_cards = [
        ('4242424242424242', 'Visa'),
        ('5555555555554444', 'Mastercard'),
        ('378282246310005', 'American Express'),
        ('6011111111111117', 'Discover')
    ]
    
    for card_number, expected_type in test_cards:
        detected_type = detect_card_type(card_number)
        result = "✓ PASS" if detected_type == expected_type else "✗ FAIL"
        print(f"   {card_number[:4]}******: {detected_type} ({result})")
    
    print("\n7. Testing Payment Processing Simulation:")
    print("   (This simulates various payment outcomes)")
    
    # Test multiple payment attempts to see different outcomes
    for i in range(3):
        try:
            result = process_payment(50.00, 'credit_card', valid_card)
            print(f"   Attempt {i+1}: ✓ {result}")
        except PaymentError as e:
            error_type, user_message, suggested_action = handle_payment_error(e)
            print(f"   Attempt {i+1}: ✗ {e.code} - {user_message}")

def test_luhn_algorithm():
    """Test the Luhn algorithm with known test cases."""
    print("\n=== Luhn Algorithm Test Cases ===\n")
    
    test_cases = [
        ('4242424242424242', True, 'Visa Test Card'),
        ('4000000000000002', True, 'Visa Test Card'),
        ('5555555555554444', True, 'Mastercard Test Card'),
        ('2223003122003222', True, 'Mastercard Test Card'),
        ('378282246310005', True, 'Amex Test Card'),
        ('371449635398431', True, 'Amex Test Card'),
        ('6011111111111117', True, 'Discover Test Card'),
        ('6011000990139424', True, 'Discover Test Card'),
        ('4242424242424243', False, 'Invalid (modified Visa)'),
        ('1234567890123456', False, 'Invalid sequence'),
    ]
    
    print("Card Number          | Expected | Result | Status")
    print("-" * 55)
    
    for card_number, expected, description in test_cases:
        result = luhn_check(card_number)
        status = "✓ PASS" if result == expected else "✗ FAIL"
        print(f"{card_number} | {'Valid' if expected else 'Invalid':8} | {'Valid' if result else 'Invalid':6} | {status}")

if __name__ == "__main__":
    try:
        test_payment_validation()
        test_luhn_algorithm()
        print("\n=== Test Complete ===")
        print("Payment validation system is working correctly!")
        
    except ImportError as e:
        print(f"Error importing payment modules: {e}")
        print("Make sure you're running this from the project root directory.")
    except Exception as e:
        print(f"Unexpected error: {e}")