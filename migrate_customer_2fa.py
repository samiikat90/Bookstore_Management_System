import sqlite3
import os

def add_two_fa_verified_column():
 """Add the two_fa_verified column to the customer table"""
 db_path = os.path.join('instance', 'inventory.db')
 
 if not os.path.exists(db_path):
 print("Database file not found!")
 return False
 
 conn = sqlite3.connect(db_path)
 cursor = conn.cursor()
 
 try:
 # Check if the column already exists
 cursor.execute("PRAGMA table_info(customer)")
 columns = cursor.fetchall()
 column_names = [col[1] for col in columns]
 
 if 'two_fa_verified' in column_names:
 print("Column 'two_fa_verified' already exists in customer table.")
 return True
 
 # Add the new column
 cursor.execute("ALTER TABLE customer ADD COLUMN two_fa_verified BOOLEAN DEFAULT 0")
 conn.commit()
 print("Successfully added 'two_fa_verified' column to customer table.")
 
 # Verify it was added
 cursor.execute("PRAGMA table_info(customer)")
 columns = cursor.fetchall()
 print("\nUpdated customer table structure:")
 for col in columns:
 print(f" {col[1]} ({col[2]})")
 
 return True
 
 except Exception as e:
 print(f"Error adding column: {e}")
 conn.rollback()
 return False
 
 finally:
 conn.close()

if __name__ == "__main__":
 print("Adding two_fa_verified column to customer table...")
 success = add_two_fa_verified_column()
 if success:
 print("\nMigration completed successfully!")
 else:
 print("\nMigration failed!")