import bcrypt
from utils.db import get_db_connection

class User:
    @staticmethod
    def create_user(username, email, password):
        conn = get_db_connection()
        cursor = conn.cursor()
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
        conn.close()
        return user_id

    @staticmethod
    def verify_user(username, password):
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
            return dict(user)
        return None

    @staticmethod
    def get_user_by_id(user_id):
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        return dict(user) if user else None

    @staticmethod
    def update_password(user_id, new_password):
        conn = get_db_connection()
        cursor = conn.cursor()
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (hashed_password, user_id))
        conn.commit()
        conn.close()

    @staticmethod
    def update_username(user_id, new_username):
        conn = get_db_connection()
        cursor = conn.cursor()
        existing_user = conn.execute('SELECT id FROM users WHERE username = ? AND id != ?', (new_username, user_id)).fetchone()
        if existing_user:
            conn.close()
            raise ValueError("Username already exists")
        cursor.execute('UPDATE users SET username = ? WHERE id = ?', (new_username, user_id))
        conn.commit()
        conn.close()

    @staticmethod
    def username_exists(username, exclude_user_id=None):
        conn = get_db_connection()
        if exclude_user_id:
            user = conn.execute('SELECT id FROM users WHERE username = ? AND id != ?', (username, exclude_user_id)).fetchone()
        else:
            user = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        return user is not None
