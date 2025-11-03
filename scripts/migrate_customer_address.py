#!/usr/bin/env python3
"""
Database migration script to add new address fields to Customer table.

This script adds the new address columns (address_line1, address_line2, city, state, zip_code)
to the existing Customer table without losing existing data.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.app import app, db, Customer
from sqlalchemy import text

def migrate_customer_address_fields():
    """Add new address fields to Customer table."""
    
    with app.app_context():
        try:
            # Check if the new columns already exist
            result = db.session.execute(text("PRAGMA table_info(customer)"))
            columns = [row[1] for row in result.fetchall()]
            
            new_columns = ['address_line1', 'address_line2', 'city', 'state', 'zip_code']
            columns_to_add = [col for col in new_columns if col not in columns]
            
            if not columns_to_add:
                print("✓ All address columns already exist in the database.")
                return
            
            print(f"Adding new address columns: {columns_to_add}")
            
            # Add new columns one by one
            for column in columns_to_add:
                if column == 'address_line1':
                    sql = "ALTER TABLE customer ADD COLUMN address_line1 VARCHAR(255)"
                elif column == 'address_line2':
                    sql = "ALTER TABLE customer ADD COLUMN address_line2 VARCHAR(255)"
                elif column == 'city':
                    sql = "ALTER TABLE customer ADD COLUMN city VARCHAR(100)"
                elif column == 'state':
                    sql = "ALTER TABLE customer ADD COLUMN state VARCHAR(50)"
                elif column == 'zip_code':
                    sql = "ALTER TABLE customer ADD COLUMN zip_code VARCHAR(20)"
                
                db.session.execute(text(sql))
                print(f"✓ Added column: {column}")
            
            db.session.commit()
            print("✓ Database migration completed successfully!")
            
            # Show current customer table structure
            result = db.session.execute(text("PRAGMA table_info(customer)"))
            print("\nCurrent customer table structure:")
            for row in result.fetchall():
                print(f"  - {row[1]} ({row[2]})")
                
        except Exception as e:
            db.session.rollback()
            print(f"✗ Migration failed: {e}")
            raise

if __name__ == "__main__":
    print("Starting Customer Address Fields Migration...")
    migrate_customer_address_fields()
    print("Migration completed!")