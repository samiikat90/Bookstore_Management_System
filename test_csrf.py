#!/usr/bin/env python3
"""
Test CSRF token generation to debug the session token missing error
"""
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app import app
from flask import session

def test_csrf():
	with app.app_context():
		with app.test_request_context():
			print("=== CSRF Test ===")
			
			# Test Flask-WTF CSRF
			try:
				from flask_wtf.csrf import generate_csrf
				token = generate_csrf()
				print(f"[SUCCESS] Flask-WTF CSRF token generated: {token[:20]}...")
			except Exception as e:
				print(f"[FAILED] Flask-WTF CSRF failed: {e}")
			
			# Check app configuration
			print(f"\nApp config:")
			print(f"- SECRET_KEY set: {'yes' if app.secret_key else 'no'}")
			print(f"- SECRET_KEY length: {len(app.secret_key) if app.secret_key else 0}")
			print(f"- WTF_CSRF_ENABLED: {app.config.get('WTF_CSRF_ENABLED', 'not set')}")
			print(f"- WTF_CSRF_TIME_LIMIT: {app.config.get('WTF_CSRF_TIME_LIMIT', 'not set')}")
			
			# Check session configuration
			print(f"\nSession config:")
			print(f"- SESSION_COOKIE_SAMESITE: {app.config.get('SESSION_COOKIE_SAMESITE', 'not set')}")
			print(f"- SESSION_COOKIE_HTTPONLY: {app.config.get('SESSION_COOKIE_HTTPONLY', 'not set')}")
			print(f"- SESSION_COOKIE_SECURE: {app.config.get('SESSION_COOKIE_SECURE', 'not set')}")

if __name__ == "__main__":
 test_csrf()