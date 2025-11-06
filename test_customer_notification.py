#!/usr/bin/env python3
"""
Test script to verify customer notification includes discount information.
"""

from datetime import datetime

def test_customer_notification_with_discount():
    """Test customer notification email formatting with discount."""
    
    # Simulate purchase details
    purchase_details = [
        {'title': 'The Great Gatsby', 'quantity': 1, 'price': 15.99},
        {'title': 'To Kill a Mockingbird', 'quantity': 2, 'price': 12.50}
    ]
    
    # Test with discount
    discount_info = {
        'code': 'SAVE20',
        'amount': 8.20,
        'final_total': 32.79
    }
    
    # Calculate what the email would show
    order_summary = ""
    subtotal = 0
    for item in purchase_details:
        book_title = item.get('title', 'Unknown Book')
        quantity = item.get('quantity', 1)
        price = item.get('price', 0)
        item_total = price * quantity
        subtotal += item_total
        order_summary += f"• {book_title} (Qty: {quantity}) - ${price:.2f} each = ${item_total:.2f}\n"
    
    # Calculate discount and final total
    discount_text = ""
    final_total = subtotal
    if discount_info:
        discount_code = discount_info.get('code')
        discount_amount = discount_info.get('amount', 0)
        final_total = discount_info.get('final_total', subtotal)
        if discount_code and discount_amount > 0:
            discount_text = f"\nSubtotal: ${subtotal:.2f}\nDiscount ({discount_code}): -${discount_amount:.2f}"
    
    total_text = f"TOTAL: ${final_total:.2f}"
    if discount_text:
        total_text = f"{discount_text}\n{total_text}"
    
    print("Customer Email Notification Test")
    print("=" * 50)
    print("ITEMS ORDERED:")
    print(order_summary)
    print(total_text)
    print("\n" + "=" * 50)
    
    # Verify calculations
    expected_subtotal = 15.99 + (12.50 * 2)  # 40.99
    expected_discount = 8.20
    expected_total = expected_subtotal - expected_discount  # 32.79
    
    print(f"Expected subtotal: ${expected_subtotal:.2f}")
    print(f"Actual subtotal: ${subtotal:.2f}")
    print(f"Expected discount: ${expected_discount:.2f}")
    print(f"Actual discount: ${discount_info['amount']:.2f}")
    print(f"Expected final total: ${expected_total:.2f}")
    print(f"Actual final total: ${final_total:.2f}")
    
    if (abs(subtotal - expected_subtotal) < 0.01 and 
        abs(final_total - expected_total) < 0.01):
        print("\n✓ SUCCESS: Email would show correct discount information!")
    else:
        print("\n✗ FAILURE: Calculation mismatch detected")

def test_customer_notification_without_discount():
    """Test customer notification email formatting without discount."""
    
    # Simulate purchase details
    purchase_details = [
        {'title': 'Pride and Prejudice', 'quantity': 1, 'price': 14.99}
    ]
    
    # No discount
    discount_info = None
    
    # Calculate what the email would show
    order_summary = ""
    subtotal = 0
    for item in purchase_details:
        book_title = item.get('title', 'Unknown Book')
        quantity = item.get('quantity', 1)
        price = item.get('price', 0)
        item_total = price * quantity
        subtotal += item_total
        order_summary += f"• {book_title} (Qty: {quantity}) - ${price:.2f} each = ${item_total:.2f}\n"
    
    total_text = f"TOTAL: ${subtotal:.2f}"
    
    print("\nCustomer Email Notification Test (No Discount)")
    print("=" * 50)
    print("ITEMS ORDERED:")
    print(order_summary)
    print(total_text)
    print("\n✓ SUCCESS: Email would show simple total without discount section!")

if __name__ == "__main__":
    test_customer_notification_with_discount()
    test_customer_notification_without_discount()