#!/usr/bin/env python3
"""
Database initialization script for Personal Finance Tracker.
This script ensures the database is properly initialized with clean state.
"""

import os
import sys
from utils.db import reset_database, init_db

def main():
    """Initialize database with clean state"""
    try:
        print("=" * 50)
        print("Personal Finance Tracker - Database Initialization")
        print("=" * 50)
        
        # Reset database to clean state
        print("Step 1: Resetting database...")
        reset_database()
        print("✅ Database reset completed")
        
        # Initialize with fresh schema
        print("Step 2: Creating database schema...")
        init_db()
        print("✅ Database initialization completed")
        
        print("=" * 50)
        print("Database is ready for use!")
        print("You can now start the application with: python app.py")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error during database initialization: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
