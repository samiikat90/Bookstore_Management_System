#!/usr/bin/env python3
"""
Script to add genres to all books currently in inventory
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app import app, db, Book

# Genre mapping based on book titles and typical literary classifications
BOOK_GENRES = {
    # Fiction
    "To Kill a Mockingbird": "Fiction",
    "1984": "Science Fiction",
    "Pride and Prejudice": "Romance",
    "The Great Gatsby": "Fiction",
    "Lord of the Flies": "Fiction",
    "Jane Eyre": "Romance",
    "The Catcher in the Rye": "Fiction",
    "Wuthering Heights": "Romance",
    "Of Mice and Men": "Fiction",
    "Animal Farm": "Fiction",
    "Brave New World": "Science Fiction",
    "The Hobbit": "Fantasy",
    "Fahrenheit 451": "Science Fiction",
    "The Lord of the Rings": "Fantasy",
    "Harry Potter": "Fantasy",
    "Gone with the Wind": "Romance",
    "The Chronicles of Narnia": "Fantasy",
    "Little Women": "Fiction",
    "The Picture of Dorian Gray": "Fiction",
    "Dracula": "Horror",
    "Frankenstein": "Horror",
    "The Strange Case of Dr. Jekyll and Mr. Hyde": "Horror",
    "The Count of Monte Cristo": "Adventure",
    "Les Miserables": "Fiction",
    "War and Peace": "Fiction",
    "Crime and Punishment": "Fiction",
    "The Brothers Karamazov": "Fiction",
    "Anna Karenina": "Romance",
    
    # Mystery/Thriller
    "The Girl with the Dragon Tattoo": "Mystery",
    "Gone Girl": "Thriller",
    "The Da Vinci Code": "Thriller",
    "And Then There Were None": "Mystery",
    "The Murder of Roger Ackroyd": "Mystery",
    "The Big Sleep": "Mystery",
    "The Maltese Falcon": "Mystery",
    "Rebecca": "Mystery",
    "The Silence of the Lambs": "Thriller",
    "The Shining": "Horror",
    
    # Non-Fiction
    "Sapiens": "History",
    "Educated": "Biography",
    "Becoming": "Biography",
    "The Immortal Life of Henrietta Lacks": "Science",
    "Steve Jobs": "Biography",
    "Einstein": "Biography",
    "A Brief History of Time": "Science",
    "The Diary of a Young Girl": "Biography",
    "Long Walk to Freedom": "Biography",
    "The Art of War": "Philosophy",
    
    # Self-Help/Business
    "Think and Grow Rich": "Self-Help",
    "How to Win Friends and Influence People": "Self-Help",
    "The 7 Habits of Highly Effective People": "Self-Help",
    "Rich Dad Poor Dad": "Business",
    "The Lean Startup": "Business",
    "Good to Great": "Business",
    "The Power of Now": "Self-Help",
    "Atomic Habits": "Self-Help",
    
    # Young Adult
    "The Hunger Games": "Young Adult",
    "Twilight": "Young Adult",
    "The Fault in Our Stars": "Young Adult",
    "Divergent": "Young Adult",
    "The Maze Runner": "Young Adult",
    "Percy Jackson": "Young Adult",
    
    # Poetry/Drama
    "The Complete Works of Shakespeare": "Drama",
    "Romeo and Juliet": "Drama",
    "Hamlet": "Drama",
    "Macbeth": "Drama",
    "A Midsummer Night's Dream": "Drama",
    "The Poetry of Robert Frost": "Poetry",
    "Leaves of Grass": "Poetry",
    
    # Children's Books
    "Charlotte's Web": "Children's Books",
    "Where the Wild Things Are": "Children's Books",
    "The Cat in the Hat": "Children's Books",
    "Goodnight Moon": "Children's Books",
    "The Very Hungry Caterpillar": "Children's Books",
}

def assign_genre_by_title(title):
    """
    Assign genre based on book title using fuzzy matching
    """
    title_lower = title.lower()
    
    # Direct matches first
    for book_title, genre in BOOK_GENRES.items():
        if book_title.lower() in title_lower or title_lower in book_title.lower():
            return genre
    
    # Keyword-based matching
    if any(keyword in title_lower for keyword in ['harry potter', 'potter']):
        return "Fantasy"
    elif any(keyword in title_lower for keyword in ['lord of the rings', 'lotr', 'hobbit']):
        return "Fantasy"
    elif any(keyword in title_lower for keyword in ['sherlock', 'holmes', 'christie', 'agatha']):
        return "Mystery"
    elif any(keyword in title_lower for keyword in ['hunger games', 'twilight', 'divergent']):
        return "Young Adult"
    elif any(keyword in title_lower for keyword in ['shakespeare', 'hamlet', 'romeo']):
        return "Drama"
    elif any(keyword in title_lower for keyword in ['steve jobs', 'einstein', 'biography']):
        return "Biography"
    elif any(keyword in title_lower for keyword in ['business', 'startup', 'rich dad']):
        return "Business"
    elif any(keyword in title_lower for keyword in ['self-help', 'habits', 'influence']):
        return "Self-Help"
    elif any(keyword in title_lower for keyword in ['history', 'war', 'sapiens']):
        return "History"
    elif any(keyword in title_lower for keyword in ['science', 'physics', 'time']):
        return "Science"
    elif any(keyword in title_lower for keyword in ['horror', 'scary', 'dracula', 'frankenstein']):
        return "Horror"
    elif any(keyword in title_lower for keyword in ['romance', 'love', 'pride and prejudice']):
        return "Romance"
    elif any(keyword in title_lower for keyword in ['children', 'kids', 'cat in the hat']):
        return "Children's Books"
    elif any(keyword in title_lower for keyword in ['poetry', 'poems', 'frost']):
        return "Poetry"
    elif any(keyword in title_lower for keyword in ['fantasy', 'magic', 'dragon', 'wizard']):
        return "Fantasy"
    elif any(keyword in title_lower for keyword in ['thriller', 'suspense', 'gone girl']):
        return "Thriller"
    elif any(keyword in title_lower for keyword in ['mystery', 'detective', 'murder']):
        return "Mystery"
    elif any(keyword in title_lower for keyword in ['science fiction', 'sci-fi', '1984', 'brave new world']):
        return "Science Fiction"
    else:
        return "Fiction"  # Default genre

def update_book_genres():
    """
    Update all books in the database with appropriate genres
    """
    with app.app_context():
        try:
            # Get all books
            books = Book.query.all()
            print(f"Found {len(books)} books in the database")
            
            updated_count = 0
            for book in books:
                if not book.genre or book.genre.strip() == "":
                    # Assign genre based on title
                    new_genre = assign_genre_by_title(book.title)
                    book.genre = new_genre
                    updated_count += 1
                    print(f"Updated '{book.title}' -> Genre: {new_genre}")
                else:
                    print(f"'{book.title}' already has genre: {book.genre}")
            
            # Commit changes
            db.session.commit()
            print(f"\nSuccessfully updated {updated_count} books with genres!")
            
            # Display genre summary
            genre_counts = {}
            for book in Book.query.all():
                genre = book.genre or "No Genre"
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
            
            print("\nGenre Distribution:")
            for genre, count in sorted(genre_counts.items()):
                print(f"  {genre}: {count} books")
                
        except Exception as e:
            db.session.rollback()
            print(f"Error updating book genres: {e}")

if __name__ == "__main__":
    update_book_genres()