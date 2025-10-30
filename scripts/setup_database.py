#!/usr/bin/env python3
"""
Database setup script that automatically populates the database with sample data.
This script will create sample books, users, and purchases if they don't exist.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.app import app, db, Book, User, Purchase
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

def setup_sample_books():
    """Create sample books if inventory is empty."""
    print("Setting up sample books...")
    
    if Book.query.count() > 0:
        print("Books already exist in database. Skipping book creation.")
        return
    
    sample_books = [
        {
            'isbn': '9780061120084',
            'title': 'To Kill a Mockingbird',
            'author': 'Harper Lee',
            'price': 12.99,
            'quantity': 25,
            'cover_type': 'Paperback',
            'description': 'A gripping tale of racial injustice and childhood innocence in the American South.'
        },
        {
            'isbn': '9780451524935',
            'title': '1984',
            'author': 'George Orwell',
            'price': 13.99,
            'quantity': 30,
            'cover_type': 'Paperback',
            'description': 'A dystopian social science fiction novel about totalitarian control.'
        },
        {
            'isbn': '9780062315007',
            'title': 'The Alchemist',
            'author': 'Paulo Coelho',
            'price': 14.99,
            'quantity': 20,
            'cover_type': 'Paperback',
            'description': 'A philosophical book about following your dreams and personal legend.'
        },
        {
            'isbn': '9780553380163',
            'title': 'A Brief History of Time',
            'author': 'Stephen Hawking',
            'price': 16.99,
            'quantity': 15,
            'cover_type': 'Paperback',
            'description': 'An accessible introduction to cosmology and the nature of time.'
        },
        {
            'isbn': '9780140449136',
            'title': 'Pride and Prejudice',
            'author': 'Jane Austen',
            'price': 11.99,
            'quantity': 22,
            'cover_type': 'Paperback',
            'description': 'A romantic novel about manners, upbringing, and marriage in Georgian England.'
        },
        {
            'isbn': '9780547928227',
            'title': 'The Hobbit',
            'author': 'J.R.R. Tolkien',
            'price': 15.99,
            'quantity': 18,
            'cover_type': 'Paperback',
            'description': 'A fantasy adventure about Bilbo Baggins and his unexpected journey.'
        },
        {
            'isbn': '9780679783268',
            'title': 'Crime and Punishment',
            'author': 'Fyodor Dostoevsky',
            'price': 17.99,
            'quantity': 12,
            'cover_type': 'Paperback',
            'description': 'A psychological novel about guilt, redemption, and moral philosophy.'
        },
        {
            'isbn': '9780061122415',
            'title': 'Where the Crawdads Sing',
            'author': 'Delia Owens',
            'price': 18.99,
            'quantity': 35,
            'cover_type': 'Hardcover',
            'description': 'A coming-of-age mystery set in the marshlands of North Carolina.'
        },
        {
            'isbn': '9780735224292',
            'title': 'Atomic Habits',
            'author': 'James Clear',
            'price': 19.99,
            'quantity': 40,
            'cover_type': 'Hardcover',
            'description': 'A practical guide to building good habits and breaking bad ones.'
        },
        {
            'isbn': '9780525559474',
            'title': 'Educated',
            'author': 'Tara Westover',
            'price': 16.99,
            'quantity': 28,
            'cover_type': 'Paperback',
            'description': 'A memoir about education, family, and the struggle for self-invention.'
        },
        {
            'isbn': '9780142424179',
            'title': 'The Fault in Our Stars',
            'author': 'John Green',
            'price': 12.99,
            'quantity': 32,
            'cover_type': 'Paperback',
            'description': 'A heart-wrenching romance between two teenagers with cancer.'
        },
        {
            'isbn': '9780316769174',
            'title': 'The Catcher in the Rye',
            'author': 'J.D. Salinger',
            'price': 13.99,
            'quantity': 24,
            'cover_type': 'Paperback',
            'description': 'A coming-of-age story about teenage rebellion and alienation.'
        },
        {
            'isbn': '9780062073488',
            'title': 'And Then There Were None',
            'author': 'Agatha Christie',
            'price': 14.99,
            'quantity': 26,
            'cover_type': 'Paperback',
            'description': 'A classic mystery novel about ten strangers trapped on an island.'
        },
        {
            'isbn': '9780062316097',
            'title': 'Sapiens',
            'author': 'Yuval Noah Harari',
            'price': 21.99,
            'quantity': 33,
            'cover_type': 'Hardcover',
            'description': 'A brief history of humankind from the Stone Age to the present.'
        },
        {
            'isbn': '9780593133408',
            'title': 'The Seven Husbands of Evelyn Hugo',
            'author': 'Taylor Jenkins Reid',
            'price': 17.99,
            'quantity': 29,
            'cover_type': 'Paperback',
            'description': 'A captivating novel about a reclusive Hollywood icon and her secrets.'
        }
    ]
    
    created_count = 0
    for book_data in sample_books:
        try:
            book = Book(
                isbn=book_data['isbn'],
                title=book_data['title'],
                author=book_data['author'],
                price=book_data['price'],
                quantity=book_data['quantity'],
                in_stock=book_data['quantity'] > 0,
                cover_type=book_data['cover_type'],
                description=book_data['description']
            )
            db.session.add(book)
            created_count += 1
        except Exception as e:
            print(f"Error creating book {book_data['title']}: {e}")
    
    try:
        db.session.commit()
        print(f"Successfully created {created_count} sample books!")
    except Exception as e:
        db.session.rollback()
        print(f"Error saving books to database: {e}")

def setup_admin_users():
    """Create admin users if none exist."""
    print("Setting up admin users...")
    
    if User.query.filter_by(is_manager=True).count() > 0:
        print("Admin users already exist. Skipping user creation.")
        return
    
    admin_users = [
        {
            'username': 'admin',
            'password': 'admin123',
            'email': 'admin@plottwist.com',
            'full_name': 'System Administrator',
            'receive_notifications': True
        },
        {
            'username': 'manager1',
            'password': 'admin123',
            'email': 'manager1@plottwist.com',
            'full_name': 'Store Manager One',
            'receive_notifications': True
        },
        {
            'username': 'manager2',
            'password': 'admin123',
            'email': 'manager2@plottwist.com',
            'full_name': 'Store Manager Two',
            'receive_notifications': True
        },
        {
            'username': 'supervisor',
            'password': 'admin123',
            'email': 'supervisor@plottwist.com',
            'full_name': 'Store Supervisor',
            'receive_notifications': False
        }
    ]
    
    created_count = 0
    for user_data in admin_users:
        try:
            hashed_password = generate_password_hash(user_data['password'])
            user = User(
                username=user_data['username'],
                password_hash=hashed_password,
                password=hashed_password,  # For legacy compatibility
                is_manager=True,
                email=user_data['email'],
                full_name=user_data['full_name'],
                receive_notifications=user_data['receive_notifications']
            )
            db.session.add(user)
            created_count += 1
        except Exception as e:
            print(f"Error creating user {user_data['username']}: {e}")
    
    try:
        db.session.commit()
        print(f"Successfully created {created_count} admin users!")
        print("\nLogin credentials:")
        print("=" * 40)
        for user_data in admin_users:
            print(f"Username: {user_data['username']} | Password: {user_data['password']}")
        print("=" * 40)
    except Exception as e:
        db.session.rollback()
        print(f"Error saving users to database: {e}")

def setup_sample_purchases():
    """Create sample purchases to populate the orders dashboard."""
    print("Setting up sample purchases...")
    
    if Purchase.query.count() > 0:
        print("Purchases already exist. Skipping purchase creation.")
        return
    
    # Get some books for the purchases
    books = Book.query.limit(10).all()
    if not books:
        print("No books available for creating sample purchases.")
        return
    
    customer_names = [
        "John Smith", "Emily Johnson", "Michael Brown", "Sarah Davis",
        "Robert Wilson", "Jessica Garcia", "David Martinez", "Lisa Anderson",
        "James Taylor", "Maria Rodriguez", "Christopher Lee", "Ashley Moore"
    ]
    
    statuses = ['Pending', 'Processing', 'Shipped', 'Completed']
    
    created_count = 0
    for i in range(15):  # Create 15 sample purchases
        try:
            book = random.choice(books)
            customer = random.choice(customer_names)
            
            purchase = Purchase(
                customer_name=customer,
                customer_email=f"{customer.lower().replace(' ', '.')}@email.com",
                customer_phone=f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                customer_address=f"{random.randint(100, 9999)} {random.choice(['Main St', 'Oak Ave', 'Elm St', 'Pine Rd'])}, City, State {random.randint(10000, 99999)}",
                book_isbn=book.isbn,
                quantity=random.randint(1, 3),
                status=random.choice(statuses),
                timestamp=datetime.now() - timedelta(days=random.randint(0, 30))
            )
            db.session.add(purchase)
            created_count += 1
        except Exception as e:
            print(f"Error creating sample purchase {i}: {e}")
    
    try:
        db.session.commit()
        print(f"Successfully created {created_count} sample purchases!")
    except Exception as e:
        db.session.rollback()
        print(f"Error saving purchases to database: {e}")

def main():
    """Main setup function."""
    print("=" * 60)
    print("CHAPTER 6: A PLOT TWIST - DATABASE SETUP")
    print("=" * 60)
    print("Setting up sample data for your bookstore...")
    print()
    
    with app.app_context():
        # Ensure all tables exist
        db.create_all()
        
        # Setup sample data
        setup_sample_books()
        print()
        setup_admin_users()
        print()
        setup_sample_purchases()
        
        print()
        print("=" * 60)
        print("SETUP COMPLETE!")
        print("=" * 60)
        print("Your bookstore is now ready with:")
        print(f"• {Book.query.count()} books in inventory")
        print(f"• {User.query.filter_by(is_manager=True).count()} admin users")
        print(f"• {Purchase.query.count()} sample orders")
        print()
        print("You can now:")
        print("• Visit http://127.0.0.1:5000 to access your bookstore")
        print("• Log in with any of the admin accounts shown above")
        print("• Browse and manage your inventory")
        print("• View and process customer orders")
        print("=" * 60)

if __name__ == "__main__":
    main()