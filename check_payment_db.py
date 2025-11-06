#!/usr/bin/env python3
"""
Database check script to verify payment-related tables exist
"""

import sqlite3
import os

def check_database():
    db_path = os.path.join('instance', 'inventory.db')
    
    if not os.path.exists(db_path):
        print("Database does not exist at:", db_path)
        return
    
    print(f"Checking database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if payment_methods table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='payment_methods';")
    result = cursor.fetchone()
    
    if result:
        print("SUCCESS: payment_methods table exists")
        
        # Check the structure
        cursor.execute("PRAGMA table_info(payment_methods);")
        columns = cursor.fetchall()
        print("  Columns:")
        for col in columns:
            print(f"    {col[1]} {col[2]}")
    else:
        print("ERROR: payment_methods table does not exist")
    
    # Check if purchases table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='purchases';")
    result = cursor.fetchone()
    
    if result:
        print("SUCCESS: purchases table exists")
        
        # Check the structure
        cursor.execute("PRAGMA table_info(purchases);")
        columns = cursor.fetchall()
        print("  Columns:")
        for col in columns:
            print(f"    {col[1]} {col[2]}")
    else:
        print("ERROR: purchases table does not exist")
    
    # Check all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"\nAll tables in database: {[table[0] for table in tables]}")
    
    conn.close()

if __name__ == "__main__":
    check_database()