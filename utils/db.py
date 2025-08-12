import sqlite3
import os

DATABASE = os.environ.get('DATABASE_URL', 'sqlite:///finance.db').replace('sqlite:///', '')

def init_db():
    """Initialize the database with required tables"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash BLOB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
                date TEXT NOT NULL,
                description TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        print(f"Database tables created successfully at: {DATABASE}")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise
    finally:
        if conn:
            conn.close()

def get_db_connection():
    """Get a database connection with proper configuration"""
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        raise
