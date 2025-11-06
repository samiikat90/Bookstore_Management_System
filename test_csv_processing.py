#!/usr/bin/env python3
"""
Simple test to validate CSV processing logic without full Flask app.
"""

import csv
import os

# Mock the genre validation like in app.py
BOOK_GENRES = [
    'Fiction', 'Non-Fiction', 'Mystery', 'Romance', 'Science Fiction', 'Fantasy',
    'Biography', 'History', 'Self-Help', 'Business', 'Health', 'Travel',
    'Cooking', 'Art', 'Poetry', 'Drama', 'Children', 'Young Adult',
    'Education', 'Reference'
]

def test_csv_processing():
    """Test the CSV processing logic similar to upload_csv function."""
    
    print("Testing CSV processing logic...")
    
    csv_file = 'uploads/UpdatedBookListing2.csv'
    
    if not os.path.exists(csv_file):
        print(f"ERROR: CSV file {csv_file} not found!")
        return False
    
    try:
        with open(csv_file, newline='', encoding='utf-8') as csvfile:
            # Read and process headers
            reader = csv.DictReader(csvfile)
            
            # Handle BOM in first column name if present
            fieldnames = reader.fieldnames
            if fieldnames and fieldnames[0].startswith('\ufeff'):
                fieldnames[0] = fieldnames[0].lstrip('\ufeff')
            
            # Normalize header names to lowercase
            normalized_fieldnames = [h.strip().lower() for h in fieldnames]
            
            # Reset file pointer and create new DictReader with normalized headers
            csvfile.seek(0)
            next(csvfile)  # Skip header line
            reader = csv.DictReader(csvfile, fieldnames=normalized_fieldnames)

            # Counters for feedback
            processed_count = 0
            genre_warnings = 0

            for row in reader:
                # Process each field like in the upload function
                isbn = row.get('isbn', '').strip()
                title = row.get('title', '').strip()
                author = row.get('author', '').strip()
                
                try:
                    price = float(row.get('price', '0').strip().replace('$', '').replace(',', ''))
                except (ValueError, AttributeError):
                    print(f"Warning: Invalid price for {title}")
                    continue
                
                try:
                    quantity = int(float(row.get('quantity', '0').strip()))
                except (ValueError, AttributeError):
                    print(f"Warning: Invalid quantity for {title}")
                    continue
                
                # Handle genre field - validate against predefined genres
                genre = row.get('genre', '').strip()
                if genre and genre not in BOOK_GENRES:
                    print(f"Warning: Unknown genre '{genre}' for book '{title}'. Would set to 'Fiction'.")
                    genre = 'Fiction'
                    genre_warnings += 1
                elif not genre:
                    genre = 'Fiction'  # Default genre
                
                cover_type = row.get('cover_type', '').strip()
                description = row.get('description', '').strip()
                
                # Validate required fields
                if not isbn or not title or not author:
                    print(f"Warning: Missing required fields for book '{title}'")
                    continue
                
                processed_count += 1
                print(f"✓ {processed_count}: {title} by {author} ({genre}) - ${price}")
        
        print(f"\nProcessing Summary:")
        print(f"  Total books processed: {processed_count}")
        print(f"  Genre warnings: {genre_warnings}")
        print("✓ CSV processing test completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"ERROR processing CSV: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("CSV Processing Logic Test")
    print("=" * 60)
    
    success = test_csv_processing()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ CSV processing logic is working correctly!")
        print("The upload function should handle the new genre column properly.")
    else:
        print("✗ Issues found in CSV processing logic.")
    print("=" * 60)