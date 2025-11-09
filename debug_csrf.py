#!/usr/bin/env python3
"""
Quick CSRF debugging script to test token generation
"""
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from flask import Flask
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
import secrets

# Create minimal Flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Enable CSRF protection
csrf = CSRFProtect(app)

# Test form
class TestForm(FlaskForm):
 test_field = StringField('Test')
 submit = SubmitField('Submit')

@app.route('/', methods=['GET', 'POST'])
def test_csrf():
 form = TestForm()
 
 with app.test_request_context():
 # Test if CSRF token can be generated
 try:
 token = generate_csrf()
 print(f" CSRF token generated successfully: {token[:20]}...")
 return f"CSRF Token: {token}"
 except Exception as e:
 print(f" Error generating CSRF token: {e}")
 return f"Error: {e}"

if __name__ == '__main__':
 print("Testing CSRF token generation...")
 
 with app.test_request_context():
 try:
 token = generate_csrf()
 print(f" CSRF token generated: {token[:20]}...")
 except Exception as e:
 print(f" Error: {e}")
 
 print("\nStarting test server on http://127.0.0.1:5001")
 app.run(debug=True, port=5001)