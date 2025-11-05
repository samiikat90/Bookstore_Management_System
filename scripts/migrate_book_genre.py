#!/usr/bin/env python3

"""
Migration script to add the missing 'genre' column to the book table.
"""

import sqlite3
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from app.app import app

def add_genre_column():
    """Add the genre column to the book table."""
    db_path = os.path.join('instance', 'inventory.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if genre column already exists
        cursor.execute("PRAGMA table_info(book)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'genre' in columns:
            print("Genre column already exists in book table.")
            conn.close()
            return True
            
        # Add the genre column
        print("Adding genre column to book table...")
        cursor.execute("ALTER TABLE book ADD COLUMN genre VARCHAR(100)")
        
        conn.commit()
        conn.close()
        
        print("Successfully added genre column to book table.")
        return True
        
    except Exception as e:
        print(f"Error adding genre column: {e}")
        return False

if __name__ == "__main__":
    print("Starting database migration...")
    success = add_genre_column()
    
    if success:
        print("Migration completed successfully!")
        
        # Verify the change
        print("\nVerifying the migration...")
        with app.app_context():
            from sqlalchemy import inspect
            inspector = inspect(app.extensions['sqlalchemy'].db.engine)
            columns = inspector.get_columns('book')
            print('Book table columns after migration:')
            for col in columns:
                print(f'  {col["name"]} ({col["type"]})')
    else:
        print("Migration failed!")