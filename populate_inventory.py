#!/usr/bin/env python3
"""
Script to add more diverse sample books with various genres and sample purchases.
"""

import os
import sys
import random
from datetime import datetime, timedelta

# Add the app directory to the path
sys.path.insert(0, 'app')

def populate_diverse_inventory():
    """Add books with diverse genres and sample purchases."""
    
    # Import here to avoid path issues
    from app import app, db, Book, Purchase
    
    with app.app_context():
        print("Adding diverse sample books and purchases...")
        
        # Sample books with various genres
        diverse_books = [
            {
                'isbn': '9780143127741',
                'title': 'Becoming',
                'author': 'Michelle Obama',
                'price': 22.99,
                'quantity': 15,
                'genre': 'Biography',
                'cover_type': 'Hardcover',
                'description': 'The inspiring memoir of former First Lady Michelle Obama.'
            },
            {
                'isbn': '9780525434788',
                'title': 'The Silent Patient',
                'author': 'Alex Michaelides',
                'price': 16.99,
                'quantity': 28,
                'genre': 'Mystery',
                'cover_type': 'Paperback',
                'description': 'A psychological thriller about a woman who refuses to speak.'
            },
            {
                'isbn': '9780735219090',
                'title': 'Where the Forest Meets the Stars',
                'author': 'Glendy Vanderah',
                'price': 15.99,
                'quantity': 22,
                'genre': 'Romance',
                'cover_type': 'Paperback',
                'description': 'A heartwarming story about love, loss, and new beginnings.'
            },
            {
                'isbn': '9781984898111',
                'title': 'The Body Keeps the Score',
                'author': 'Bessel van der Kolk',
                'price': 18.99,
                'quantity': 12,
                'genre': 'Health',
                'cover_type': 'Paperback',
                'description': 'Revolutionary insights into trauma and recovery.'
            },
            {
                'isbn': '9780062316110',
                'title': 'The Power of Now',
                'author': 'Eckhart Tolle',
                'price': 17.50,
                'quantity': 18,
                'genre': 'Self-Help',
                'cover_type': 'Paperback',
                'description': 'A guide to spiritual enlightenment and present-moment awareness.'
            },
            {
                'isbn': '9780525521143',
                'title': 'Untamed',
                'author': 'Glennon Doyle',
                'price': 19.99,
                'quantity': 25,
                'genre': 'Self-Help',
                'cover_type': 'Hardcover',
                'description': 'A memoir about breaking free from societal expectations.'
            },
            {
                'isbn': '9780593133408',
                'title': 'The Invisible Bridge',
                'author': 'Julie Orringer',
                'price': 24.99,
                'quantity': 8,
                'genre': 'History',
                'cover_type': 'Hardcover',
                'description': 'An epic novel set during World War II.'
            },
            {
                'isbn': '9780062457714',
                'title': 'The Little Prince',
                'author': 'Antoine de Saint-Exupéry',
                'price': 12.99,
                'quantity': 35,
                'genre': 'Children',
                'cover_type': 'Paperback',
                'description': 'A beloved tale about friendship and imagination.'
            },
            {
                'isbn': '9781338216677',
                'title': 'Wonder',
                'author': 'R.J. Palacio',
                'price': 14.99,
                'quantity': 30,
                'genre': 'Young Adult',
                'cover_type': 'Paperback',
                'description': 'An inspiring story about kindness and acceptance.'
            },
            {
                'isbn': '9780316769488',
                'title': 'The Art of War',
                'author': 'Sun Tzu',
                'price': 13.99,
                'quantity': 20,
                'genre': 'Reference',
                'cover_type': 'Paperback',
                'description': 'Ancient Chinese military strategy and philosophy.'
            }
        ]
        
        books_added = 0
        for book_data in diverse_books:
            # Check if book already exists
            existing_book = Book.query.get(book_data['isbn'])
            if not existing_book:
                try:
                    book = Book(
                        isbn=book_data['isbn'],
                        title=book_data['title'],
                        author=book_data['author'],
                        price=book_data['price'],
                        quantity=book_data['quantity'],
                        in_stock=book_data['quantity'] > 0,
                        genre=book_data['genre'],
                        cover_type=book_data['cover_type'],
                        description=book_data['description']
                    )
                    db.session.add(book)
                    books_added += 1
                    print(f"Added book: {book_data['title']} ({book_data['genre']})")
                except Exception as e:
                    print(f"Error adding book {book_data['title']}: {e}")
        
        # Add sample purchases for the new books
        customer_names = [
            "Alice Johnson", "Bob Smith", "Carol Williams", "David Brown",
            "Emma Davis", "Frank Miller", "Grace Wilson", "Henry Moore",
            "Ivy Taylor", "Jack Anderson", "Kate Thomas", "Liam Jackson"
        ]
        
        statuses = ['Pending', 'Confirmed', 'Processing', 'Shipped', 'Delivered']
        
        purchases_added = 0
        all_books = Book.query.all()
        
        for i in range(15):  # Add 15 new sample purchases
            try:
                book = random.choice(all_books)
                customer = random.choice(customer_names)
                
                purchase = Purchase(
                    customer_name=customer,
                    customer_email=f"{customer.lower().replace(' ', '.')}@email.com",
                    customer_phone=f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                    customer_address=f"{random.randint(100, 9999)} {random.choice(['Main St', 'Oak Ave', 'Elm St', 'Pine Rd', 'Cedar Ln'])}, {random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'])}, {random.choice(['NY', 'CA', 'IL', 'TX', 'AZ'])} {random.randint(10000, 99999)}",
                    book_isbn=book.isbn,
                    quantity=random.randint(1, 3),
                    status=random.choice(statuses),
                    timestamp=datetime.now() - timedelta(days=random.randint(0, 60)),
                    source='Online'
                )
                db.session.add(purchase)
                purchases_added += 1
            except Exception as e:
                print(f"Error creating sample purchase {i}: {e}")
        
        try:
            db.session.commit()
            print(f"\nSuccessfully added:")
            print(f"  {books_added} new books")
            print(f"  {purchases_added} new purchases")
            
            # Show final counts
            total_books = Book.query.count()
            total_purchases = Purchase.query.count()
            
            print(f"\nTotal database contents:")
            print(f"  Books: {total_books}")
            print(f"  Purchases: {total_purchases}")
            
            # Show genre distribution
            from sqlalchemy import func
            genre_counts = db.session.query(Book.genre, func.count(Book.genre)).group_by(Book.genre).all()
            print(f"\nBooks by genre:")
            for genre, count in genre_counts:
                print(f"  {genre}: {count} books")
                
        except Exception as e:
            db.session.rollback()
            print(f"Error saving to database: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("POPULATING DIVERSE INVENTORY")
    print("=" * 60)
    
    populate_diverse_inventory()
    
    print("=" * 60)
    print("Inventory population complete!")
    print("You should now see diverse genres and purchases in your bookstore.")
    print("=" * 60)