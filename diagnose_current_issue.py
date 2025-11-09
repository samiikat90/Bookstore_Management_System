#!/usr/bin/env python3
"""
Comprehensive diagnostic script to check all potential error scenarios
"""
import sys
import os
import sqlite3
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def check_database():
 """Check if database is accessible and has required tables"""
 print("[DEBUG] Checking Database...")
 try:
 # Check if database exists
 db_path = os.path.join('instance', 'bookstore.db')
 if not os.path.exists(db_path):
 print(f"[ERROR] Database not found at: {db_path}")
 return False
 
 # Connect and check tables
 conn = sqlite3.connect(db_path)
 cursor = conn.cursor()
 
 # Check for required tables
 cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
 tables = [row[0] for row in cursor.fetchall()]
 
 required_tables = ['user', 'book', 'purchase', 'order']
 missing_tables = [table for table in required_tables if table not in tables]
 
 if missing_tables:
 print(f"[ERROR] Missing tables: {missing_tables}")
 print(f"[SUCCESS] Available tables: {tables}")
 else:
 print(f"[SUCCESS] All required tables present: {required_tables}")
 
 # Check for recent orders
 try:
 cursor.execute("SELECT COUNT(*) FROM purchase WHERE status='Pending'")
 pending_count = cursor.fetchone()[0]
 print(f"[SUCCESS] Pending orders in database: {pending_count}")
 except Exception as e:
 print(f"[WARNING] Could not check pending orders: {e}")
 
 conn.close()
 return True
 
 except Exception as e:
 print(f"[ERROR] Database error: {e}")
 return False

def check_imports():
 """Check if all required imports are working"""
 print("\n[DEBUG] Checking Imports...")
 try:
 from flask import Flask, request, jsonify
 from flask_sqlalchemy import SQLAlchemy
 from flask_login import LoginManager, current_user
 from flask_wtf.csrf import CSRFProtect, validate_csrf
 print("[SUCCESS] Core Flask imports working")
 
 import smtplib
 from email.mime.text import MIMEText
 from email.mime.multipart import MIMEMultipart
 print("[SUCCESS] Email imports working")
 
 return True
 except ImportError as e:
 print(f"[ERROR] Import error: {e}")
 return False

def check_routes():
 """Check if key routes are defined correctly"""
 print("\n[DEBUG] Checking Route Definitions...")
 try:
 # Import the app to check routes
 from app import app
 
 routes = []
 for rule in app.url_map.iter_rules():
 routes.append(f"{rule.rule} [{', '.join(rule.methods)}]")
 
 # Check for key routes
 key_routes = [
 '/api/update_order',
 '/orders/update',
 '/admin/users',
 '/all_orders'
 ]
 
 found_routes = []
 for route in routes:
 for key in key_routes:
 if key in route:
 found_routes.append(route)
 
 if found_routes:
 print("[SUCCESS] Key routes found:")
 for route in found_routes:
 print(f" {route}")
 else:
 print("[ERROR] Key routes not found")
 print("Available routes:")
 for route in routes[:10]: # Show first 10 routes
 print(f" {route}")
 
 return True
 
 except Exception as e:
 print(f"[ERROR] Route check error: {e}")
 return False

def check_environment():
 """Check environment variables and configurations"""
 print("\n[DEBUG] Checking Environment...")
 
 # Check Python version
 print(f"[SUCCESS] Python version: {sys.version}")
 
 # Check current directory
 print(f"[SUCCESS] Current directory: {os.getcwd()}")
 
 # Check if app directory exists
 app_dir = os.path.join(os.getcwd(), 'app')
 if os.path.exists(app_dir):
 print(f"[SUCCESS] App directory exists: {app_dir}")
 else:
 print(f"[ERROR] App directory not found: {app_dir}")
 
 # Check if templates exist
 templates_dir = os.path.join(app_dir, 'templates')
 if os.path.exists(templates_dir):
 templates = os.listdir(templates_dir)
 print(f"[SUCCESS] Templates directory: {len(templates)} templates found")
 else:
 print(f"[ERROR] Templates directory not found: {templates_dir}")

def main():
 print(" COMPREHENSIVE DIAGNOSTIC CHECK")
 print("=" * 50)
 print(f"Timestamp: {datetime.now()}")
 print()
 
 checks = [
 check_environment(),
 check_imports(),
 check_database(),
 check_routes()
 ]
 
 print("\n" + "=" * 50)
 if all(checks):
 print("[SUCCESS] ALL CHECKS PASSED - System appears healthy!")
 else:
 print("[ERROR] SOME CHECKS FAILED - Issues detected")
 
 print("\nIf you're still experiencing errors, please share:")
 print("1. The exact error message")
 print("2. What action triggers the error")
 print("3. Which page/URL you're on when it happens")

if __name__ == "__main__":
 main()