#!/usr/bin/env python3
"""
Test to check admin user attributes and session status
"""
import requests
import re

def check_admin_status():
	print("[DEBUG] ADMIN STATUS DEBUG TEST")
	print("=" * 30)
	
	session = requests.Session()
	base_url = "http://127.0.0.1:5000"
	
	try:
		# Step 1: Login
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
			
			login_result = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
			print(f" Login result: {login_result.status_code}")
		
			if login_result.status_code == 302:
				redirect_location = login_result.headers.get('Location', '')
				print(f" Redirect location: {redirect_location}")
			
			# Step 2: Try to access admin dashboard (should work if admin)
			print("\n2. Testing admin dashboard access...")
			dashboard_response = session.get(f"{base_url}/admin_dashboard")
			print(f" Dashboard status: {dashboard_response.status_code}")
			
			if dashboard_response.status_code == 200:
				print(" [SUCCESS] Admin dashboard accessible - user IS a manager")
			elif dashboard_response.status_code == 302:
				print(" [ERROR] Redirected - user NOT a manager or session issue")
			else:
				print(f" [WARNING] Unexpected status: {dashboard_response.status_code}")
			
			# Step 3: Check what happens with all_orders
			print("\n3. Testing all_orders access...")
			orders_response = session.get(f"{base_url}/all_orders", allow_redirects=False)
			print(f" All_orders status: {orders_response.status_code}")
			
			if orders_response.status_code == 200:
				print(" [SUCCESS] All_orders page accessible")
			elif orders_response.status_code == 302:
				redirect_loc = orders_response.headers.get('Location', '')
				print(f" [ERROR] Redirected to: {redirect_loc}")
				if 'login' in redirect_loc:
					print(" [ERROR] Being redirected to login - authentication issue")
			else:
				print(f" [WARNING] Unexpected status: {orders_response.status_code}")
			
			# Step 4: Try other manager routes
			print("\n4. Testing other manager routes...")
			test_routes = ['/admin_users', '/inventory', '/purchases']
			for route in test_routes:
				response = session.get(f"{base_url}{route}", allow_redirects=False)
				status = "[SUCCESS] Accessible" if response.status_code == 200 else f"[ERROR] {response.status_code}"
				print(f" {route}: {status}")
		
		else:
			print(" [ERROR] Login failed")
	
	except Exception as e:
		print(f"[ERROR] Error: {e}")

if __name__ == "__main__":
 check_admin_status()