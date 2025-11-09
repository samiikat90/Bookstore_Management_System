#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app import app, db, Purchase
from datetime import datetime, timedelta

def check_recent_orders():
	"""Check recent orders to see if checkout is actually working."""
	with app.app_context():
		print("Checking Recent Orders and Checkout Activity")
		print("=" * 50)
		
		# Get all purchases from the last 24 hours
		yesterday = datetime.utcnow() - timedelta(days=1)
		recent_purchases = Purchase.query.filter(Purchase.timestamp >= yesterday).all()
		
		print(f"Recent purchases (last 24 hours): {len(recent_purchases)}")
		
		if recent_purchases:
			print("\\nRecent orders:")
			for purchase in recent_purchases[-10:]:  # Show last 10
				print(f" ID: {purchase.id}, Customer: {purchase.customer_name}, "
				      f"Book: {purchase.book_isbn}, Status: {purchase.status}, "
				      f"Date: {purchase.timestamp}")
		
		# Get all purchases regardless of date
		all_purchases = Purchase.query.order_by(Purchase.timestamp.desc()).limit(20).all()
		print(f"\\nTotal purchases in database: {Purchase.query.count()}")
		print("\\nLast 20 orders (any date):")
		
		for purchase in all_purchases:
			print(f" ID: {purchase.id}, Customer: {purchase.customer_name}, "
			      f"Book: {purchase.book_isbn}, Status: {purchase.status}, "
			      f"Date: {purchase.timestamp}")
		
		# Check order status distribution
		print("\\n=== Order Status Distribution ===")
		statuses = db.session.query(Purchase.status, db.func.count(Purchase.status)).group_by(Purchase.status).all()
		for status, count in statuses:
			print(f" {status}: {count} orders")
		
		# Check if there are any orders with recent timestamps that might not have sent notifications
		print("\\n=== Checking for orders that might have missed admin notifications ===")
		pending_orders = Purchase.query.filter(Purchase.status.in_(['Pending', 'Confirmed'])).all()
		print(f"Orders in Pending/Confirmed status: {len(pending_orders)}")
		
		if len(pending_orders) > 0:
			print("These orders should have triggered admin notifications:")
			for order in pending_orders:
				print(f" ID: {order.id}, Customer: {order.customer_name}, "
				      f"Status: {order.status}, Date: {order.timestamp}")

if __name__ == "__main__":
 check_recent_orders()