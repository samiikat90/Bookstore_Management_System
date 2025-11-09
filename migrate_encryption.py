#!/usr/bin/env python3
"""
Database migration script to encrypt existing customer data.

This script will:
1. Read existing unencrypted customer data
2. Encrypt sensitive fields (email, phone, address)
3. Update the database with encrypted data
4. Backup original data before migration

IMPORTANT: Run this script AFTER updating the models but BEFORE using the new encryption fields.
"""

import sys
import os
import sqlite3
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app import encryption_utils

def backup_database():
    """Create a backup of the current database."""
    db_path = 'instance/bookstore.db'
    backup_path = f'instance/bookstore_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
    
    if os.path.exists(db_path):
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"Database backed up to: {backup_path}")
        return backup_path
    else:
        print("Warning: Database file not found, no backup created")
        return None

def migrate_customer_data():
    """Migrate customer data to use encrypted fields."""
    db_path = 'instance/bookstore.db'
    
    if not os.path.exists(db_path):
        print("Database file not found. Creating new database with encrypted fields.")
        return
    
    print("Migrating customer data to encrypted format...")
    encryption = encryption_utils.DataEncryption()
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the new encrypted columns exist
        cursor.execute("PRAGMA table_info(customer)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add new encrypted columns if they don't exist
        if 'email_encrypted' not in columns:
            print("Adding email_encrypted column...")
            cursor.execute("ALTER TABLE customer ADD COLUMN email_encrypted TEXT")
        
        if 'phone_encrypted' not in columns:
            print("Adding phone_encrypted column...")
            cursor.execute("ALTER TABLE customer ADD COLUMN phone_encrypted TEXT")
        
        if 'address_encrypted' not in columns:
            print("Adding address_encrypted column...")
            cursor.execute("ALTER TABLE customer ADD COLUMN address_encrypted TEXT")
        
        if 'address_line1_encrypted' not in columns:
            print("Adding address_line1_encrypted column...")
            cursor.execute("ALTER TABLE customer ADD COLUMN address_line1_encrypted TEXT")
        
        if 'address_line2_encrypted' not in columns:
            print("Adding address_line2_encrypted column...")
            cursor.execute("ALTER TABLE customer ADD COLUMN address_line2_encrypted TEXT")
        
        # Migrate existing data
        cursor.execute("SELECT id, email, phone, address, address_line1, address_line2 FROM customer")
        customers = cursor.fetchall()
        
        migrated_count = 0
        for customer in customers:
            customer_id, email, phone, address, address_line1, address_line2 = customer
            
            # Encrypt sensitive data
            email_encrypted = encryption.encrypt(email) if email else None
            phone_encrypted = encryption.encrypt(phone) if phone else None
            address_encrypted = encryption.encrypt(address) if address else None
            address_line1_encrypted = encryption.encrypt(address_line1) if address_line1 else None
            address_line2_encrypted = encryption.encrypt(address_line2) if address_line2 else None
            
            # Update the record with encrypted data
            cursor.execute("""
                UPDATE customer 
                SET email_encrypted = ?, phone_encrypted = ?, address_encrypted = ?, 
                    address_line1_encrypted = ?, address_line2_encrypted = ?
                WHERE id = ?
            """, (email_encrypted, phone_encrypted, address_encrypted, 
                  address_line1_encrypted, address_line2_encrypted, customer_id))
            
            migrated_count += 1
        
        conn.commit()
        print(f"Successfully migrated {migrated_count} customer records to encrypted format")
        
    except Exception as e:
        print(f"Error during customer data migration: {e}")
        conn.rollback()
    finally:
        conn.close()

def migrate_purchase_data():
    """Migrate purchase data to use encrypted fields."""
    db_path = 'instance/bookstore.db'
    
    if not os.path.exists(db_path):
        print("Database file not found. No purchase data to migrate.")
        return
    
    print("Migrating purchase data to encrypted format...")
    encryption = encryption_utils.DataEncryption()
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the purchases table exists and has the old columns
        cursor.execute("PRAGMA table_info(purchases)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if not columns:
            print("Purchases table not found. No migration needed.")
            return
        
        # Add new encrypted columns if they don't exist
        if 'customer_email_encrypted' not in columns:
            print("Adding customer_email_encrypted column...")
            cursor.execute("ALTER TABLE purchases ADD COLUMN customer_email_encrypted TEXT")
        
        if 'customer_phone_encrypted' not in columns:
            print("Adding customer_phone_encrypted column...")
            cursor.execute("ALTER TABLE purchases ADD COLUMN customer_phone_encrypted TEXT")
        
        if 'customer_address_encrypted' not in columns:
            print("Adding customer_address_encrypted column...")
            cursor.execute("ALTER TABLE purchases ADD COLUMN customer_address_encrypted TEXT")
        
        # Migrate existing data if old columns exist
        if 'customer_email' in columns:
            cursor.execute("SELECT id, customer_email, customer_phone, customer_address FROM purchases")
            purchases = cursor.fetchall()
            
            migrated_count = 0
            for purchase in purchases:
                purchase_id, email, phone, address = purchase
                
                # Encrypt sensitive data
                email_encrypted = encryption.encrypt(email) if email else None
                phone_encrypted = encryption.encrypt(phone) if phone else None
                address_encrypted = encryption.encrypt(address) if address else None
                
                # Update the record with encrypted data
                cursor.execute("""
                    UPDATE purchases 
                    SET customer_email_encrypted = ?, customer_phone_encrypted = ?, customer_address_encrypted = ?
                    WHERE id = ?
                """, (email_encrypted, phone_encrypted, address_encrypted, purchase_id))
                
                migrated_count += 1
            
            conn.commit()
            print(f"Successfully migrated {migrated_count} purchase records to encrypted format")
        
    except Exception as e:
        print(f"Error during purchase data migration: {e}")
        conn.rollback()
    finally:
        conn.close()

def migrate_payment_data():
    """Migrate payment method data to use encrypted fields."""
    db_path = 'instance/bookstore.db'
    
    if not os.path.exists(db_path):
        print("Database file not found. No payment data to migrate.")
        return
    
    print("Migrating payment method data to encrypted format...")
    encryption = encryption_utils.DataEncryption()
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the payment_methods table exists
        cursor.execute("PRAGMA table_info(payment_methods)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if not columns:
            print("Payment methods table not found. No migration needed.")
            return
        
        # Add new encrypted column if it doesn't exist
        if 'paypal_email_encrypted' not in columns:
            print("Adding paypal_email_encrypted column...")
            cursor.execute("ALTER TABLE payment_methods ADD COLUMN paypal_email_encrypted TEXT")
        
        # Migrate existing PayPal email data if old column exists
        if 'paypal_email' in columns:
            cursor.execute("SELECT id, paypal_email FROM payment_methods WHERE paypal_email IS NOT NULL")
            payments = cursor.fetchall()
            
            migrated_count = 0
            for payment in payments:
                payment_id, paypal_email = payment
                
                # Encrypt PayPal email
                email_encrypted = encryption.encrypt(paypal_email) if paypal_email else None
                
                # Update the record with encrypted data
                cursor.execute("""
                    UPDATE payment_methods 
                    SET paypal_email_encrypted = ?
                    WHERE id = ?
                """, (email_encrypted, payment_id))
                
                migrated_count += 1
            
            conn.commit()
            print(f"Successfully migrated {migrated_count} payment method records to encrypted format")
        
    except Exception as e:
        print(f"Error during payment data migration: {e}")
        conn.rollback()
    finally:
        conn.close()

def verify_encryption():
    """Verify that encryption is working correctly on migrated data."""
    db_path = 'instance/bookstore.db'
    
    if not os.path.exists(db_path):
        print("Database file not found. Cannot verify encryption.")
        return
    
    print("Verifying encryption integrity...")
    encryption = encryption_utils.DataEncryption()
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test customer data
        cursor.execute("SELECT id, email, email_encrypted FROM customer LIMIT 1")
        result = cursor.fetchone()
        
        if result:
            customer_id, original_email, encrypted_email = result
            if encrypted_email:
                decrypted_email = encryption.decrypt(encrypted_email)
                if original_email == decrypted_email:
                    print("Customer data encryption verification: PASSED")
                else:
                    print(f"Customer data encryption verification: FAILED")
                    print(f"  Original: {original_email}")
                    print(f"  Decrypted: {decrypted_email}")
            else:
                print("No encrypted customer data found to verify")
        
    except Exception as e:
        print(f"Error during encryption verification: {e}")
    finally:
        conn.close()

def main():
    """Main migration function."""
    print("=== Customer Data Encryption Migration ===")
    print("This script will encrypt sensitive customer data in the database.")
    print("A backup will be created before any changes are made.")
    print()
    
    # Create backup
    backup_file = backup_database()
    
    if backup_file:
        print(f"Backup created: {backup_file}")
    
    # Perform migrations
    try:
        migrate_customer_data()
        migrate_purchase_data()
        migrate_payment_data()
        verify_encryption()
        
        print("\n=== Migration Complete ===")
        print("Customer data has been successfully encrypted.")
        print("You can now use the application with encrypted data storage.")
        
    except Exception as e:
        print(f"\n=== Migration Failed ===")
        print(f"Error: {e}")
        if backup_file:
            print(f"You can restore from backup: {backup_file}")

if __name__ == "__main__":
    main()