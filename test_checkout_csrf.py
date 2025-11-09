#!/usr/bin/env python3
"""
Test script to verify CSRF token and checkout functionality
"""
import requests
import sys
import os

# Add app directory to path
sys.path.insert(0, './app')

def test_checkout_csrf():
 """Test that CSRF tokens are properly handled in checkout"""
 
 base_url = "http://localhost:5000"
 
 # Create a session to maintain cookies
 session = requests.Session()
 
 try:
 # 1. First, try to access the login page to establish a session
 print("1. Accessing login page...")
 login_response = session.get(f"{base_url}/customer/login")
 print(f"Login page status: {login_response.status_code}")
 
 # 2. Try to login as the test user
 print("2. Logging in as SampleUser...")
 login_data = {
 'username': 'SampleUser',
 'password': 'password123'
 }
 
 login_result = session.post(f"{base_url}/customer/login", data=login_data)
 print(f"Login result status: {login_result.status_code}")
 print(f"Login result URL: {login_result.url}")
 
 # 3. Add a book to cart
 print("3. Adding book to cart...")
 add_cart_result = session.post(f"{base_url}/add_to_cart/9781234567892")
 print(f"Add to cart status: {add_cart_result.status_code}")
 
 # 4. Try to access checkout page
 print("4. Accessing checkout page...")
 checkout_response = session.get(f"{base_url}/checkout")
 print(f"Checkout page status: {checkout_response.status_code}")
 print(f"Checkout page URL: {checkout_response.url}")
 
 # 5. Check if checkout page contains CSRF token
 if "csrf_token" in checkout_response.text:
 print(" CSRF token found in checkout page")
 else:
 print(" CSRF token NOT found in checkout page")
 
 # 6. Extract CSRF token if present
 import re
 csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', checkout_response.text)
 if csrf_match:
 csrf_token = csrf_match.group(1)
 print(f" CSRF token extracted: {csrf_token[:10]}...")
 
 # 7. Try to submit checkout form with CSRF token
 print("5. Submitting checkout form...")
 checkout_data = {
 'csrf_token': csrf_token,
 'payment_method': 'credit_card',
 'card_number': '4111111111111111',
 'cvv': '123',
 'cardholder_name': 'Test User',
 'expiry': '12/25'
 }
 
 checkout_result = session.post(f"{base_url}/process_checkout", data=checkout_data)
 print(f"Checkout result status: {checkout_result.status_code}")
 print(f"Checkout result URL: {checkout_result.url}")
 
 if checkout_result.status_code == 200:
 print(" Checkout successful!")
 elif checkout_result.status_code == 302:
 print(f"→ Checkout redirected to: {checkout_result.headers.get('Location')}")
 else:
 print(f" Checkout failed with status: {checkout_result.status_code}")
 else:
 print(" Could not extract CSRF token")
 
 except requests.exceptions.RequestException as e:
 print(f"Request error: {e}")
 except Exception as e:
 print(f"Error: {e}")

if __name__ == "__main__":
 print("Testing CSRF token and checkout functionality...")
 print("=" * 50)
 test_checkout_csrf()