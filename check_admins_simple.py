import sqlite3

conn = sqlite3.connect('instance/database.db')
cursor = conn.cursor()

cursor.execute('SELECT username, full_name, email, receive_notifications, is_manager FROM user WHERE is_manager = 1')
admins = cursor.fetchall()

print('=== ADMIN USERS EMAIL CONFIGURATION ===')
if admins:
 for row in admins:
 username, full_name, email, notifications, is_manager = row
 print(f'Username: {username}')
 print(f'Name: {full_name or "Not set"}')
 print(f'Email: {email or "NOT SET"}')
 print(f'Notifications: {bool(notifications)}')
 print(f'Can receive notifications: {email and notifications}')
 print()
 
 can_notify = any(row[2] and row[3] for row in admins)
 print(f'Can send notifications to at least one admin: {can_notify}')
 
 if not can_notify:
 print("NO ADMIN CAN RECEIVE EMAIL NOTIFICATIONS!")
 print("Fix needed: Set admin email addresses and enable notifications")
else:
 print("No admin users found!")

conn.close()