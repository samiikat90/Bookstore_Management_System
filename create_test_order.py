#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app import app, db, Book, Customer, User, Purchase
from app import send_admin_order_notification, send_admin_notification

def create_test_order():
 """Create a test order and trigger admin notifications to see if they work."""
 with app.app_context():
 print("Creating Test Order and Triggering Admin Notifications")
 print("=" * 60)
 
 # Check if we have any books in the database
 books = Book.query.limit(3).all()
 if not books:
 print("No books found in database! Please add some books first.")
 return False
 
 print(f"Found {len(books)} books in database:")
 for book in books:
 print(f" - {book.title} by {book.author} (${book.price})")
 
 # Check if we have any customers
 customers = Customer.query.limit(2).all()
 if not customers:
 print("No customers found in database!")
 return False
 
 customer = customers[0]
 print(f"\\nUsing customer: {customer.full_name or 'Unknown'}")
 
 # Create a test order manually
 try:
 # Simulate purchase details 
 purchase_details = []
 total_amount = 0
 
 for i, book in enumerate(books[:2]): # Use first 2 books
 quantity = i + 1 # 1, 2 quantities
 subtotal = book.price * quantity
 total_amount += subtotal
 
 purchase_details.append({
 'title': book.title,
 'author': book.author,
 'isbn': book.isbn,
 'price': book.price,
 'quantity': quantity
 })
 
 # Create a Purchase record
 purchase = Purchase(
 customer_name=customer.full_name or "Test Customer",
 customer_email=customer.email,
 book_isbn=book.isbn,
 quantity=quantity,
 status="Pending"
 )
 db.session.add(purchase)
 
 db.session.commit()
 print(f"\\nCreated test order with total: ${total_amount:.2f}")
 
 # Now test admin notifications
 print("\\n=== Testing Admin Notification (Rich HTML) ===")
 admin_order_details = {
 'order_id': f'TEST-{purchase.id}',
 'customer_name': customer.full_name or 'Test Customer',
 'customer_email': customer.email,
 'customer_phone': 'N/A',
 'customer_address': 'Test Address',
 'book_count': len(purchase_details),
 'total_amount': total_amount,
 'status': 'Pending',
 'timestamp': '2025-11-08 10:30:00',
 'items': purchase_details
 }
 
 result = send_admin_order_notification(admin_order_details)
 print(f"Rich HTML admin notification result: {result}")
 
 print("\\n=== Testing Simple Admin Notification ===")
 order_summary = ""
 for item in purchase_details:
 order_summary += f"- {item['title']} by {item['author']} (Qty: {item['quantity']}) @ ${item['price']:.2f}\\n"
 
 message = f"""A new test order has been placed!

Customer: {customer.full_name or 'Test Customer'}
Email: {customer.email}
Total: ${total_amount:.2f}

Items:
{order_summary}

This is a test order to verify admin notifications are working."""
 
 send_admin_notification(
 subject=f"TEST ORDER - Admin Notification Test - ${total_amount:.2f}",
 message=message,
 order_details={
 'id': f'TEST-{purchase.id}',
 'customer_name': customer.full_name or 'Test Customer',
 'customer_email': customer.email,
 'status': 'Pending'
 }
 )
 print("Simple admin notification sent")
 
 return True
 
 except Exception as e:
 print(f"Error creating test order: {e}")
 db.session.rollback()
 return False

if __name__ == "__main__":
 create_test_order()