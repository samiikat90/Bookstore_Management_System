#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app import app, send_admin_notification, send_admin_order_notification

def test_both_admin_functions():
 """Test both admin notification functions to see which one works."""
 with app.app_context():
 print("Testing Admin Notification Functions")
 print("=" * 50)
 
 # Test 1: send_admin_notification (simple text)
 print("\n=== Testing send_admin_notification (simple) ===")
 try:
 test_order_details = {
 'id': 'TEST-001',
 'customer_name': 'Test Customer',
 'customer_email': 'test@example.com',
 'customer_phone': '555-1234',
 'book_isbn': '9781234567890',
 'quantity': 2,
 'status': 'Pending',
 'timestamp': '2025-11-08 10:00:00'
 }
 
 send_admin_notification(
 subject="TEST: Simple Admin Notification",
 message="This is a test of the simple admin notification system.",
 order_details=test_order_details
 )
 print("send_admin_notification: Called successfully")
 except Exception as e:
 print(f"send_admin_notification: FAILED with error: {e}")
 
 # Test 2: send_admin_order_notification (rich HTML)
 print("\n=== Testing send_admin_order_notification (rich) ===")
 try:
 test_order_details = {
 'order_id': 'TEST-002',
 'customer_name': 'Test Customer 2',
 'customer_email': 'test2@example.com',
 'customer_phone': '555-5678',
 'customer_address': '123 Test St, Test City, TC 12345',
 'book_count': 3,
 'total_amount': 89.97,
 'status': 'Confirmed',
 'timestamp': '2025-11-08 10:30:00',
 'items': [
 {
 'title': 'Test Book 1',
 'author': 'Test Author 1',
 'isbn': '9781111111111',
 'price': 29.99,
 'quantity': 2
 },
 {
 'title': 'Test Book 2', 
 'author': 'Test Author 2',
 'isbn': '9782222222222',
 'price': 29.99,
 'quantity': 1
 }
 ]
 }
 
 result = send_admin_order_notification(test_order_details)
 print(f"send_admin_order_notification: Result = {result}")
 except Exception as e:
 print(f"send_admin_order_notification: FAILED with error: {e}")

if __name__ == "__main__":
 test_both_admin_functions()