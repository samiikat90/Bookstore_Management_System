import sqlite3
import os

def check_customer_table():
	"""Check the customer table structure"""
	db_path = os.path.join('instance', 'inventory.db')
	
	if not os.path.exists(db_path):
		print("Database file not found!")
		return
	
	conn = sqlite3.connect(db_path)
	cursor = conn.cursor()
	
	try:
		# Check table structure
		cursor.execute("PRAGMA table_info(customer)")
		columns = cursor.fetchall()
		print("Customer table structure:")
		for col in columns:
			print(f" {col[0]}: {col[1]} ({col[2]}) - NotNull: {col[3]}, Default: {col[4]}")
		
		# Check if there are any customers
		cursor.execute("SELECT COUNT(*) FROM customer")
		count = cursor.fetchone()[0]
		print(f"\nTotal customers in database: {count}")
		
		# Show sample customer data
		if count > 0:
			cursor.execute("SELECT id, username, email_encrypted, two_fa_verified FROM customer LIMIT 3")
			customers = cursor.fetchall()
			print("\nSample customer data:")
			for customer in customers:
				print(f" ID: {customer[0]}, Username: {customer[1]}, Email: {customer[2][:20]}..., 2FA: {customer[3]}")
		
	except Exception as e:
		print(f"Error checking table: {e}")
		
	finally:
		conn.close()

if __name__ == "__main__":
 check_customer_table()