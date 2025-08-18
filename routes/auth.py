import re
from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from models.user import User

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            data = request.get_json() if request.is_json else request.form
            username = data.get('username', '').strip() if data.get('username') else ''
            email = data.get('email', '').strip() if data.get('email') else ''
            password = data.get('password', '') if data.get('password') else ''
            
            if not all([username, email, password]):
                return jsonify({'error': 'All fields are required'}), 400
                
            # Validate input lengths
            if len(username) < 3:
                return jsonify({'error': 'Username must be at least 3 characters long'}), 400
            if len(username) > 50:
                return jsonify({'error': 'Username cannot be longer than 50 characters'}), 400
            if len(email) > 100:
                return jsonify({'error': 'Email cannot be longer than 100 characters'}), 400
                
            # Validate username format
            if not re.match(r'^[a-zA-Z0-9_]+$', username):
                return jsonify({'error': 'Username can only contain letters, numbers, and underscores'}), 400
                
            # Validate email format
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                return jsonify({'error': 'Please enter a valid email address'}), 400
            
            # Validate password strength
            is_strong, message = validate_password_strength(password)
            if not is_strong:
                return jsonify({'error': message}), 400
                
            # Create user
            user_id = User.create_user(username, email, password)
            session['user_id'] = user_id
            session['username'] = username
            return jsonify({'message': 'User created successfully', 'user_id': user_id}), 201
            
        except ValueError as e:
            error_message = str(e)
            if 'username already exists' in error_message.lower():
                return jsonify({'error': 'Username already exists. Please choose a different username.'}), 400
            elif 'email already exists' in error_message.lower():
                return jsonify({'error': 'Email already exists. Please use a different email address.'}), 400
            else:
                return jsonify({'error': error_message}), 400
        except Exception as e:
            print(f"Registration error: {e}")
            return jsonify({'error': 'Registration failed. Please try again.'}), 500

@bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json() if request.is_json else request.form
        username = data.get('username', '').strip() if data.get('username') else ''
        password = data.get('password', '') if data.get('password') else ''
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
            
        user = User.verify_user(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return jsonify({
                'message': 'Login successful', 
                'user': {
                    'id': user['id'], 
                    'username': user['username']
                }
            }), 200
        else:
            return jsonify({'error': 'Invalid username or password'}), 401
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': 'Login failed. Please try again.'}), 500

@bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

@bp.route('/me', methods=['GET'])
def get_current_user():
    if 'user_id' in session:
        try:
            user = User.get_user_by_id(session['user_id'])
            if user:
                return jsonify({'user': {'id': user['id'], 'username': user['username']}}), 200
            else:
                session.clear()  # Clear invalid session
                return jsonify({'error': 'User not found'}), 401
        except Exception as e:
            print(f"Get current user error: {e}")
            session.clear()  # Clear session on error
            return jsonify({'error': 'Session invalid'}), 401
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
        
    try:
        data = request.get_json() if request.is_json else request.form
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')
        
        if not all([current_password, new_password, confirm_password]):
            return jsonify({'error': 'All fields are required'}), 400
            
        if new_password != confirm_password:
            return jsonify({'error': 'New passwords do not match'}), 400
            
        is_strong, message = validate_password_strength(new_password)
        if not is_strong:
            return jsonify({'error': message}), 400
            
        user = User.get_user_by_id(session['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        if not User.verify_user(user['username'], current_password):
            return jsonify({'error': 'Current password is incorrect'}), 400
            
        User.update_password(session['user_id'], new_password)
        return jsonify({'message': 'Password updated successfully'}), 200
    except Exception as e:
        print(f"Change password error: {e}")
        return jsonify({'error': 'Failed to update password'}), 500

@bp.route('/change-username', methods=['POST'])
def change_username():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
        
    try:
        data = request.get_json() if request.is_json else request.form
        new_username = data.get('new_username', '').strip() if data.get('new_username') else ''
        current_password = data.get('current_password', '')
        
        if not all([new_username, current_password]):
            return jsonify({'error': 'Username and current password are required'}), 400
            
        if len(new_username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters long'}), 400
        if len(new_username) > 50:
            return jsonify({'error': 'Username cannot be longer than 50 characters'}), 400
        if not re.match(r'^[a-zA-Z0-9_]+$', new_username):
            return jsonify({'error': 'Username can only contain letters, numbers, and underscores'}), 400
            
        user = User.get_user_by_id(session['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        if not User.verify_user(user['username'], current_password):
            return jsonify({'error': 'Current password is incorrect'}), 400
            
        User.update_username(session['user_id'], new_username)
        session['username'] = new_username
        return jsonify({'message': 'Username updated successfully', 'new_username': new_username}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"Change username error: {e}")
        return jsonify({'error': 'Failed to update username'}), 500
