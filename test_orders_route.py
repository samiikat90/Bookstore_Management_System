#!/usr/bin/env python3
"""
Test the orders_view route to see if it returns orders
"""
import requests
import re

def test_orders_route():
	print("[DEBUG] TESTING ORDERS_VIEW ROUTE")
	print("=" * 40)
	
	session = requests.Session()
	base_url = "http://127.0.0.1:5000"
	
	try:
		# Step 1: Login as admin
		print("1. Logging in as admin...")
		login_response = session.get(f"{base_url}/login")
		csrf_match = re.search(r'name="csrf_token" value="([^"]*)"', login_response.text)
		
		if csrf_match:
			csrf_token = csrf_match.group(1)
			login_data = {
				'username': 'admin',
				'password': 'admin123',
				'csrf_token': csrf_token
			}
			
			login_result = session.post(f"{base_url}/login", data=login_data)
			print(f" Login result: {login_result.status_code}")
			
			if login_result.status_code == 200 or "Admin Dashboard" in login_result.text:
				print(" [SUCCESS] Login successful")
				
				# Step 2: Test orders_view route
				print("\n2. Testing /orders route...")
				orders_response = session.get(f"{base_url}/orders")
				print(f" Orders page status: {orders_response.status_code}")
				
				if orders_response.status_code == 200:
					# Check if the page shows orders or "No orders" message
					if "No orders have been placed yet" in orders_response.text:
						print(" [ERROR] Page shows 'No orders have been placed yet'")
					elif "Customer Orders" in orders_response.text:
						print(" [SUCCESS] Orders page loaded successfully")
						# Count how many order rows are displayed
						order_rows = orders_response.text.count('<tr>') - 1 # Subtract header row
						print(f" Estimated orders displayed: {order_rows}")
					else:
						print(" [WARNING] Unexpected page content")
						print(" First 500 chars:", orders_response.text[:500])
				else:
					print(f" [ERROR] Failed to load orders page: {orders_response.status_code}")
			else:
				print(f" [ERROR] Login failed: {login_result.status_code}")
	
	except Exception as e:
		print(f"[ERROR] Error: {e}")

if __name__ == "__main__":
 test_orders_route()