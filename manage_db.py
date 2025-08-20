#!/usr/bin/env python3
"""
Database Management Script for Personal Finance Tracker
Usage:
    python manage_db.py --reset     # Reset database (DELETE ALL DATA)
    python manage_db.py --init      # Initialize database if not exists
    python manage_db.py --migrate   # Run database migrations
    python manage_db.py --status    # Check database status
"""

import os
import sys
import argparse
from utils.db import init_db, reset_database, get_db_connection, DATABASE

def check_database_status():
    """Check if database exists and show basic info"""
    if not os.path.exists(DATABASE):
        print(f"❌ Database does not exist: {DATABASE}")
        return False
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"✅ Database exists: {DATABASE}")
        print(f"📊 Tables: {', '.join(tables)}")
        
        # Count users and transactions
        if 'users' in tables:
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            print(f"👥 Users: {user_count}")
        
        if 'transactions' in tables:
            cursor.execute("SELECT COUNT(*) FROM transactions")
            transaction_count = cursor.fetchone()[0]
            print(f"💰 Transactions: {transaction_count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False

def reset_db():
    """Reset database (DELETE ALL DATA)"""
    print("⚠️  WARNING: This will DELETE ALL DATA in the database!")
    confirm = input("Are you sure you want to continue? Type 'DELETE' to confirm: ")
    
    if confirm != 'DELETE':
        print("❌ Operation cancelled.")
        return
    
    try:
        reset_database()
        init_db()
        print("✅ Database reset successfully!")
    except Exception as e:
        print(f"❌ Error resetting database: {e}")

def initialize_db():
    """Initialize database if it doesn't exist"""
    if os.path.exists(DATABASE):
        print(f"ℹ️  Database already exists: {DATABASE}")
        return
    
    try:
        init_db()
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")

def migrate_db():
    """Run database migrations"""
    try:
        from migrate_db import migrate_database
        migrate_database()
        print("✅ Database migrations completed!")
    except Exception as e:
        print(f"❌ Error running migrations: {e}")

def main():
    parser = argparse.ArgumentParser(description='Database Management Script')
    parser.add_argument('--reset', action='store_true', help='Reset database (DELETE ALL DATA)')
    parser.add_argument('--init', action='store_true', help='Initialize database if not exists')
    parser.add_argument('--migrate', action='store_true', help='Run database migrations')
    parser.add_argument('--status', action='store_true', help='Check database status')
    
    args = parser.parse_args()
    
    if args.reset:
        reset_db()
    elif args.init:
        initialize_db()
    elif args.migrate:
        migrate_db()
    elif args.status:
        check_database_status()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
