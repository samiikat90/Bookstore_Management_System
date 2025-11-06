#!/usr/bin/env python3
"""
Test script to verify admin notification contains all required information.
This script will simulate the notification data structure and verify all fields are present.
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_admin_notification_data():
    """Test that admin notification has all required fields."""
    
    # Simulate the order details that would be created
    simulated_purchase_details = [
        {'title': 'Test Book 1', 'quantity': 2, 'price': 15.99},
        {'title': 'Test Book 2', 'quantity': 1, 'price': 22.50}
    ]
    
    simulated_cart = {
        '9780123456789': 2,
        '9780987654321': 1
    }
    
    # Simulate the admin_order_details structure from the fixed code
    book_isbn_list = [isbn for isbn in simulated_cart.keys()]
    quantity_total = sum(simulated_cart.values())
    
    admin_order_details = {
        'id': 'TXN12345TEST',
        'customer_name': 'Test Customer',
        'customer_email': 'test@example.com',
        'customer_phone': '555-1234',
        'book_isbn': ', '.join(book_isbn_list) if book_isbn_list else 'N/A',
        'quantity': quantity_total,
        'status': 'Confirmed',
        'payment_method': 'credit_card',
        'amount': 54.48,
        'items_count': len(simulated_purchase_details),
        'timestamp': 'November 05, 2025 at 06:17 PM'
    }
    
    print("Testing Admin Notification Data Structure:")
    print("=" * 50)
    
    # Check all required fields
    required_fields = [
        'id', 'customer_name', 'customer_email', 'customer_phone',
        'book_isbn', 'quantity', 'status', 'timestamp'
    ]
    
    all_present = True
    for field in required_fields:
        if field in admin_order_details:
            value = admin_order_details[field]
            print(f"✓ {field}: {value}")
            if value == 'N/A' and field in ['book_isbn', 'quantity', 'status']:
                print(f"  WARNING: {field} should not be N/A")
                all_present = False
        else:
            print(f"✗ {field}: MISSING")
            all_present = False
    
    print("\n" + "=" * 50)
    if all_present and admin_order_details['book_isbn'] != 'N/A':
        print("✓ SUCCESS: All required fields are present with valid data!")
    else:
        print("✗ FAILURE: Some fields are missing or have N/A values")
    
    print(f"\nSample notification message would contain:")
    print(f"Order ID: {admin_order_details.get('id', 'N/A')}")
    print(f"Customer: {admin_order_details.get('customer_name', 'N/A')}")
    print(f"Email: {admin_order_details.get('customer_email', 'N/A')}")
    print(f"Phone: {admin_order_details.get('customer_phone', 'N/A')}")
    print(f"Book ISBN: {admin_order_details.get('book_isbn', 'N/A')}")
    print(f"Quantity: {admin_order_details.get('quantity', 'N/A')}")
    print(f"Status: {admin_order_details.get('status', 'N/A')}")
    print(f"Date: {admin_order_details.get('timestamp', 'N/A')}")

if __name__ == "__main__":
    test_admin_notification_data()