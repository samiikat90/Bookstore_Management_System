#!/usr/bin/env python3

"""
Migration script to add password reset token fields to User and Customer tables.
"""

import sqlite3
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def add_reset_token_fields():
    """Add reset token fields to User and Customer tables."""
    db_path = os.path.join('instance', 'inventory.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check and add fields to User table
        cursor.execute("PRAGMA table_info(user)")
        user_columns = [column[1] for column in cursor.fetchall()]
        
        print("Updating User table...")
        if 'reset_token' not in user_columns:
            cursor.execute("ALTER TABLE user ADD COLUMN reset_token VARCHAR(100)")
            print("Added reset_token column to user table")
        else:
            print("reset_token column already exists in user table")
            
        if 'reset_token_expires' not in user_columns:
            cursor.execute("ALTER TABLE user ADD COLUMN reset_token_expires DATETIME")
            print("Added reset_token_expires column to user table")
        else:
            print("reset_token_expires column already exists in user table")
        
        # Check and add fields to Customer table
        cursor.execute("PRAGMA table_info(customer)")
        customer_columns = [column[1] for column in cursor.fetchall()]
        
        print("Updating Customer table...")
        if 'reset_token' not in customer_columns:
            cursor.execute("ALTER TABLE customer ADD COLUMN reset_token VARCHAR(100)")
            print("Added reset_token column to customer table")
        else:
            print("reset_token column already exists in customer table")
            
        if 'reset_token_expires' not in customer_columns:
            cursor.execute("ALTER TABLE customer ADD COLUMN reset_token_expires DATETIME")
            print("Added reset_token_expires column to customer table")
        else:
            print("reset_token_expires column already exists in customer table")
        
        conn.commit()
        conn.close()
        
        print("Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error during migration: {e}")
        return False

if __name__ == "__main__":
    print("Starting password reset token migration...")
    success = add_reset_token_fields()
    
    if success:
        print("Migration completed successfully!")
        
        # Verify the changes
        print("\nVerifying the migration...")
        try:
            db_path = os.path.join('instance', 'inventory.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("PRAGMA table_info(user)")
            user_columns = cursor.fetchall()
            print('User table columns:')
            for col in user_columns:
                print(f'  {col[1]} ({col[2]})')
            
            print()
            cursor.execute("PRAGMA table_info(customer)")
            customer_columns = cursor.fetchall()
            print('Customer table columns:')
            for col in customer_columns:
                print(f'  {col[1]} ({col[2]})')
                
            conn.close()
        except Exception as e:
            print(f"Error verifying migration: {e}")
    else:
        print("Migration failed!")