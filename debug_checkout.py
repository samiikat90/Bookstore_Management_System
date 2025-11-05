#!/usr/bin/env python3
"""
Debug script to test checkout workflow
"""

import requests
import json

BASE_URL = 'http://127.0.0.1:5000'

def test_checkout_workflow():
    """Test the checkout workflow step by step."""
    print("=== Testing Checkout Workflow ===\n")
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Test 1: Can we access the home page?
    print("1. Testing home page access...")
    try:
        response = session.get(BASE_URL)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ Home page accessible")
        else:
            print("   ✗ Home page not accessible")
            return
    except Exception as e:
        print(f"   ✗ Error accessing home page: {e}")
        return
    
    # Test 2: Can we access the checkout page directly?
    print("\n2. Testing direct checkout access...")
    try:
        response = session.get(f'{BASE_URL}/checkout')
        print(f"   Status: {response.status_code}")
        print(f"   URL after redirect: {response.url}")
        
        if 'login' in response.url:
            print("   → Redirected to login (expected if not logged in)")
        elif 'cart' in response.url:
            print("   → Redirected to cart (expected if cart is empty)")
        elif response.status_code == 200:
            print("   ✓ Checkout page accessible")
        else:
            print("   ✗ Unexpected response")
    except Exception as e:
        print(f"   ✗ Error accessing checkout: {e}")
    
    # Test 3: Test the process_checkout endpoint
    print("\n3. Testing process_checkout endpoint...")
    try:
        # Simulate form data
        form_data = {
            'payment_method': 'credit_card',
            'card_number': '4242424242424242',
            'expiry': '12/26',
            'cvv': '123',
            'cardholder_name': 'Test User'
        }
        
        response = session.post(f'{BASE_URL}/process_checkout', data=form_data)
        print(f"   Status: {response.status_code}")
        print(f"   URL after redirect: {response.url}")
        
        if 'login' in response.url:
            print("   → Redirected to login (expected if not logged in)")
        elif 'cart' in response.url:
            print("   → Redirected to cart (expected if cart is empty)")
        else:
            print("   → Other response")
            
    except Exception as e:
        print(f"   ✗ Error testing process_checkout: {e}")
    
    # Test 4: Test our test route
    print("\n4. Testing test route...")
    try:
        response = session.get(f'{BASE_URL}/test_route')
        print(f"   Status: {response.status_code}")
        print(f"   Content: {response.text[:100]}")
        
        # Test POST to test route
        response = session.post(f'{BASE_URL}/test_route', data={'test': 'data'})
        print(f"   POST Status: {response.status_code}")
        print(f"   POST Content: {response.text[:100]}")
        
    except Exception as e:
        print(f"   ✗ Error testing test route: {e}")

if __name__ == "__main__":
    test_checkout_workflow()