#!/usr/bin/env python3
"""
Temporarily disable 2FA for admin user to test order status updates
"""
import sys
import os
import sqlite3

def disable_admin_2fa():
 print(" DISABLING 2FA FOR ADMIN USER")
 print("=" * 35)
 
 try:
 # Connect to database
 db_path = os.path.join('instance', 'bookstore.db')
 if not os.path.exists(db_path):
 print("[ERROR] Database not found")
 return False
 
 conn = sqlite3.connect(db_path)
 cursor = conn.cursor()
 
 # Check current admin user 2FA status
 cursor.execute("SELECT username, two_fa_code, two_fa_verified, is_manager FROM user WHERE username = 'admin'")
 admin_user = cursor.fetchone()
 
 if admin_user:
 username, two_fa_code, two_fa_verified, is_manager = admin_user
 print(f"Current admin user status:")
 print(f" Username: {username}")
 print(f" 2FA Code: {two_fa_code}")
 print(f" 2FA Verified: {two_fa_verified}")
 print(f" Is Manager: {is_manager}")
 
 if two_fa_code and not two_fa_verified:
 print("\n Clearing 2FA code for admin user...")
 cursor.execute("""
 UPDATE user 
 SET two_fa_code = NULL, two_fa_expires = NULL, two_fa_verified = 0
 WHERE username = 'admin'
 """)
 conn.commit()
 print("[SUCCESS] 2FA code cleared for admin user")
 elif two_fa_code and two_fa_verified:
 print("[SUCCESS] 2FA already verified")
 else:
 print("[SUCCESS] No 2FA code present")
 
 # Ensure user is a manager
 if not is_manager:
 print("\n Setting admin user as manager...")
 cursor.execute("UPDATE user SET is_manager = 1 WHERE username = 'admin'")
 conn.commit()
 print("[SUCCESS] Admin user set as manager")
 else:
 print("[SUCCESS] Admin user already has manager privileges")
 
 else:
 print("[ERROR] Admin user not found in database")
 return False
 
 conn.close()
 print("\n Admin user configured for testing!")
 print("You can now login as admin without 2FA and test order status updates.")
 return True
 
 except Exception as e:
 print(f"[ERROR] Error: {e}")
 return False

if __name__ == "__main__":
 disable_admin_2fa()