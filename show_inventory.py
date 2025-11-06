#!/usr/bin/env python3
"""
Script to show what should be visible in the inventory and purchases.
"""

import sys
sys.path.insert(0, 'app')

def show_inventory_summary():
    """Show what should be visible in the inventory."""
    
    from app import app, db, Book, Purchase
    from sqlalchemy import func
    
    with app.app_context():
        print("CURRENT INVENTORY SUMMARY")
        print("=" * 50)
        
        # Show total counts
        total_books = Book.query.count()
        total_purchases = Purchase.query.count()
        
        print(f"Total Books: {total_books}")
        print(f"Total Purchases: {total_purchases}")
        print()
        
        # Show books by genre
        print("BOOKS BY GENRE:")
        print("-" * 30)
        genre_counts = db.session.query(Book.genre, func.count(Book.genre)).group_by(Book.genre).order_by(Book.genre).all()
        for genre, count in genre_counts:
            print(f"{genre:15} : {count} books")
        print()
        
        # Show recent purchases
        print("RECENT PURCHASES:")
        print("-" * 30)
        recent_purchases = Purchase.query.order_by(Purchase.timestamp.desc()).limit(10).all()
        for purchase in recent_purchases:
            book = Book.query.get(purchase.book_isbn)
            book_title = book.title if book else "Unknown Book"
            print(f"{purchase.customer_name:20} | {book_title:25} | {purchase.status:10} | {purchase.timestamp.strftime('%Y-%m-%d')}")
        
        print()
        print("=" * 50)
        print("What you should see in the web interface:")
        print("1. Inventory page should show books from all genres")
        print("2. Genre filter should show all the genres listed above") 
        print("3. Purchases/Orders page should show the recent purchases")
        print("4. You can filter books by genre in the catalog")
        print("=" * 50)

if __name__ == "__main__":
    show_inventory_summary()