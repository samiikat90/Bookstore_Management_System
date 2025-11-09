#!/usr/bin/env python3

import requests
import re

# Create session to persist cookies
session = requests.Session()

print("Testing CSRF token functionality...")
print("=" * 50)

try:
 # Step 1: Get the browse page to establish session
 print("1. Getting browse page to establish session...")
 response = session.get('http://localhost:5000/browse')
 print(f"Browse page status: {response.status_code}")
 
 if response.status_code == 200:
 # Find CSRF token using regex
 csrf_pattern = r'name="csrf_token" value="([^"]+)"'
 csrf_match = re.search(csrf_pattern, response.text)
 
 if csrf_match:
 csrf_token = csrf_match.group(1)
 print(f"Found CSRF token: {csrf_token[:20]}...")
 
 # Find an add_to_cart URL
 add_pattern = r'action="([^"]*add_to_cart/[^"]*)"'
 add_match = re.search(add_pattern, response.text)
 
 if add_match:
 action_path = add_match.group(1)
 full_url = f'http://localhost:5000{action_path}'
 print(f"Found add_to_cart URL: {full_url}")
 
 print(f"\n2. Testing add_to_cart POST with CSRF token...")
 
 # Submit with CSRF token
 form_data = {
 'csrf_token': csrf_token,
 'quantity': 1
 }
 
 post_response = session.post(full_url, data=form_data)
 print(f"Add to cart with CSRF status: {post_response.status_code}")
 
 if post_response.status_code in [200, 302]:
 print("[SUCCESS] SUCCESS: Add to cart worked with CSRF token!")
 if post_response.status_code == 302:
 print(f"Redirected to: {post_response.headers.get('Location', 'Unknown')}")
 else:
 print(f"[ERROR] FAILED: Add to cart returned {post_response.status_code}")
 
 # Step 3: Test without CSRF token (should fail)
 print(f"\n3. Testing add_to_cart POST WITHOUT CSRF token...")
 
 form_data_no_csrf = {
 'quantity': 1 # No CSRF token
 }
 
 post_response_no_csrf = session.post(full_url, data=form_data_no_csrf)
 print(f"Add to cart without CSRF status: {post_response_no_csrf.status_code}")
 
 if post_response_no_csrf.status_code == 400:
 print("[SUCCESS] SUCCESS: Add to cart properly rejected request without CSRF token!")
 elif post_response_no_csrf.status_code == 403:
 print("[SUCCESS] SUCCESS: Add to cart forbidden without CSRF token (403)!")
 else:
 print(f"[WARNING] WARNING: Expected 400/403, got {post_response_no_csrf.status_code}")
 
 else:
 print("[ERROR] Add to cart URL not found!")
 else:
 print("[ERROR] CSRF token not found in page!")
 else:
 print(f"[ERROR] Failed to load browse page: {response.status_code}")

except Exception as e:
 print(f"[ERROR] ERROR: {e}")

print("\n" + "=" * 50)
print("CSRF Test completed!")