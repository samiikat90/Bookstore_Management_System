#!/usr/bin/env python3
"""
Check user table schema and admin user status
"""
import sqlite3
import os

def check_user_schema():
	print("[DEBUG] CHECKING USER TABLE SCHEMA")
	print("=" * 32)
	
try:
	db_path = os.path.join('instance', 'bookstore.db')
	conn = sqlite3.connect(db_path)
	cursor = conn.cursor()
	
	# Get table schema
	cursor.execute("PRAGMA table_info(user)")
	columns = cursor.fetchall()
	
	print("User table columns:")
	for col in columns:
		print(f" {col[1]} ({col[2]})")
	
	print("\nChecking admin user:")
	cursor.execute("SELECT * FROM user WHERE username = 'admin'")
	admin_row = cursor.fetchone()
	
	if admin_row:
		# Get column names
		cursor.execute("PRAGMA table_info(user)")
		col_names = [col[1] for col in cursor.fetchall()]
		
		print("Admin user data:")
		for i, col_name in enumerate(col_names):
			print(f" {col_name}: {admin_row[i]}")
	else:
		print("[ERROR] Admin user not found")
	
	conn.close()
	
except Exception as e:
	print(f"[ERROR] Error: {e}")

if __name__ == "__main__":
	check_user_schema()