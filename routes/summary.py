from flask import Blueprint, jsonify, session
from models.transaction import Transaction

bp = Blueprint('summary', __name__, url_prefix='/api/summary')

@bp.route('', methods=['GET'])
def get_summary():
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    return jsonify(Transaction.summary(session['user_id']))

@bp.route('/current-month', methods=['GET'])
def get_current_month_summary():
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    return jsonify(Transaction.current_month_summary(session['user_id']))
