#!/usr/bin/env python3
"""
Database reset script for production deployment
This removes the existing database and creates a fresh one
"""

import os
import sqlite3
from utils.db import init_db

def reset_database():
    """Remove existing database and create fresh tables"""
    db_path = os.environ.get('DATABASE_URL', 'sqlite:///finance.db').replace('sqlite:///', '')
    
    # Remove existing database file if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing database: {db_path}")
    
    # Initialize fresh database
    init_db()
    print(f"Created fresh database: {db_path}")

if __name__ == '__main__':
    reset_database()
