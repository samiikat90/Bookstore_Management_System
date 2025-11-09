#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import urllib.parse

# Create session to persist cookies
session = requests.Session()

print("Testing CSRF token functionality...")
print("=" * 50)

try:
 # Step 1: Get the home page to establish session and get CSRF token
 print("1. Getting home page to establish session...")
 response = session.get('http://localhost:5000/')
 print(f"Home page status: {response.status_code}")
 
 # Step 2: Get browse page where add_to_cart forms are
 print("\n2. Getting browse page...")
 response = session.get('http://localhost:5000/browse')
 print(f"Browse page status: {response.status_code}")
 
 # Parse the page to find a form with add_to_cart
 soup = BeautifulSoup(response.text, 'html.parser')
 
 # Find first add_to_cart form
 add_form = soup.find('form', action=lambda x: x and 'add_to_cart' in x)
 if add_form:
 print(f"Found add_to_cart form: {add_form.get('action')}")
 
 # Look for CSRF token in the form
 csrf_input = add_form.find('input', {'name': 'csrf_token'})
 if csrf_input:
 csrf_token = csrf_input.get('value')
 print(f"Found CSRF token in form: {csrf_token[:20]}...")
 
 # Extract the action URL
 action_url = add_form.get('action')
 full_url = urllib.parse.urljoin('http://localhost:5000/', action_url)
 
 print(f"\n3. Testing add_to_cart POST with CSRF token...")
 
 # Submit the form with CSRF token
 form_data = {
 'csrf_token': csrf_token,
 'quantity': 1
 }
 
 post_response = session.post(full_url, data=form_data)
 print(f"Add to cart status: {post_response.status_code}")
 
 if post_response.status_code == 200:
 print("[SUCCESS] SUCCESS: Add to cart worked with CSRF token!")
 elif post_response.status_code == 302:
 print("[SUCCESS] SUCCESS: Add to cart redirected (likely successful)!")
 print(f"Redirect location: {post_response.headers.get('Location', 'Not specified')}")
 else:
 print(f"[ERROR] FAILED: Add to cart returned {post_response.status_code}")
 print(f"Response text: {post_response.text[:200]}...")
 else:
 print("[ERROR] CSRF token not found in add_to_cart form!")
 else:
 print("[ERROR] Add to cart form not found!")
 
 # Step 4: Test without CSRF token (should fail)
 print(f"\n4. Testing add_to_cart POST WITHOUT CSRF token...")
 if add_form:
 action_url = add_form.get('action')
 full_url = urllib.parse.urljoin('http://localhost:5000/', action_url)
 
 form_data = {
 'quantity': 1 # No CSRF token
 }
 
 post_response = session.post(full_url, data=form_data)
 print(f"Add to cart without CSRF status: {post_response.status_code}")
 
 if post_response.status_code == 400:
 print("[SUCCESS] SUCCESS: Add to cart properly rejected request without CSRF token!")
 else:
 print(f"[WARNING] WARNING: Expected 400, got {post_response.status_code}")
 
except Exception as e:
 print(f"[ERROR] ERROR: {e}")

print("\n" + "=" * 50)
print("CSRF Test completed!")