#!/usr/bin/env python3
"""
Debug test to simulate the exact AJAX request from all_orders.html
"""
import requests
import json
from bs4 import BeautifulSoup

def test_ajax_update():
 print("[DEBUG] DEBUG: Testing AJAX Order Update")
 print("=" * 40)
 
 session = requests.Session()
 base_url = "http://127.0.0.1:5000"
 
 try:
 # Step 1: Get login page and extract CSRF token
 print("1. Getting login page...")
 login_response = session.get(f"{base_url}/login")
 print(f" Status: {login_response.status_code}")
 
 soup = BeautifulSoup(login_response.text, 'html.parser')
 csrf_token = None
 csrf_input = soup.find('input', {'name': 'csrf_token'})
 if csrf_input:
 csrf_token = csrf_input.get('value')
 print(f" CSRF Token: {csrf_token[:10]}...")
 else:
 print(" [ERROR] No CSRF token found in login page")
 
 # Step 2: Try to login
 print("2. Attempting login...")
 login_data = {
 'username': 'admin',
 'password': 'admin123',
 'csrf_token': csrf_token
 }
 
 login_result = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
 print(f" Login result: {login_result.status_code}")
 
 if login_result.status_code == 302:
 print(" [SUCCESS] Login successful (redirected)")
 else:
 print(f" [ERROR] Login failed: {login_result.text[:200]}")
 return
 
 # Step 3: Get all_orders page and check CSRF token
 print("3. Getting all_orders page...")
 orders_response = session.get(f"{base_url}/all_orders")
 print(f" Status: {orders_response.status_code}")
 
 if orders_response.status_code != 200:
 print(" [ERROR] Cannot access all_orders page")
 return
 
 # Extract CSRF token from meta tag
 soup = BeautifulSoup(orders_response.text, 'html.parser')
 csrf_meta = soup.find('meta', {'name': 'csrf-token'})
 if csrf_meta:
 page_csrf_token = csrf_meta.get('content')
 print(f" Page CSRF Token: {page_csrf_token[:10]}...")
 else:
 print(" [ERROR] No CSRF meta tag found in all_orders page")
 return
 
 # Step 4: Test the AJAX update request
 print("4. Testing AJAX update request...")
 
 # Use the same headers and data as the JavaScript
 headers = {
 'Content-Type': 'application/x-www-form-urlencoded',
 'X-CSRFToken': page_csrf_token,
 'X-Requested-With': 'XMLHttpRequest' # Important for AJAX detection
 }
 
 data = 'status=Processing'
 
 # Try to update order #1 (assuming it exists)
 ajax_response = session.post(
 f"{base_url}/api/update_order/purchase/1",
 headers=headers,
 data=data
 )
 
 print(f" AJAX Status: {ajax_response.status_code}")
 print(f" Content-Type: {ajax_response.headers.get('content-type', 'unknown')}")
 
 if ajax_response.status_code == 200:
 try:
 json_data = ajax_response.json()
 print(f" [SUCCESS] JSON Response: {json_data}")
 except:
 print(f" [ERROR] Not JSON. Response: {ajax_response.text[:200]}")
 else:
 print(f" [ERROR] Error response: {ajax_response.text[:200]}")
 
 except requests.exceptions.ConnectionError:
 print("[ERROR] Cannot connect to Flask server at http://127.0.0.1:5000")
 print(" Make sure Flask is running: python app/app.py")
 except Exception as e:
 print(f"[ERROR] Error: {e}")

if __name__ == "__main__":
 test_ajax_update()