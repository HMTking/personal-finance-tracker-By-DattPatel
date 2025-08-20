

import os
from flask import Flask, render_template, session, redirect, url_for, send_file
from utils.db import init_db, get_db_connection, reset_database
from routes.transactions import bp as transactions_bp
from routes.summary import bp as summary_bp
from routes.auth import bp as auth_bp

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'finance-tracker-secret-key-change-this-in-production-2025')

# Initialize database when app starts (works with both direct run and gunicorn)
with app.app_context():
    # Only reset database if explicitly requested via environment variable
    if os.environ.get('RESET_DB', 'false').lower() == 'true':
        print("RESET_DB environment variable set - Resetting database...")
        reset_database()
        init_db()
        print("Database reset and initialized with clean state")
    else:
        # Check if database exists, if not create it
        from utils.db import DATABASE
        if not os.path.exists(DATABASE):
            print("Database doesn't exist - Creating new database...")
            init_db()
            print("Database initialized successfully")
        else:
            print("Database exists - Skipping initialization")
            # Run any pending migrations
            try:
                from migrate_db import migrate_database
                migrate_database()
            except Exception as e:
                print(f"Migration check completed: {e}")

app.register_blueprint(transactions_bp)
app.register_blueprint(summary_bp)
app.register_blueprint(auth_bp)

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/settings')
def settings_page():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('account_settings.html')


# Route to download transactions as XLS (legacy - kept for compatibility)
@app.route('/download_xls')
def download_xls():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    import io
    import xlsxwriter
    from models.transaction import Transaction
    
    # Get transactions for current user only
    transactions = Transaction.get_all(session['user_id'])

    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet('Transactions')

    headers = ['Date', 'Type', 'Category', 'Amount', 'Description']
    for col_num, header in enumerate(headers):
        worksheet.write(0, col_num, header)

    for row_num, t in enumerate(transactions, start=1):
        worksheet.write(row_num, 0, t['date'])
        worksheet.write(row_num, 1, t['type'])
        worksheet.write(row_num, 2, t['category'])
        worksheet.write(row_num, 3, t['amount'])
        worksheet.write(row_num, 4, t['description'] if t['description'] else '')

    workbook.close()
    output.seek(0)
    return send_file(output, download_name='transactions.xlsx', as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV', 'development') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
