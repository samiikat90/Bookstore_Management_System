import sqlite3
import os
from datetime import datetime

# Connect directly to the database file
db_path = os.path.join('instance', 'inventory.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create a couple of test pending orders
test_orders = [
 ('Test Customer 1', 'encrypted_email1', 'encrypted_phone1', 'encrypted_address1', '9781234567891', 1, 'Pending', datetime.now().isoformat(), 'purchase'),
 ('Test Customer 2', 'encrypted_email2', 'encrypted_phone2', 'encrypted_address2', '9781234567892', 2, 'Pending', datetime.now().isoformat(), 'purchase')
]

for order in test_orders:
 cursor.execute("""
 INSERT INTO purchases (customer_name, customer_email_encrypted, customer_phone_encrypted, 
 customer_address_encrypted, book_isbn, quantity, status, timestamp, source)
 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
 """, order)

conn.commit()

# Verify the new orders were added
cursor.execute("SELECT id, customer_name, book_isbn, quantity, status FROM purchases WHERE status = 'Pending'")
pending_orders = cursor.fetchall()

print(f"Created {len(pending_orders)} pending orders:")
for order in pending_orders:
 print(f" ID: {order[0]}, Customer: {order[1]}, Book: {order[2]}, Qty: {order[3]}, Status: {order[4]}")

# Check total count
cursor.execute("SELECT COUNT(*) FROM purchases WHERE status = 'Pending'")
pending_count = cursor.fetchone()[0]
print(f"\nTotal pending orders: {pending_count}")

conn.close()
print("\nTest pending orders created successfully!")