import re
from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from models.user import User

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        if not all([username, email, password]):
            return jsonify({'error': 'All fields required'}), 400
        is_strong, message = validate_password_strength(password)
        if not is_strong:
            return jsonify({'error': message}), 400
        try:
            user_id = User.create_user(username, email, password)
            session['user_id'] = user_id
            session['username'] = username
            return jsonify({'message': 'User created successfully', 'user_id': user_id}), 201
        except Exception:
            return jsonify({'error': 'Username or email already exists'}), 400

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() if request.is_json else request.form
    username = data.get('username')
    password = data.get('password')
    user = User.verify_user(username, password)
    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
        return jsonify({'message': 'Login successful', 'user': {'id': user['id'], 'username': user['username']}}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

@bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

@bp.route('/me', methods=['GET'])
def get_current_user():
    if 'user_id' in session:
        user = User.get_user_by_id(session['user_id'])
        return jsonify({'user': {'id': user['id'], 'username': user['username']}}), 200
    return jsonify({'error': 'Not logged in'}), 401

def validate_password_strength(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
        return False, "Password must contain at least one special character"
    return True, "Password is strong"

@bp.route('/settings', methods=['GET'])
def account_settings():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('account_settings.html')

@bp.route('/change-password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    data = request.get_json() if request.is_json else request.form
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')
    if not all([current_password, new_password, confirm_password]):
        return jsonify({'error': 'All fields are required'}), 400
    if new_password != confirm_password:
        return jsonify({'error': 'New passwords do not match'}), 400
    is_strong, message = validate_password_strength(new_password)
    if not is_strong:
        return jsonify({'error': message}), 400
    user = User.get_user_by_id(session['user_id'])
    if not User.verify_user(user['username'], current_password):
        return jsonify({'error': 'Current password is incorrect'}), 400
    try:
        User.update_password(session['user_id'], new_password)
        return jsonify({'message': 'Password updated successfully'}), 200
    except Exception:
        return jsonify({'error': 'Failed to update password'}), 500

@bp.route('/change-username', methods=['POST'])
def change_username():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    data = request.get_json() if request.is_json else request.form
    new_username = data.get('new_username')
    current_password = data.get('current_password')
    if not all([new_username, current_password]):
        return jsonify({'error': 'Username and current password are required'}), 400
    if len(new_username.strip()) < 3:
        return jsonify({'error': 'Username must be at least 3 characters long'}), 400
    if len(new_username.strip()) > 50:
        return jsonify({'error': 'Username cannot be longer than 50 characters'}), 400
    if not re.match(r'^[a-zA-Z0-9_]+$', new_username.strip()):
        return jsonify({'error': 'Username can only contain letters, numbers, and underscores'}), 400
    user = User.get_user_by_id(session['user_id'])
    if not User.verify_user(user['username'], current_password):
        return jsonify({'error': 'Current password is incorrect'}), 400
    try:
        User.update_username(session['user_id'], new_username.strip())
        session['username'] = new_username.strip()
        return jsonify({'message': 'Username updated successfully', 'new_username': new_username.strip()}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception:
        return jsonify({'error': 'Failed to update username'}), 500
