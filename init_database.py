#!/usr/bin/env python3
"""
Initialize database tables for the bookstore management system
"""

import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app import app, db

def init_database():
    """Initialize all database tables."""
    print("Initializing database tables...")
    
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("SUCCESS: Database tables created successfully!")
            
            # Verify tables were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"Created tables: {tables}")
            
        except Exception as e:
            print(f"Error creating database tables: {e}")
            return False
    
    return True

if __name__ == "__main__":
    success = init_database()
    if success:
        print("Database initialization complete!")
    else:
        print("Database initialization failed!")
        sys.exit(1)