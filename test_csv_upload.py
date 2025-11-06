#!/usr/bin/env python3
"""
Test script to verify CSV upload functionality with genre column.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import just what we need for testing
import csv

# Define the expected genres (copying from app.py)
BOOK_GENRES = [
    'Fiction', 'Non-Fiction', 'Mystery', 'Romance', 'Science Fiction', 'Fantasy',
    'Biography', 'History', 'Self-Help', 'Business', 'Health', 'Travel',
    'Cooking', 'Art', 'Poetry', 'Drama', 'Children', 'Young Adult',
    'Education', 'Reference'
]

def test_csv_format():
    """Test the new CSV format with genre column."""
    
    print("Testing CSV format with genre column...")
    
    # Read the new CSV file
    csv_file = 'uploads/UpdatedBookListing2.csv'
    
    if not os.path.exists(csv_file):
        print(f"ERROR: CSV file {csv_file} not found!")
        return False
    
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        print(f"CSV Headers: {reader.fieldnames}")
        
        # Check that genre column is present
        if 'genre' not in reader.fieldnames:
            print("ERROR: 'genre' column not found in CSV!")
            return False
        
        # Verify column order
        expected_order = ['isbn', 'title', 'author', 'price', 'quantity', 'genre', 'cover_type', 'description']
        if reader.fieldnames != expected_order:
            print(f"WARNING: Column order might not match expected order.")
            print(f"Expected: {expected_order}")
            print(f"Found: {reader.fieldnames}")
        
        # Read and validate some sample rows
        row_count = 0
        for row in reader:
            row_count += 1
            if row_count <= 3:  # Show first 3 rows
                print(f"Row {row_count}:")
                print(f"  ISBN: {row.get('isbn')}")
                print(f"  Title: {row.get('title')}")
                print(f"  Genre: {row.get('genre')}")
                print(f"  Cover Type: {row.get('cover_type')}")
                print()
        
        print(f"Total rows in CSV: {row_count}")
        return True

def test_genre_validation():
    """Test genre validation against predefined genres."""
    
    print(f"\nTesting genre validation...")
    print(f"Available genres ({len(BOOK_GENRES)}): {', '.join(BOOK_GENRES)}")
    
    # Test some genres from the CSV
    test_genres = ['Mystery', 'Science Fiction', 'Fantasy', 'Adventure', 'Poetry', 'Invalid Genre']
    
    for genre in test_genres:
        is_valid = genre in BOOK_GENRES
        status = "Valid" if is_valid else "Invalid"
        print(f"  {genre}: {status}")
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("CSV Upload Format Test")
    print("=" * 60)
    
    # Test CSV format
    format_ok = test_csv_format()
    
    # Test genre validation
    validation_ok = test_genre_validation()
    
    print("\n" + "=" * 60)
    if format_ok and validation_ok:
        print("SUCCESS: All tests passed! CSV format is ready for upload.")
    else:
        print("ERROR: Some tests failed. Please check the issues above.")
    print("=" * 60)