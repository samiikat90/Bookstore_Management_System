#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app import app, db, Purchase, Customer

def check_order_sources():
 """Check if recent orders came from guest checkout or customer checkout."""
 with app.app_context():
 print("Analyzing Order Sources (Guest vs Customer Checkout)")
 print("=" * 60)
 
 # Get all recent purchases
 all_purchases = Purchase.query.order_by(Purchase.timestamp.desc()).limit(10).all()
 
 # Get all registered customers
 customers = {c.full_name: c for c in Customer.query.all()}
 customer_emails = {c.email: c for c in Customer.query.all()}
 
 print(f"Registered customers: {len(customers)}")
 for name, customer in customers.items():
 print(f" - {name} ({customer.email})")
 
 print(f"\\nAnalyzing {len(all_purchases)} recent orders:")
 print("-" * 40)
 
 guest_orders = 0
 customer_orders = 0
 
 for purchase in all_purchases:
 customer_name = purchase.customer_name
 customer_email = purchase.customer_email
 
 # Check if this matches a registered customer
 is_registered = False
 if customer_name in customers:
 registered_customer = customers[customer_name]
 if customer_email == registered_customer.email:
 is_registered = True
 elif customer_email and customer_email in customer_emails:
 is_registered = True
 
 order_type = "CUSTOMER" if is_registered else "GUEST"
 if is_registered:
 customer_orders += 1
 else:
 guest_orders += 1
 
 print(f" ID {purchase.id}: {customer_name} ({customer_email}) - {order_type} - {purchase.status}")
 
 print(f"\\nOrder Type Summary:")
 print(f" Guest orders: {guest_orders}")
 print(f" Customer orders: {customer_orders}")
 
 # Check which notification function should have been called
 print(f"\\nNotification Analysis:")
 print(f" Guest orders should use: send_admin_notification() (simple text)")
 print(f" Customer orders should use: send_admin_order_notification() (rich HTML)")
 
 if guest_orders > 0:
 print(f"\\n[WARNING] If {guest_orders} guest orders didn't send admin notifications,")
 print(f" check the guest checkout code around line 1787 in app.py")
 
 if customer_orders > 0:
 print(f"\\n[WARNING] If {customer_orders} customer orders didn't send admin notifications,")
 print(f" check the customer checkout code around line 4123 in app.py")

if __name__ == "__main__":
 check_order_sources()