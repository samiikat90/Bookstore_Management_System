#!/usr/bin/env python3
"""
Test to check what template is actually being rendered
"""
import requests
import re

def check_template_being_rendered():
 print("[DEBUG] TEMPLATE DEBUG TEST")
 print("=" * 25)
 
 session = requests.Session()
 base_url = "http://127.0.0.1:5000"
 
 try:
 # Login first
 print("1. Logging in...")
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
 
 if login_result.status_code == 302:
 print(" [SUCCESS] Login successful")
 
 # Get all_orders page
 print("\n2. Getting all_orders page...")
 orders_response = session.get(f"{base_url}/all_orders")
 
 print(f" Status: {orders_response.status_code}")
 
 if orders_response.status_code == 200:
 html = orders_response.text
 
 # Check what title is actually in the page
 title_match = re.search(r'<title>([^<]*)</title>', html)
 if title_match:
 title = title_match.group(1).strip()
 print(f" Page title: '{title}'")
 
 if title == "All Orders":
 print(" [SUCCESS] Correct template (all_orders.html)")
 else:
 print(f" [ERROR] Wrong template - expected 'All Orders', got '{title}'")
 
 # Look for specific markers from all_orders.html
 if 'Set status...' in html:
 print(" [SUCCESS] Found 'Set status...' (from all_orders.html)")
 else:
 print(" [ERROR] 'Set status...' not found")
 
 if 'status-select' in html:
 print(" [SUCCESS] Found 'status-select' class (from all_orders.html)")
 else:
 print(" [ERROR] 'status-select' class not found")
 
 # Check for CSRF token specifically
 if 'csrf-token' in html:
 print(" [SUCCESS] Found 'csrf-token' in HTML")
 # Find the actual meta tag
 meta_match = re.search(r'<meta name="csrf-token" content="([^"]*)"', html)
 if meta_match:
 token = meta_match.group(1)
 if token.strip():
 print(f" [SUCCESS] CSRF token has content: {token[:15]}...")
 else:
 print(" [ERROR] CSRF token is empty")
 else:
 print(" [ERROR] Could not extract CSRF token content")
 else:
 print(" [ERROR] No 'csrf-token' found in HTML")
 
 # Show the head section
 head_match = re.search(r'<head>(.*?)</head>', html, re.DOTALL)
 if head_match:
 head_content = head_match.group(1)
 print("\n Head section content:")
 lines = head_content.split('\n')
 for i, line in enumerate(lines[:10], 1):
 print(f" {i:2}: {line.strip()}")
 
 else:
 print(f" [ERROR] Failed to get page: {orders_response.status_code}")
 
 else:
 print(" [ERROR] Login failed")
 else:
 print(" [ERROR] No CSRF token in login page")
 
 except Exception as e:
 print(f"[ERROR] Error: {e}")

if __name__ == "__main__":
 check_template_being_rendered()