#!/usr/bin/env python3
"""
Test script to verify customer data encryption functionality.

This script tests:
1. Customer model encryption/decryption
2. Purchase model encryption/decryption
3. PaymentMethod model encryption/decryption
4. Database operations with encrypted data
"""

import sys
import os
import tempfile
import sqlite3

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.encryption_utils import DataEncryption
from app import app, db, Customer, Purchase, PaymentMethod

def test_customer_encryption():
    """Test Customer model encryption/decryption."""
    print("Testing Customer model encryption...")
    
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Create a test customer
        customer = Customer(
            username='testuser',
            full_name='Test User',
            password_hash='dummy_hash'
        )
        
        # Set sensitive data using properties
        customer.email = 'test@example.com'
        customer.phone = '+1-555-123-4567'
        customer.address = '123 Main Street'
        customer.address_line1 = '123 Main Street'
        customer.address_line2 = 'Apt 4B'
        customer.city = 'Test City'
        customer.state = 'TS'
        customer.zip_code = '12345'
        
        # Save to database
        db.session.add(customer)
        db.session.commit()
        
        # Verify encrypted storage
        print(f"  Original email: {customer.email}")
        print(f"  Encrypted email: {customer.email_encrypted[:50]}...")
        print(f"  Original phone: {customer.phone}")
        print(f"  Encrypted phone: {customer.phone_encrypted[:50]}...")
        
        # Retrieve from database and verify decryption
        retrieved_customer = Customer.query.filter_by(username='testuser').first()
        
        success = True
        if retrieved_customer.email != 'test@example.com':
            print(f"  ERROR: Email decryption failed. Got: {retrieved_customer.email}")
            success = False
        
        if retrieved_customer.phone != '+1-555-123-4567':
            print(f"  ERROR: Phone decryption failed. Got: {retrieved_customer.phone}")
            success = False
        
        if retrieved_customer.address != '123 Main Street':
            print(f"  ERROR: Address decryption failed. Got: {retrieved_customer.address}")
            success = False
        
        if success:
            print("  SUCCESS: Customer encryption/decryption working correctly")
        
        # Clean up
        db.session.delete(customer)
        db.session.commit()
        
        return success

def test_purchase_encryption():
    """Test Purchase model encryption/decryption."""
    print("\nTesting Purchase model encryption...")
    
    with app.app_context():
        # Create a test purchase
        purchase = Purchase(
            customer_name='Test Customer',
            book_isbn='9780123456789',
            quantity=2,
            status='Confirmed'
        )
        
        # Set sensitive data using properties
        purchase.customer_email = 'customer@example.com'
        purchase.customer_phone = '+1-555-987-6543'
        purchase.customer_address = '456 Oak Avenue, Test Town, TS 54321'
        
        # Save to database
        db.session.add(purchase)
        db.session.commit()
        
        # Verify encrypted storage
        print(f"  Original email: {purchase.customer_email}")
        print(f"  Encrypted email: {purchase.customer_email_encrypted[:50]}...")
        
        # Retrieve from database and verify decryption
        retrieved_purchase = Purchase.query.filter_by(customer_name='Test Customer').first()
        
        success = True
        if retrieved_purchase.customer_email != 'customer@example.com':
            print(f"  ERROR: Email decryption failed. Got: {retrieved_purchase.customer_email}")
            success = False
        
        if retrieved_purchase.customer_phone != '+1-555-987-6543':
            print(f"  ERROR: Phone decryption failed. Got: {retrieved_purchase.customer_phone}")
            success = False
        
        if retrieved_purchase.customer_address != '456 Oak Avenue, Test Town, TS 54321':
            print(f"  ERROR: Address decryption failed. Got: {retrieved_purchase.customer_address}")
            success = False
        
        if success:
            print("  SUCCESS: Purchase encryption/decryption working correctly")
        
        # Clean up
        db.session.delete(purchase)
        db.session.commit()
        
        return success

def test_payment_encryption():
    """Test PaymentMethod model encryption/decryption."""
    print("\nTesting PaymentMethod model encryption...")
    
    with app.app_context():
        # Create a test payment method
        payment = PaymentMethod(
            method_type='paypal',
            amount=99.99,
            transaction_id='TEST123456',
            status='completed'
        )
        
        # Set sensitive data using properties
        payment.paypal_email = 'payment@example.com'
        
        # Save to database
        db.session.add(payment)
        db.session.commit()
        
        # Verify encrypted storage
        print(f"  Original PayPal email: {payment.paypal_email}")
        print(f"  Encrypted PayPal email: {payment.paypal_email_encrypted[:50]}...")
        
        # Retrieve from database and verify decryption
        retrieved_payment = PaymentMethod.query.filter_by(transaction_id='TEST123456').first()
        
        success = True
        if retrieved_payment.paypal_email != 'payment@example.com':
            print(f"  ERROR: PayPal email decryption failed. Got: {retrieved_payment.paypal_email}")
            success = False
        
        if success:
            print("  SUCCESS: PaymentMethod encryption/decryption working correctly")
        
        # Clean up
        db.session.delete(payment)
        db.session.commit()
        
        return success

def test_encryption_security():
    """Test encryption security properties."""
    print("\nTesting encryption security...")
    
    encryption = DataEncryption()
    
    # Test that same input produces different encrypted output (due to Fernet nonce)
    test_email = "security@test.com"
    encrypted1 = encryption.encrypt(test_email)
    encrypted2 = encryption.encrypt(test_email)
    
    print(f"  Same input, different encrypted outputs:")
    print(f"    Encrypted 1: {encrypted1[:50]}...")
    print(f"    Encrypted 2: {encrypted2[:50]}...")
    
    # Both should decrypt to the same value
    decrypted1 = encryption.decrypt(encrypted1)
    decrypted2 = encryption.decrypt(encrypted2)
    
    success = True
    if decrypted1 != test_email or decrypted2 != test_email:
        print("  ERROR: Decryption failed")
        success = False
    elif encrypted1 == encrypted2:
        print("  WARNING: Encrypted outputs are identical (weak security)")
        success = False
    else:
        print("  SUCCESS: Encryption provides proper security")
    
    return success

def main():
    """Run all encryption tests."""
    print("=== Customer Data Encryption Tests ===")
    
    # Set up a temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
        temp_db_path = temp_db.name
    
    # Configure app to use temporary database
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{temp_db_path}'
    
    try:
        results = []
        results.append(test_customer_encryption())
        results.append(test_purchase_encryption())
        results.append(test_payment_encryption())
        results.append(test_encryption_security())
        
        print("\n=== Test Results ===")
        if all(results):
            print("SUCCESS: All encryption tests passed!")
            print("Customer data encryption is working correctly.")
        else:
            print("FAILURE: Some encryption tests failed.")
            print("Please review the output above for details.")
    
    finally:
        # Clean up temporary database
        if os.path.exists(temp_db_path):
            os.unlink(temp_db_path)

if __name__ == "__main__":
    main()