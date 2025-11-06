#!/usr/bin/env python3
"""
Script to display all books with their assigned genres
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.app import app, db, Book

def display_books_with_genres():
    """
    Display all books with their genres in a formatted table
    """
    with app.app_context():
        try:
            books = Book.query.order_by(Book.genre, Book.title).all()
            
            print("=" * 80)
            print("BOOKSTORE INVENTORY WITH GENRES")
            print("=" * 80)
            print(f"{'Title':<40} {'Author':<25} {'Genre':<15}")
            print("-" * 80)
            
            current_genre = None
            for book in books:
                if book.genre != current_genre:
                    if current_genre is not None:
                        print()
                    current_genre = book.genre
                    print(f"\n--- {book.genre.upper()} ---")
                
                title = book.title[:37] + "..." if len(book.title) > 40 else book.title
                author = book.author[:22] + "..." if len(book.author) > 25 else book.author
                print(f"{title:<40} {author:<25} {book.genre:<15}")
            
            print("\n" + "=" * 80)
            
            # Genre summary
            genre_counts = {}
            for book in books:
                genre = book.genre or "No Genre"
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
            
            print("\nGENRE SUMMARY:")
            for genre, count in sorted(genre_counts.items()):
                print(f"  {genre}: {count} books")
            print(f"\nTotal Books: {len(books)}")
            
        except Exception as e:
            print(f"Error displaying books: {e}")

if __name__ == "__main__":
    display_books_with_genres()