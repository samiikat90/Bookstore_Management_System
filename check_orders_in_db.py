#!/usr/bin/env python3
"""
Quick check to see what orders exist in the database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.app import app, db, Purchase, User, Book

def check_orders():
 with app.app_context():
 print("[DEBUG] CHECKING ORDERS IN DATABASE")
 print("=" * 40)
 
 # Check total orders
 total_orders = Purchase.query.count()
 print(f"Total orders in database: {total_orders}")
 
 if total_orders > 0:
 print("\n ORDER DETAILS:")
 orders = Purchase.query.order_by(Purchase.timestamp.desc()).all()
 
 for i, order in enumerate(orders[:10]): # Show first 10
 print(f" {i+1}. Order #{order.id}")
 print(f" Customer: {order.customer_name}")
 print(f" Email: {order.customer_email}")
 print(f" Book ISBN: {order.book_isbn}")
 print(f" Status: {order.status}")
 print(f" Quantity: {order.quantity}")
 # Check if order has total attribute
 total_str = f"${order.total:.2f}" if hasattr(order, 'total') and order.total else "N/A"
 print(f" Total: {total_str}")
 print(f" Date: {order.timestamp}")
 print()
 
 if total_orders > 10:
 print(f" ... and {total_orders - 10} more orders")
 
 # Check status breakdown
 print("\n[STATS] STATUS BREAKDOWN:")
 statuses = ['Pending', 'Confirmed', 'Processing', 'Shipped', 'Completed', 'Cancelled']
 for status in statuses:
 count = Purchase.query.filter_by(status=status).count()
 if count > 0:
 print(f" {status}: {count}")
 else:
 print("[ERROR] No orders found in database!")
 print("\nLet's check if we have customers and books:")
 
 # Check customers
 customer_count = User.query.filter_by(is_manager=False).count()
 print(f"Customers in database: {customer_count}")
 
 # Check books
 book_count = Book.query.count()
 print(f"Books in database: {book_count}")
 
 if customer_count == 0:
 print("[WARNING] No customers found - this might be why no orders exist")
 if book_count == 0:
 print("[WARNING] No books found - this might be why no orders exist")

if __name__ == "__main__":
 check_orders()