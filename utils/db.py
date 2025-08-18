import sqlite3
import os

DATABASE = os.environ.get('DATABASE_URL', 'sqlite:///finance.db').replace('sqlite:///', '')

def reset_database():
    """Reset the database by removing the existing file"""
    try:
        if os.path.exists(DATABASE):
            os.remove(DATABASE)
            print(f"Removed existing database: {DATABASE}")
        
        # Ensure directory exists for database file
        db_dir = os.path.dirname(os.path.abspath(DATABASE))
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            print(f"Created database directory: {db_dir}")
    except Exception as e:
        print(f"Error resetting database: {e}")

def init_db():
    """Initialize the database with required tables"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Drop existing tables if they exist (for clean slate)
        cursor.execute('DROP TABLE IF EXISTS transactions')
        cursor.execute('DROP TABLE IF EXISTS users')
        
        # Create users table with improved constraints
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL COLLATE NOCASE,
                email TEXT UNIQUE NOT NULL COLLATE NOCASE,
                password_hash BLOB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT check_username_length CHECK (length(trim(username)) >= 3),
                CONSTRAINT check_email_format CHECK (email LIKE '%@%.%')
            )
        ''')
        
        # Create transactions table
        cursor.execute('''
            CREATE TABLE transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL CHECK (amount > 0),
                category TEXT NOT NULL,
                type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
                date TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX idx_transactions_user_id ON transactions(user_id)')
        cursor.execute('CREATE INDEX idx_transactions_date ON transactions(date)')
        cursor.execute('CREATE INDEX idx_transactions_type ON transactions(type)')
        cursor.execute('CREATE INDEX idx_users_username ON users(username)')
        cursor.execute('CREATE INDEX idx_users_email ON users(email)')
        
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
        conn = sqlite3.connect(DATABASE, timeout=30.0)
        conn.row_factory = sqlite3.Row
        # Enable foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON")
        # Enable WAL mode for better concurrency
        conn.execute("PRAGMA journal_mode = WAL")
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        raise
