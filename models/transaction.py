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
