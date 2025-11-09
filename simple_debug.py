#!/usr/bin/env python3
"""
Simple debug test to check the AJAX endpoint directly
"""
import requests
import json
import re

def test_ajax_simple():
 print("[DEBUG] SIMPLE AJAX DEBUG TEST")
 print("=" * 30)
 
 session = requests.Session()
 base_url = "http://127.0.0.1:5000"
 
 try:
 # Step 1: Try to access the API endpoint directly without login
 print("1. Testing API endpoint without authentication...")
 
 headers = {
 'Content-Type': 'application/x-www-form-urlencoded',
 'X-CSRFToken': 'test-token',
 'X-Requested-With': 'XMLHttpRequest'
 }
 
 data = 'status=Processing'
 
 response = session.post(
 f"{base_url}/api/update_order/purchase/1",
 headers=headers,
 data=data
 )
 
 print(f" Status Code: {response.status_code}")
 print(f" Content-Type: {response.headers.get('content-type', 'unknown')}")
 print(f" Response: {response.text[:200]}...")
 
 # Step 2: Check if it's an HTML redirect
 if '<html' in response.text.lower() or '<!doctype' in response.text.lower():
 print(" [SUCCESS] Response is HTML (likely redirect to login)")
 
 # Look for redirect URL
 if 'login' in response.text.lower():
 print(" [SUCCESS] Confirmed: Redirecting to login page")
 
 elif response.headers.get('content-type', '').startswith('application/json'):
 print(" [SUCCESS] Response is JSON")
 try:
 json_data = response.json()
 print(f" JSON Data: {json_data}")
 except:
 print(" [ERROR] Invalid JSON")
 else:
 print(f" [WARNING] Unexpected response type")
 
 # Step 3: Simple login attempt
 print("\n2. Attempting simple login...")
 login_response = session.get(f"{base_url}/login")
 print(f" Login page status: {login_response.status_code}")
 
 # Extract CSRF token with regex
 csrf_match = re.search(r'name="csrf_token" value="([^"]*)"', login_response.text)
 if csrf_match:
 csrf_token = csrf_match.group(1)
 print(f" Found CSRF token: {csrf_token[:10]}...")
 
 # Try login
 login_data = {
 'username': 'admin',
 'password': 'admin123',
 'csrf_token': csrf_token
 }
 
 login_result = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
 print(f" Login attempt: {login_result.status_code}")
 
 if login_result.status_code == 302:
 print(" [SUCCESS] Login successful!")
 
 # Now try the API call again
 print("\n3. Retrying API call after login...")
 
 # Get page with meta CSRF token
 all_orders_response = session.get(f"{base_url}/all_orders")
 if all_orders_response.status_code == 200:
 print(f" All orders page loaded successfully")
 
 # Look for the exact CSRF meta tag
 if 'name="csrf-token"' in all_orders_response.text:
 print(" [SUCCESS] CSRF meta tag found in HTML")
 # Look for CSRF meta tag content
 csrf_meta_match = re.search(r'<meta name="csrf-token" content="([^"]*)"', all_orders_response.text)
 if csrf_meta_match:
 meta_csrf = csrf_meta_match.group(1)
 print(f" Found meta CSRF: {meta_csrf[:10]}...")
 else:
 print(" [ERROR] Meta tag found but no content")
 # Let's see what the meta tag looks like
 csrf_line_match = re.search(r'<meta name="csrf-token"[^>]*>', all_orders_response.text)
 if csrf_line_match:
 print(f" Meta tag: {csrf_line_match.group(0)}")
 else:
 print(" [ERROR] No CSRF meta tag found in page")
 # Let's see the first few lines of the HTML to debug
 lines = all_orders_response.text.split('\n')[:10]
 print(" First 10 lines of HTML:")
 for i, line in enumerate(lines, 1):
 print(f" {i}: {line}")
 
 # Also check for any mention of csrf at all
 if 'csrf' in all_orders_response.text.lower():
 print(" [WARNING] Found 'csrf' somewhere in the page")
 else:
 print(" [ERROR] No 'csrf' found anywhere in the page")
 
 # Retry the API call with proper authentication and CSRF
 headers['X-CSRFToken'] = meta_csrf
 
 final_response = session.post(
 f"{base_url}/api/update_order/purchase/1",
 headers=headers,
 data=data
 )
 
 print(f" Final API Status: {final_response.status_code}")
 print(f" Final Response: {final_response.text}")
 
 else:
 print(" [ERROR] No CSRF meta tag found")
 else:
 print(f" [ERROR] Cannot access all_orders: {all_orders_response.status_code}")
 else:
 print(" [ERROR] Login failed")
 else:
 print(" [ERROR] No CSRF token found in login page")
 
 except requests.exceptions.ConnectionError:
 print("[ERROR] Cannot connect to server. Make sure Flask is running!")
 except Exception as e:
 print(f"[ERROR] Error: {e}")

if __name__ == "__main__":
 test_ajax_simple()