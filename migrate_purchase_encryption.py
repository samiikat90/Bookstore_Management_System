#!/usr/bin/env python3
"""
Database migration script to add encrypted columns to the Purchase table.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def migrate_database():
    """Add encrypted columns to the Purchase table."""
    
    import sqlite3
    
    # Check if database exists
    db_path = 'instance/inventory.db'
    if not os.path.exists(db_path):
        print(f'Database not found at: {db_path}')
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if the encrypted columns already exist
        cursor.execute("PRAGMA table_info(purchases)")
        columns = cursor.fetchall()
        existing_columns = [col[1] for col in columns]
        
        print(f"Existing columns in purchases table: {existing_columns}")
        
        # Add encrypted columns if they don't exist
        columns_to_add = [
            ('customer_email_encrypted', 'TEXT'),
            ('customer_phone_encrypted', 'TEXT'), 
            ('customer_address_encrypted', 'TEXT')
        ]
        
        for column_name, column_type in columns_to_add:
            if column_name not in existing_columns:
                try:
                    cursor.execute(f'ALTER TABLE purchases ADD COLUMN {column_name} {column_type}')
                    print(f'Added column: {column_name}')
                except Exception as e:
                    print(f'Error adding column {column_name}: {e}')
            else:
                print(f'Column {column_name} already exists')
        
        conn.commit()
        print('Database migration completed successfully!')
        return True
        
    except Exception as e:
        print(f'Error during migration: {e}')
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("DATABASE MIGRATION - Adding Encrypted Columns")
    print("=" * 60)
    
    success = migrate_database()
    
    if success:
        print("Migration completed successfully!")
        print("You can now start the application.")
    else:
        print("Migration failed! Please check the errors above.")
    
    print("=" * 60)