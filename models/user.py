import bcrypt
from utils.db import get_db_connection

class User:
    @staticmethod
    def create_user(username, email, password):
        if not username or not username.strip():
            raise ValueError("Username cannot be empty")
        if not email or not email.strip():
            raise ValueError("Email cannot be empty")
        if not password:
            raise ValueError("Password cannot be empty")
            
        username = username.strip()
        email = email.strip().lower()
        
        if len(username) < 3:
            raise ValueError("Username must be at least 3 characters long")
        if len(username) > 50:
            raise ValueError("Username cannot be longer than 50 characters")
        
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Check if username already exists (case insensitive)
            existing_user = cursor.execute('SELECT id FROM users WHERE LOWER(username) = LOWER(?)', (username,)).fetchone()
            if existing_user:
                raise ValueError("Username already exists")
                
            # Check if email already exists (case insensitive)
            existing_email = cursor.execute('SELECT id FROM users WHERE LOWER(email) = LOWER(?)', (email,)).fetchone()
            if existing_email:
                raise ValueError("Email already exists")
            
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute(
                """
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
                """,
                (username, email, hashed_password)
            )
            conn.commit()
            user_id = cursor.lastrowid
            return user_id
        finally:
            conn.close()

    @staticmethod
    def verify_user(username, password):
        if not username or not password:
            return None
            
        conn = get_db_connection()
        try:
            # Try case-insensitive lookup
            user = conn.execute('SELECT * FROM users WHERE LOWER(username) = LOWER(?)', (username.strip(),)).fetchone()
            if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
                return dict(user)
            return None
        except Exception as e:
            print(f"Error verifying user: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_user_by_id(user_id):
        conn = get_db_connection()
        try:
            user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
            return dict(user) if user else None
        finally:
            conn.close()

    @staticmethod
    def update_password(user_id, new_password):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (hashed_password, user_id))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def update_username(user_id, new_username):
        if not new_username or not new_username.strip():
            raise ValueError("Username cannot be empty")
            
        new_username = new_username.strip()
        
        if len(new_username) < 3:
            raise ValueError("Username must be at least 3 characters long")
        if len(new_username) > 50:
            raise ValueError("Username cannot be longer than 50 characters")
            
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            existing_user = conn.execute('SELECT id FROM users WHERE LOWER(username) = LOWER(?) AND id != ?', (new_username, user_id)).fetchone()
            if existing_user:
                raise ValueError("Username already exists")
            cursor.execute('UPDATE users SET username = ? WHERE id = ?', (new_username, user_id))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def username_exists(username, exclude_user_id=None):
        if not username:
            return False
            
        conn = get_db_connection()
        try:
            if exclude_user_id:
                user = conn.execute('SELECT id FROM users WHERE LOWER(username) = LOWER(?) AND id != ?', (username.strip(), exclude_user_id)).fetchone()
            else:
                user = conn.execute('SELECT id FROM users WHERE LOWER(username) = LOWER(?)', (username.strip(),)).fetchone()
            return user is not None
        finally:
            conn.close()

    @staticmethod
    def email_exists(email, exclude_user_id=None):
        if not email:
            return False
            
        email = email.strip().lower()
        conn = get_db_connection()
        try:
            if exclude_user_id:
                user = conn.execute('SELECT id FROM users WHERE LOWER(email) = LOWER(?) AND id != ?', (email, exclude_user_id)).fetchone()
            else:
                user = conn.execute('SELECT id FROM users WHERE LOWER(email) = LOWER(?)', (email,)).fetchone()
            return user is not None
        finally:
            conn.close()
