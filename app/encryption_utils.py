#!/usr/bin/env python3
"""
Customer data encryption utilities for secure handling of sensitive information.

This module provides encryption/decryption functions for customer data such as:
- Email addresses
- Phone numbers
- Physical addresses
- Payment information

Uses Fernet symmetric encryption from the cryptography library for security.
"""

import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class DataEncryption:
    """Handles encryption and decryption of sensitive customer data."""
    
    def __init__(self, password=None):
        """Initialize encryption with a password or environment variable."""
        if password is None:
            # Try to get from environment variable, fallback to default for development
            password = os.environ.get('ENCRYPTION_PASSWORD', 'chapter6_bookstore_dev_key_2025')
        
        # Generate a key from the password
        self.key = self._generate_key_from_password(password)
        self.cipher_suite = Fernet(self.key)
    
    def _generate_key_from_password(self, password):
        """Generate a Fernet key from a password using PBKDF2."""
        # Use a fixed salt for consistency (in production, consider using random salt per user)
        salt = b'chapter6_bookstore_salt_2025'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,  # Recommended minimum iterations
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt(self, data):
        """Encrypt a string and return base64 encoded result."""
        if data is None or data == '':
            return None
        
        try:
            # Convert to bytes if it's a string
            if isinstance(data, str):
                data_bytes = data.encode('utf-8')
            else:
                data_bytes = data
            
            # Encrypt the data
            encrypted_data = self.cipher_suite.encrypt(data_bytes)
            
            # Return base64 encoded string for database storage
            return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
            
        except Exception as e:
            print(f"Encryption error: {e}")
            return None
    
    def decrypt(self, encrypted_data):
        """Decrypt base64 encoded data and return original string."""
        if encrypted_data is None or encrypted_data == '':
            return None
        
        try:
            # Decode from base64
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
            
            # Decrypt the data
            decrypted_bytes = self.cipher_suite.decrypt(encrypted_bytes)
            
            # Return as string
            return decrypted_bytes.decode('utf-8')
            
        except Exception as e:
            print(f"Decryption error: {e}")
            return None
    
    def encrypt_email(self, email):
        """Encrypt an email address."""
        return self.encrypt(email)
    
    def decrypt_email(self, encrypted_email):
        """Decrypt an email address."""
        return self.decrypt(encrypted_email)
    
    def encrypt_phone(self, phone):
        """Encrypt a phone number."""
        return self.encrypt(phone)
    
    def decrypt_phone(self, encrypted_phone):
        """Decrypt a phone number."""
        return self.decrypt(encrypted_phone)
    
    def encrypt_address(self, address):
        """Encrypt an address."""
        return self.encrypt(address)
    
    def decrypt_address(self, encrypted_address):
        """Decrypt an address."""
        return self.decrypt(encrypted_address)
    
    def encrypt_sensitive_data(self, data_dict):
        """Encrypt multiple fields in a dictionary."""
        encrypted_dict = {}
        sensitive_fields = ['email', 'phone', 'address', 'address_line1', 'address_line2', 'customer_email', 'customer_phone', 'customer_address']
        
        for key, value in data_dict.items():
            if key in sensitive_fields and value:
                encrypted_dict[key] = self.encrypt(value)
            else:
                encrypted_dict[key] = value
        
        return encrypted_dict
    
    def decrypt_sensitive_data(self, data_dict):
        """Decrypt multiple fields in a dictionary."""
        decrypted_dict = {}
        sensitive_fields = ['email', 'phone', 'address', 'address_line1', 'address_line2', 'customer_email', 'customer_phone', 'customer_address']
        
        for key, value in data_dict.items():
            if key in sensitive_fields and value:
                decrypted_dict[key] = self.decrypt(value)
            else:
                decrypted_dict[key] = value
        
        return decrypted_dict


# Global encryption instance
encryption = DataEncryption()


def test_encryption():
    """Test encryption functionality."""
    test_data = {
        'email': 'customer@example.com',
        'phone': '+1-555-123-4567',
        'address': '123 Main Street, Anytown, ST 12345',
        'name': 'John Doe'  # Non-sensitive field
    }
    
    print("Original data:")
    for key, value in test_data.items():
        print(f"  {key}: {value}")
    
    # Encrypt sensitive data
    encrypted_data = encryption.encrypt_sensitive_data(test_data)
    print("\nEncrypted data:")
    for key, value in encrypted_data.items():
        print(f"  {key}: {value}")
    
    # Decrypt sensitive data
    decrypted_data = encryption.decrypt_sensitive_data(encrypted_data)
    print("\nDecrypted data:")
    for key, value in decrypted_data.items():
        print(f"  {key}: {value}")
    
    # Verify data integrity
    sensitive_fields = ['email', 'phone', 'address']
    success = True
    for field in sensitive_fields:
        if test_data[field] != decrypted_data[field]:
            print(f"ERROR: {field} data integrity check failed!")
            success = False
    
    if success:
        print("\nSUCCESS: All encryption/decryption tests passed!")
    else:
        print("\nFAILURE: Data integrity check failed!")


if __name__ == "__main__":
    test_encryption()