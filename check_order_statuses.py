#!/usr/bin/env python3

"""
Check all order statuses in the database to see what orders need attention
"""

import os
import sys

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app import app, db, Purchase

def check_order_statuses():
	"""Check all order statuses and their counts"""
	print("=== Order Status Analysis ===")
	
	with app.app_context():
		# Get all unique statuses
		statuses = db.session.query(Purchase.status).distinct().all()
		print(f"All order statuses in database: {[s[0] for s in statuses]}")
		
		print("\n=== Order Counts by Status ===")
		for status_tuple in statuses:
			status = status_tuple[0]
			count = Purchase.query.filter_by(status=status).count()
			print(f"{status}: {count} orders")
		
		print("\n=== Current 'Pending' Orders ===")
		pending_orders = Purchase.query.filter_by(status='Pending').all()
		print(f"Pending orders count: {len(pending_orders)}")
		for order in pending_orders:
			print(f"- Order ID {order.id}: {order.customer_name} - {order.book_isbn} - {order.timestamp}")
		
		print("\n=== Orders That Might Need Attention ===")
		# Orders that typically need attention: Pending, Processing, maybe others
		attention_statuses = ['Pending', 'Processing', 'Confirmed']
		total_needing_attention = 0
		
		for status in attention_statuses:
			count = Purchase.query.filter_by(status=status).count()
			if count > 0:
				total_needing_attention += count
				print(f"{status}: {count} orders")
				orders = Purchase.query.filter_by(status=status).all()
				for order in orders:
					print(f" - Order {order.id}: {order.customer_name} ({order.timestamp})")
		
		print(f"\nTotal orders needing attention: {total_needing_attention}")
		
		print("\n=== Current Dashboard Count ===")
		current_pending = Purchase.query.filter_by(status='Pending').count()
		print(f"Current dashboard 'Pending' count: {current_pending}")

if __name__ == "__main__":
 check_order_statuses()