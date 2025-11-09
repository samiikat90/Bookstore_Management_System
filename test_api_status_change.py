#!/usr/bin/env python3
"""
Test the order status change API directly to verify notifications work
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app import app, db, Purchase

def test_api_status_change():
	"""Test the API status change route with proper debugging."""
	with app.test_client() as client:
		with app.app_context():
			print("Testing API Status Change with Notifications")
			print("=" * 55)
			
			# Get a recent order
			order = Purchase.query.order_by(Purchase.id.desc()).first()
			if not order:
				print("No orders found to test with!")
				return
			
			print(f"Testing with Order #{order.id}")
			print(f"Customer: {order.customer_name}")
			print(f"Current Status: {order.status}")
			
			# Test the API endpoint directly
			old_status = order.status
			new_status = "Processing" if old_status != "Processing" else "Confirmed"
			
			print(f"\\nAttempting to change status: {old_status} → {new_status}")
			
			# Note: This will require authentication, so it won't work without login
			# But we can see what the endpoint expects
			
			response = client.post(
				f'/api/update_order/purchase/{order.id}',
				data={'status': new_status},
				content_type='application/x-www-form-urlencoded'
			)
			
			print(f"Response status: {response.status_code}")
			print(f"Response data: {response.get_data(as_text=True)}")
			
			if response.status_code == 401:
				print("\\n[WARNING] Expected: Authentication required for API endpoint")
				print("This confirms the route exists and requires login")
			elif response.status_code == 200:
				print("\\n[SUCCESS] Status change successful!")
				print("Check the Flask console for admin notification logs")
			else:
				print(f"\\n[ERROR] Unexpected response: {response.status_code}")

if __name__ == "__main__":
	test_api_status_change()