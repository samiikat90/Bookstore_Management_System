#!/usr/bin/env python3
"""
Test script to verify discount code messaging
"""

# Test the discount code logic
def test_discount_messaging():
    # WINTER30 requires $75 minimum for 30% off
    DISCOUNT_CODES = {
        'SAVE10': [0.10, 30.0],   # 10% off orders over $30
        'BOOK20': [0.20, 50.0],   # 20% off orders over $50
        'FALL25': [0.25, 100.0],  # 25% off orders over $100
        'STUDENT15': [0.15, 25.0], # 15% off orders over $25
        'WINTER30': [0.30, 75.0]   # 30% off orders over $75
    }
    
    # Test WINTER30 with insufficient order
    code = 'WINTER30'
    subtotal = 45.00  # Less than $75 required
    
    if code in DISCOUNT_CODES:
        discount_rate, min_order = DISCOUNT_CODES[code]
        if subtotal < min_order:
            remaining_amount = min_order - subtotal
            message = f"The discount code '{code}' requires a minimum order of ${min_order:.2f}. Your current subtotal is ${subtotal:.2f}. Please add ${remaining_amount:.2f} more to your cart to use this code."
            print("ERROR MESSAGE:")
            print(message)
            print()
            
        # Test with sufficient order
        subtotal_sufficient = 80.00
        if subtotal_sufficient >= min_order:
            discount_amount = subtotal_sufficient * discount_rate
            success_message = f"Success! Discount code '{code}' applied - {int(discount_rate*100)}% off (You saved ${discount_amount:.2f}!)"
            print("SUCCESS MESSAGE:")
            print(success_message)
            print()
    
    print("Available Discount Codes:")
    for code, (rate, minimum) in DISCOUNT_CODES.items():
        print(f"  {code}: {int(rate*100)}% off orders over ${minimum:.2f}")

if __name__ == "__main__":
    test_discount_messaging()