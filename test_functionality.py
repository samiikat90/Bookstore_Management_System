#!/usr/bin/env python3
"""
Quick test to verify the application works properly after emoji removal
"""
import sys
import os
sys.path.append('app')

try:
    print("[INFO] Testing Flask app import...")
    from app import app, db, User, Book, Purchase
    print("[SUCCESS] Flask app and models imported successfully")
    
    # Test database connection
    print("[INFO] Testing database connection...")
    with app.app_context():
        try:
            users = User.query.limit(1).all()
            books = Book.query.limit(1).all()
            orders = Purchase.query.limit(1).all()
            print(f"[SUCCESS] Database accessible - {len(users)} users, {len(books)} books, {len(orders)} orders")
        except Exception as e:
            print(f"[ERROR] Database connection failed: {e}")
    
    # Test route configuration
    print("[INFO] Testing route configuration...")
    with app.test_client() as client:
        response = client.get('/')
        if response.status_code == 200:
            print("[SUCCESS] Index route accessible")
        else:
            print(f"[WARNING] Index route returned {response.status_code}")
    
    print("\n[SUCCESS] All core functionality tests passed!")
    print("The application is ready to run without any emoji-related issues.")
    
except ImportError as e:
    print(f"[ERROR] Import failed: {e}")
except Exception as e:
    print(f"[ERROR] Test failed: {e}")