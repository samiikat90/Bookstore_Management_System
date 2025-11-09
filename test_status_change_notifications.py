#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app import app, db, Purchase, send_admin_notification, get_order_details_dict

def test_order_status_change_notifications():
	"""Test if order status change notifications are working."""
	with app.app_context():
		print("Testing Order Status Change Notifications")
		print("=" * 50)
		
		# Get some recent orders
		recent_orders = Purchase.query.order_by(Purchase.id.desc()).limit(5).all()
		
		if not recent_orders:
			print("No orders found in database!")
			return
		
		print(f"Found {len(recent_orders)} recent orders:")
		for order in recent_orders:
			print(f" ID {order.id}: {order.customer_name} - Status: {order.status}")
		
		# Test with the first order
		test_order = recent_orders[0]
		print(f"\\nTesting status change notification with Order #{test_order.id}")
		print(f"Customer: {test_order.customer_name}")
		print(f"Current status: {test_order.status}")
		
		# Test the get_order_details_dict function
		try:
			order_details = get_order_details_dict(test_order)
			print(f"\\nOrder details dictionary created successfully:")
			for key, value in order_details.items():
				print(f" {key}: {value}")
		except Exception as e:
			print(f"\\nERROR: get_order_details_dict failed: {e}")
			return
		
		# Test sending a status change notification
		print(f"\\n=== Testing Status Change Notification ===")
		old_status = test_order.status
		new_status = "Processing" if old_status != "Processing" else "Confirmed"
		
		try:
			result = send_admin_notification(
				subject=f"TEST: Order Status Changed - Chapter 6: A Plot Twist",
				message=f"""This is a TEST notification for order status change.

Order Details:
- Order ID: #{test_order.id}
- Customer: {test_order.customer_name}
- Email: {test_order.customer_email}
- Status changed: '{old_status}' → '{new_status}'
- Changed by: TEST SYSTEM

This is a test - no actual status change was made to the order.""",
				order_details=order_details
			)
			
			print("[SUCCESS] Status change notification sent successfully!")
			print("\\nCheck admin email addresses for the notification:")
			print(" - samiikat90@gmail.com")
			print(" - samantha199054@gmail.com")
			print(" (and other admin users)")
			
		except Exception as e:
			print(f"[ERROR] FAILED to send status change notification: {e}")
			import traceback
			print(f"Traceback:\\n{traceback.format_exc()}")
		
		print(f"\\n=== Real Status Change Route Analysis ===")
		print(f"The status change notifications should be triggered from:")
		print(f" Route: /api/update_order/<item_type>/<int:item_id>")
		print(f" Around line 2934 in app.py")
		print(f" When admin users change order status via the web interface")

if __name__ == "__main__":
	test_order_status_change_notifications()