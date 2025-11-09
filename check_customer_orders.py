import sqlite3
import os
import sys
sys.path.append('app')
from app import encryption

def check_customer_orders():
	"""Check order history for sampleuser2"""
	db_path = os.path.join('instance', 'inventory.db')
	
	if not os.path.exists(db_path):
		print("Database file not found!")
		return
	
	conn = sqlite3.connect(db_path)
	cursor = conn.cursor()
	
	try:
		# First, get the customer info
		cursor.execute("SELECT id, username, email_encrypted, full_name FROM customer WHERE username = ?", ('sampleuser2',))
		customer = cursor.fetchone()
		
		if customer:
			print(f"Found customer: {customer[1]} (ID: {customer[0]})")
			print(f"Full name: {customer[3]}")
			
			# Decrypt the email to match against orders
			try:
				decrypted_email = encryption.decrypt(customer[2])
				print(f"Customer email: {decrypted_email}")
			except Exception as e:
				print(f"Could not decrypt email: {e}")
				decrypted_email = None
			
			# Check the purchases table for orders
			print("\n=== Checking PURCHASES table ===")
			cursor.execute("SELECT id, customer_name, book_isbn, quantity, status, timestamp, customer_email_encrypted FROM purchases")
			all_purchases = cursor.fetchall()
			
			print(f"Total purchases: {len(all_purchases)}")
			
			# Look for orders by customer name or email
			matching_orders = []
			for purchase in all_purchases:
				purchase_id, customer_name, book_isbn, quantity, status, timestamp, email_encrypted = purchase
				
				# Try to decrypt the email from the purchase
				try:
					purchase_email = encryption.decrypt(email_encrypted) if email_encrypted else None
				except:
					purchase_email = None
				
				# Check if this order belongs to our customer
				name_match = customer_name and customer[3] and customer_name.lower() == customer[3].lower()
				email_match = purchase_email and decrypted_email and purchase_email.lower() == decrypted_email.lower()
				
				if name_match or email_match:
					matching_orders.append(purchase)
					print(f"[SUCCESS] Found order: ID {purchase_id}, Book: {book_isbn}, Status: {status}, Date: {timestamp}")
					print(f" Customer name: {customer_name}, Email match: {email_match}, Name match: {name_match}")
				else:
					print(f" Order ID {purchase_id}: Name='{customer_name}' vs '{customer[3]}', Email mismatch")
			
			# Check the order table as well
			print("\n=== Checking ORDER table ===")
			cursor.execute("SELECT id, customer_name, customer_email, book_isbn, quantity, status, timestamp, customer_id FROM `order`")
			order_results = cursor.fetchall()
			
			print(f"Total orders in 'order' table: {len(order_results)}")
			for order in order_results:
				order_id, customer_name, customer_email, book_isbn, quantity, status, timestamp, customer_id = order
				
				# Check if this order belongs to our customer
				id_match = customer_id == customer[0]
				name_match = customer_name and customer[3] and customer_name.lower() == customer[3].lower()
				email_match = customer_email and decrypted_email and customer_email.lower() == decrypted_email.lower()
				
				if id_match or name_match or email_match:
					print(f"[SUCCESS] Found order: ID {order_id}, Book: {book_isbn}, Status: {status}, Date: {timestamp}")
					print(f" Customer ID match: {id_match}, Name match: {name_match}, Email match: {email_match}")
			
			if not matching_orders and not order_results:
				print(f"\n[FAILED] No orders found for customer {customer[1]}")
			
			# Show all purchases for debugging
			print("\nAll purchases in database:")
			for i, purchase in enumerate(all_purchases):
				try:
					email = encryption.decrypt(purchase[6]) if purchase[6] else "No email"
				except:
					email = "Could not decrypt"
				print(f" {i+1}. ID: {purchase[0]}, Name: '{purchase[1]}', Email: {email}, Book: {purchase[2]}")
		
		else:
			print("[FAILED] Customer 'sampleuser2' not found!")
	
	except Exception as e:
		print(f"Error: {e}")
	
	finally:
		conn.close()

if __name__ == "__main__":
 check_customer_orders()