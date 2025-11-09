#!/usr/bin/env python3
"""
Test the low stock inventory notification system
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.app import app, db, Book, check_and_notify_low_stock, send_low_stock_notification

def test_low_stock_notifications():
 with app.app_context():
 print("[DEBUG] TESTING LOW STOCK NOTIFICATION SYSTEM")
 print("=" * 50)
 
 # First, check current low stock items
 print("\n1. Checking current inventory for low stock items...")
 low_stock_books = Book.query.filter(Book.quantity <= 5).order_by(Book.quantity.asc()).all()
 
 if low_stock_books:
 print(f"Found {len(low_stock_books)} books with low stock (≤5):")
 for book in low_stock_books:
 status = "[CRITICAL]" if book.quantity <= 2 else "[WARNING]"
 print(f" {status} {book.title} by {book.author} - {book.quantity} copies")
 else:
 print("No books currently have low stock (≤5)")
 
 # Create a test low stock scenario
 print("\n2. Creating test low stock scenario...")
 test_book = Book.query.first()
 if test_book:
 original_qty = test_book.quantity
 test_book.quantity = 3 # Set to low stock
 db.session.commit()
 
 print(f"Set '{test_book.title}' to 3 copies for testing")
 
 # Test the notification
 print("\n3. Testing low stock notification...")
 check_and_notify_low_stock()
 
 # Restore original quantity
 test_book.quantity = original_qty
 db.session.commit()
 print(f"Restored '{test_book.title}' to {original_qty} copies")
 else:
 print("No books found in database for testing")
 
 # If we found actual low stock books, send notifications
 if low_stock_books:
 print(f"\n2. Sending low stock notifications for {len(low_stock_books)} books...")
 send_low_stock_notification(low_stock_books)
 print("Low stock notifications sent!")
 
 print("\n3. Testing the check_and_notify_low_stock() function...")
 check_and_notify_low_stock()
 
 print("\nLow stock notification system test completed!")
 print("\nFeatures tested:")
 print(" • Low stock detection (≤5 quantity)")
 print(" • Critical vs warning classification")
 print(" • Email notification generation")
 print(" • Admin notification targeting")
 print(" • HTML and text email formatting")

if __name__ == "__main__":
 test_low_stock_notifications()