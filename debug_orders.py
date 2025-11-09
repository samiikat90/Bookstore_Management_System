import sqlite3
import os

# Connect directly to the database file
db_path = os.path.join('instance', 'inventory.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== PURCHASES TABLE ANALYSIS ===")

# Get all purchases and their statuses
cursor.execute("SELECT id, customer_name, book_isbn, quantity, status, timestamp FROM purchases ORDER BY timestamp DESC")
all_purchases = cursor.fetchall()

print(f"Total purchases in database: {len(all_purchases)}")
print("\nAll purchases:")
for purchase in all_purchases:
 print(f"ID: {purchase[0]}, Customer: {purchase[1]}, Book: {purchase[2]}, Qty: {purchase[3]}, Status: '{purchase[4]}', Time: {purchase[5]}")

# Count by status
cursor.execute("SELECT status, COUNT(*) FROM purchases GROUP BY status")
status_counts = cursor.fetchall()

print(f"\nStatus counts:")
for status, count in status_counts:
 print(f" '{status}': {count}")

# Check specifically for 'Pending' status
cursor.execute("SELECT COUNT(*) FROM purchases WHERE status = 'Pending'")
pending_count = cursor.fetchone()[0]
print(f"\nPending orders (exact match): {pending_count}")

# Check for any status variations (including case sensitivity)
cursor.execute("SELECT DISTINCT status FROM purchases")
all_statuses = cursor.fetchall()
print(f"\nAll unique status values in purchases table:")
for status in all_statuses:
 print(f" '{status[0]}' (length: {len(status[0])})")

# Check for any whitespace issues
cursor.execute("SELECT status FROM purchases WHERE TRIM(status) != status")
whitespace_issues = cursor.fetchall()
if whitespace_issues:
 print(f"\nStatus values with whitespace issues:")
 for status in whitespace_issues:
 print(f" '{status[0]}' (repr: {repr(status[0])})")
else:
 print("\nNo whitespace issues found in status values")

conn.close()