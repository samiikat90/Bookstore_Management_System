import sqlite3
import os
from werkzeug.security import check_password_hash

def check_customer_credentials():
	"""Check customer login credentials in the database"""
	db_path = os.path.join('instance', 'inventory.db')
	
	if not os.path.exists(db_path):
		print("Database file not found!")
		return
	
	conn = sqlite3.connect(db_path)
	cursor = conn.cursor()
	
	try:
		# Check for sampleuser2
		cursor.execute("SELECT id, username, password_hash, email_encrypted, full_name, is_active FROM customer WHERE username = ?", ('sampleuser2',))
		user = cursor.fetchone()
		
		if user:
			print(f"Found user: {user[1]} (ID: {user[0]})")
			print(f"Full name: {user[4]}")
			print(f"Email encrypted: {user[3][:30]}...")
			print(f"Password hash: {user[2][:50]}...")
			print(f"Is active: {user[5]}")
			
			# Test the password
			test_password = "password123"
			if check_password_hash(user[2], test_password):
				print(f"[SUCCESS] Password '{test_password}' is CORRECT")
			else:
				print(f"[FAILED] Password '{test_password}' is INCORRECT")
			
			# Try some other common passwords
			test_passwords = ["123", "password", "sampleuser2", "Password123"]
			for pwd in test_passwords:
				if check_password_hash(user[2], pwd):
					print(f"[SUCCESS] Found working password: '{pwd}'")
					break
			else:
				print("[FAILED] None of the common passwords work")
		else:
			print("[FAILED] User 'sampleuser2' not found!")
		
		# Show all customers
		cursor.execute("SELECT id, username, full_name FROM customer")
		all_customers = cursor.fetchall()
		print(f"\nAll customers in database:")
		for customer in all_customers:
			print(f" ID: {customer[0]}, Username: '{customer[1]}', Name: {customer[2]}")
		
	except Exception as e:
		print(f"Error: {e}")
	
	finally:
		conn.close()

if __name__ == "__main__":
	check_customer_credentials()