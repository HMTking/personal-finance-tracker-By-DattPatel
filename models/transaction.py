from utils.db import get_db_connection

class Transaction:
    @staticmethod
    def create(user_id, amount, category, type_, date, description=""):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO transactions (user_id, amount, category, type, date, description)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, amount, category, type_, date, description)
        )
        conn.commit()
        transaction_id = cursor.lastrowid
        conn.close()
        return transaction_id

    @staticmethod
    def delete(user_id, transaction_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id = ? AND user_id = ?", (transaction_id, user_id))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted
    
    @staticmethod
    def update(user_id, transaction_id, amount, category, type_, date, description=""):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE transactions 
            SET amount = ?, category = ?, type = ?, date = ?, description = ?
            WHERE id = ? AND user_id = ?
            """,
            (amount, category, type_, date, description, transaction_id, user_id)
        )
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return updated
    
    @staticmethod
    def get_by_id(user_id, transaction_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        transaction = cursor.execute(
            "SELECT * FROM transactions WHERE id = ? AND user_id = ?", 
            (transaction_id, user_id)
        ).fetchone()
        conn.close()
        return dict(transaction) if transaction else None

    @staticmethod
    def get_all(user_id):
        conn = get_db_connection()
        transactions = conn.execute("SELECT * FROM transactions WHERE user_id = ? ORDER BY date DESC", (user_id,)).fetchall()
        conn.close()
        return [dict(row) for row in transactions]

    @staticmethod
    def summary(user_id):
        conn = get_db_connection()
        total_income = conn.execute('SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE user_id = ? AND type = "income"', (user_id,)).fetchone()['total']
        total_expenses = conn.execute('SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE user_id = ? AND type = "expense"', (user_id,)).fetchone()['total']
        expense_categories = conn.execute('''
            SELECT category, SUM(amount) as total 
            FROM transactions 
            WHERE user_id = ? AND type = "expense" 
            GROUP BY category
            ORDER BY total DESC
        ''', (user_id,)).fetchall()
        income_categories = conn.execute('''
            SELECT category, SUM(amount) as total 
            FROM transactions 
            WHERE user_id = ? AND type = "income" 
            GROUP BY category
            ORDER BY total DESC
        ''', (user_id,)).fetchall()
        conn.close()
        return {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'current_balance': total_income - total_expenses,
            'expenses_by_category': [dict(row) for row in expense_categories],
            'income_by_category': [dict(row) for row in income_categories]
        }

    @staticmethod
    def current_month_summary(user_id):
        conn = get_db_connection()
        # Get current month's start and end dates
        from datetime import datetime, date
        now = datetime.now()
        start_of_month = date(now.year, now.month, 1)
        if now.month == 12:
            end_of_month = date(now.year + 1, 1, 1)
        else:
            end_of_month = date(now.year, now.month + 1, 1)
        
        total_income = conn.execute(
            'SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE user_id = ? AND type = "income" AND date >= ? AND date < ?', 
            (user_id, start_of_month, end_of_month)
        ).fetchone()['total']
        
        total_expenses = conn.execute(
            'SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE user_id = ? AND type = "expense" AND date >= ? AND date < ?', 
            (user_id, start_of_month, end_of_month)
        ).fetchone()['total']
        
        conn.close()
        return {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'current_balance': total_income - total_expenses
        }
