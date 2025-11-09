#!/usr/bin/env python3
"""
Simple route testing script to verify all routes are accessible.
This doesn't test authentication, just basic route existence.
"""

import requests
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_routes():
    """Test basic route accessibility"""
    base_url = "http://127.0.0.1:5000"
    
    # Basic routes that should be accessible
    test_routes = [
        "/",
        "/browse",
        "/customer/login",
        "/customer/register",
        "/login",
        "/cart",
        "/catalog"
    ]
    
    print("Testing basic routes...")
    for route in test_routes:
        try:
            response = requests.get(f"{base_url}{route}", timeout=5)
            status = "✓" if response.status_code < 500 else "✗"
            print(f"{status} {route} - {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"✗ {route} - Connection error: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("Route Testing Script")
    print("Make sure the Flask app is running on http://127.0.0.1:5000")
    print("=" * 50)
    
    if test_routes():
        print("\n✓ Basic route testing complete")
    else:
        print("\n✗ Route testing failed - Flask app might not be running")