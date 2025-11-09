#!/usr/bin/env python3
"""
Clean debug test to check CSRF token in all_orders page
"""
import requests
import re

def test_csrf_token():
 print("[DEBUG] CSRF TOKEN DEBUG TEST")
 print("=" * 30)
 
 session = requests.Session()
 base_url = "http://127.0.0.1:5000"
 
 try:
 # Step 1: Login
 print("1. Getting login page...")
 login_response = session.get(f"{base_url}/login")
 
 csrf_match = re.search(r'name="csrf_token" value="([^"]*)"', login_response.text)
 if csrf_match:
 csrf_token = csrf_match.group(1)
 print(f" Login CSRF token: {csrf_token[:10]}...")
 
 # Login
 login_data = {
 'username': 'admin',
 'password': 'admin123',
 'csrf_token': csrf_token
 }
 
 login_result = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
 if login_result.status_code == 302:
 print(" [SUCCESS] Login successful!")
 
 # Step 2: Check all_orders page
 print("\n2. Checking all_orders page for CSRF meta tag...")
 orders_response = session.get(f"{base_url}/all_orders")
 
 if orders_response.status_code == 200:
 print(" [SUCCESS] All orders page loaded")
 
 # Check for CSRF meta tag
 if 'name="csrf-token"' in orders_response.text:
 print(" [SUCCESS] Found csrf-token meta tag")
 
 # Extract the content
 meta_match = re.search(r'<meta name="csrf-token" content="([^"]*)"', orders_response.text)
 if meta_match:
 token = meta_match.group(1)
 if token and token.strip():
 print(f" [SUCCESS] CSRF token content: {token[:10]}...")
 
 # Now test the API call
 print("\n3. Testing API call with CSRF token...")
 
 headers = {
 'Content-Type': 'application/x-www-form-urlencoded',
 'X-CSRFToken': token,
 'X-Requested-With': 'XMLHttpRequest'
 }
 
 data = 'status=Processing'
 
 api_response = session.post(
 f"{base_url}/api/update_order/purchase/1",
 headers=headers,
 data=data
 )
 
 print(f" API Status: {api_response.status_code}")
 print(f" API Response: {api_response.text}")
 
 if api_response.status_code == 200:
 print(" [SUCCESS] API call successful!")
 elif api_response.status_code == 404:
 print(" [WARNING] Order #1 not found (normal if no orders exist)")
 else:
 print(f" [ERROR] API call failed: {api_response.status_code}")
 
 else:
 print(" [ERROR] CSRF token is empty")
 # Show the actual meta tag
 meta_tag = re.search(r'<meta name="csrf-token"[^>]*>', orders_response.text)
 if meta_tag:
 print(f" Meta tag: {meta_tag.group(0)}")
 else:
 print(" [ERROR] Meta tag found but couldn't extract content")
 else:
 print(" [ERROR] No csrf-token meta tag found")
 # Show first few lines to debug
 lines = orders_response.text.split('\n')[:15]
 print(" First 15 lines of HTML:")
 for i, line in enumerate(lines, 1):
 print(f" {i:2}: {line[:80]}...")
 else:
 print(f" [ERROR] Cannot access all_orders: {orders_response.status_code}")
 else:
 print(f" [ERROR] Login failed: {login_result.status_code}")
 else:
 print(" [ERROR] No CSRF token found in login page")
 
 except Exception as e:
 print(f"[ERROR] Error: {e}")

if __name__ == "__main__":
 test_csrf_token()