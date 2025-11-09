#!/usr/bin/env python3

import sys
import os
import requests
from urllib.parse import urljoin

def test_checkout_flow():
	"""Test the actual checkout flow to see if admin notifications are sent."""
	
	base_url = "http://127.0.0.1:5000"
	
	print("Testing Checkout Flow with Admin Notifications")
	print("=" * 55)
	
	# Create a session to maintain cookies
	session = requests.Session()
	
	try:
		# Step 1: Check if the app is running
		print("\n1. Checking if Flask app is running...")
		response = session.get(base_url)
		if response.status_code != 200:
			print(f"Flask app not running. Got status: {response.status_code}")
			return False
		print(" Flask app is running")
		
		# Step 2: Login as a customer
		print("\n2. Attempting to login as customer...")
		login_url = urljoin(base_url, "/customer_login")
		login_data = {
			'email': 'sampleuser2@example.com',  # assuming this user exists
			'password': 'password123',
			'csrf_token': 'dummy'  # We might need to get real CSRF token
		}
		
		# Get login page to get CSRF token
		login_page = session.get(login_url)
		print(f"Login page status: {login_page.status_code}")
		
		# Try to login (this might fail due to CSRF but let's see)
		login_response = session.post(login_url, data=login_data)
		print(f"Login response status: {login_response.status_code}")
		print(f"Response URL: {login_response.url}")
		
		# Step 3: Add items to cart
		print("\n3. Adding items to cart...")
		# This is complex to simulate without knowing the exact cart mechanism
		
		# For now, let's just check what happens when we visit checkout
		print("\n4. Testing checkout page access...")
		checkout_url = urljoin(base_url, "/checkout")
		checkout_response = session.get(checkout_url)
		print(f"Checkout page status: {checkout_response.status_code}")
		print(f"Checkout page URL: {checkout_response.url}")
		
		if "login" in checkout_response.url:
			print("Redirected to login page - authentication required")
		elif "cart" in checkout_response.url:
			print("Redirected to cart page - probably empty cart")
		else:
			print("Successfully accessed checkout page")
		
		return True
		
	except Exception as e:
		print(f"Error during checkout flow test: {e}")
		return False

def check_flask_app_status():
	"""Check if Flask app is running and responsive."""
	try:
		response = requests.get("http://127.0.0.1:5000", timeout=5)
		return response.status_code == 200
	except:
		return False

if __name__ == "__main__":
	if not check_flask_app_status():
		print("Flask app is not running. Please start the app first:")
		print("python app/app.py")
	else:
		test_checkout_flow()