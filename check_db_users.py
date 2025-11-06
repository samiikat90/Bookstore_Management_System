#!/usr/bin/env python3
"""
Script to check database tables and admin users.
"""

import sqlite3
import os

def check_database():
    # Check if database exists
    db_path = 'instance/bookstore.db'
    if not os.path.exists(db_path):
        print(f'Database not found at: {db_path}')
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    tables = cursor.fetchall()
    
    print('Available tables:')
    for table in tables:
        print(f'  {table[0]}')
    
    print(f'\nTotal tables found: {len(tables)}')
    
    if len(tables) == 0:
        print('No tables found in database!')
        conn.close()
        return
    
    # Check if users table exists (might be 'users' instead of 'user')
    table_names = [table[0] for table in tables]
    
    if 'user' in table_names:
        user_table = 'user'
    elif 'users' in table_names:
        user_table = 'users'
    else:
        print('\nNo user table found!')
        conn.close()
        return
    
    # Get admin users
    try:
        cursor.execute(f'SELECT username, email, full_name, is_manager FROM {user_table} WHERE is_manager = 1')
        users = cursor.fetchall()
        
        print(f'\nAdmin Users from {user_table} table:')
        print('=' * 40)
        for user in users:
            username, email, full_name, is_manager = user
            print(f'Username: {username}')
            print(f'  Email: {email}')
            print(f'  Full Name: {full_name}')
            print(f'  Manager: {bool(is_manager)}')
            print('-' * 25)
    except Exception as e:
        print(f'Error querying admin users: {e}')
        
        # Try to get column info
        cursor.execute(f'PRAGMA table_info({user_table})')
        columns = cursor.fetchall()
        print(f'\nColumns in {user_table} table:')
        for col in columns:
            print(f'  {col[1]} ({col[2]})')
    
    conn.close()

if __name__ == "__main__":
    check_database()