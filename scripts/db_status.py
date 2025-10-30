#!/usr/bin/env python3
"""
Quick database status check script.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.app import app, db, Book, User, Purchase

def main():
    with app.app_context():
        db.create_all()
        
        print("=" * 50)
        print("DATABASE STATUS")
        print("=" * 50)
        
        # Books
        book_count = Book.query.count()
        print(f"📚 Books in inventory: {book_count}")
        if book_count > 0:
            in_stock = Book.query.filter_by(in_stock=True).count()
            print(f"   - In stock: {in_stock}")
            print(f"   - Out of stock: {book_count - in_stock}")
        
        # Users
        user_count = User.query.filter_by(is_manager=True).count()
        print(f"👥 Admin users: {user_count}")
        if user_count > 0:
            users = User.query.filter_by(is_manager=True).all()
            print("   Admin accounts:")
            for user in users[:3]:  # Show first 3
                print(f"   - {user.username} ({user.email})")
            if user_count > 3:
                print(f"   - ... and {user_count - 3} more")
        
        # Purchases
        purchase_count = Purchase.query.count()
        print(f"🛒 Total orders: {purchase_count}")
        if purchase_count > 0:
            pending = Purchase.query.filter_by(status='Pending').count()
            processing = Purchase.query.filter_by(status='Processing').count()
            completed = Purchase.query.filter_by(status='Completed').count()
            print(f"   - Pending: {pending}")
            print(f"   - Processing: {processing}")
            print(f"   - Completed: {completed}")
        
        print("=" * 50)
        
        if book_count == 0 or user_count == 0:
            print("⚠️  Missing data! Run: python scripts/setup_database.py")
        else:
            print("✅ Database ready! Start app: python app/app.py")
        
        print("=" * 50)

if __name__ == "__main__":
    main()