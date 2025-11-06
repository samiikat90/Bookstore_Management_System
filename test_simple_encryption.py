#!/usr/bin/env python3
"""
Simple encryption test without database operations.
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from encryption_utils import DataEncryption

def test_basic_encryption():
    """Test basic encryption/decryption functionality."""
    print("Testing basic encryption functionality...")
    
    encryption = DataEncryption()
    
    test_data = {
        'email': 'customer@bookstore.com',
        'phone': '+1-555-BOOK-123',
        'address': '123 Literature Lane, Novel City, ST 12345',
        'non_sensitive': 'This should not be encrypted'
    }
    
    print("Original data:")
    for key, value in test_data.items():
        print(f"  {key}: {value}")
    
    # Test individual field encryption
    email_encrypted = encryption.encrypt_email(test_data['email'])
    phone_encrypted = encryption.encrypt_phone(test_data['phone'])
    address_encrypted = encryption.encrypt_address(test_data['address'])
    
    print(f"\nEncrypted data:")
    print(f"  email: {email_encrypted[:50]}...")
    print(f"  phone: {phone_encrypted[:50]}...")
    print(f"  address: {address_encrypted[:50]}...")
    
    # Test decryption
    email_decrypted = encryption.decrypt_email(email_encrypted)
    phone_decrypted = encryption.decrypt_phone(phone_encrypted)
    address_decrypted = encryption.decrypt_address(address_encrypted)
    
    print(f"\nDecrypted data:")
    print(f"  email: {email_decrypted}")
    print(f"  phone: {phone_decrypted}")
    print(f"  address: {address_decrypted}")
    
    # Verify integrity
    success = True
    if email_decrypted != test_data['email']:
        print("ERROR: Email encryption/decryption failed")
        success = False
    if phone_decrypted != test_data['phone']:
        print("ERROR: Phone encryption/decryption failed")
        success = False
    if address_decrypted != test_data['address']:
        print("ERROR: Address encryption/decryption failed")
        success = False
    
    if success:
        print("\nSUCCESS: All encryption tests passed!")
    
    return success

def test_bulk_encryption():
    """Test bulk encryption/decryption of multiple fields."""
    print("\nTesting bulk encryption functionality...")
    
    encryption = DataEncryption()
    
    customer_data = {
        'username': 'booklover123',
        'email': 'booklover@reading.com',
        'phone': '+1-555-READ-NOW',
        'address': '456 Chapter Street',
        'full_name': 'Jane Book Reader',
        'city': 'Library Town'
    }
    
    print("Original customer data:")
    for key, value in customer_data.items():
        print(f"  {key}: {value}")
    
    # Encrypt sensitive fields
    encrypted_data = encryption.encrypt_sensitive_data(customer_data)
    
    print(f"\nEncrypted customer data:")
    for key, value in encrypted_data.items():
        if key in ['email', 'phone', 'address']:
            print(f"  {key}: {value[:50]}...")
        else:
            print(f"  {key}: {value}")
    
    # Decrypt sensitive fields
    decrypted_data = encryption.decrypt_sensitive_data(encrypted_data)
    
    print(f"\nDecrypted customer data:")
    for key, value in decrypted_data.items():
        print(f"  {key}: {value}")
    
    # Verify integrity
    success = True
    sensitive_fields = ['email', 'phone', 'address']
    for field in sensitive_fields:
        if customer_data[field] != decrypted_data[field]:
            print(f"ERROR: {field} integrity check failed")
            success = False
    
    if success:
        print("\nSUCCESS: Bulk encryption tests passed!")
    
    return success

def test_edge_cases():
    """Test encryption with edge cases."""
    print("\nTesting edge cases...")
    
    encryption = DataEncryption()
    
    # Test with None values
    none_encrypted = encryption.encrypt(None)
    empty_encrypted = encryption.encrypt('')
    
    print(f"None encrypted: {none_encrypted}")
    print(f"Empty string encrypted: {empty_encrypted}")
    
    # Test decryption of None/empty
    none_decrypted = encryption.decrypt(none_encrypted)
    empty_decrypted = encryption.decrypt(empty_encrypted)
    
    print(f"None decrypted: {none_decrypted}")
    print(f"Empty string decrypted: {empty_decrypted}")
    
    # Test with special characters
    special_data = "test@example.com with special chars: àáâãäåæçèéêëìíîïðñòóôõö"
    special_encrypted = encryption.encrypt(special_data)
    special_decrypted = encryption.decrypt(special_encrypted)
    
    print(f"Special characters test:")
    print(f"  Original: {special_data}")
    print(f"  Decrypted: {special_decrypted}")
    
    success = special_data == special_decrypted
    if success:
        print("SUCCESS: Edge case tests passed!")
    else:
        print("ERROR: Edge case tests failed!")
    
    return success

def main():
    """Run all tests."""
    print("=== Customer Data Encryption Tests ===")
    
    results = []
    results.append(test_basic_encryption())
    results.append(test_bulk_encryption())
    results.append(test_edge_cases())
    
    print("\n=== Final Results ===")
    if all(results):
        print("SUCCESS: All encryption functionality is working correctly!")
        print("Customer data encryption is ready for use.")
    else:
        print("FAILURE: Some tests failed. Please review the output above.")

if __name__ == "__main__":
    main()