

from flask import Flask, render_template, session, redirect, url_for
from utils.db import init_db
from routes.transactions import bp as transactions_bp
from routes.summary import bp as summary_bp
from routes.auth import bp as auth_bp

app = Flask(__name__)
app.secret_key = 'finance-tracker-secret-key-change-this-in-production-2025'

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
    init_db()
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
