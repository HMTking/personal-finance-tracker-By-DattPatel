import sqlite3
import os

def migrate_database():
    DATABASE = 'finance.db'
    if not os.path.exists(DATABASE):
        print("Database doesn't exist yet. It will be created when the app runs.")
        return
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA table_info(transactions)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'user_id' not in columns:
            print("Adding user_id column to transactions table...")
            cursor.execute("SELECT * FROM transactions")
            existing_transactions = cursor.fetchall()
            print(f"Found {len(existing_transactions)} existing transactions")
            cursor.execute('''
                CREATE TABLE transactions_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL DEFAULT 1,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
                    date TEXT NOT NULL,
                    description TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            if existing_transactions:
                cursor.execute('''
                    INSERT INTO transactions_new (id, user_id, amount, category, type, date, description)
                    SELECT id, 1, amount, category, type, date, description FROM transactions
                ''')
                print(f"Migrated {len(existing_transactions)} transactions to new schema")
            cursor.execute("DROP TABLE transactions")
            cursor.execute("ALTER TABLE transactions_new RENAME TO transactions")
            print("Migration completed successfully!")
        else:
            print("Database is already up to date.")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash BLOB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        print("Database schema check completed.")
    except Exception as e:
        print(f"Migration error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
