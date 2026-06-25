import os
from flask import Flask, render_template, session, redirect, url_for
from utils.db import init_db, reset_database
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


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV', 'development') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
