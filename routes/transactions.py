from flask import Blueprint, request, jsonify, session
from models.transaction import Transaction

bp = Blueprint('transactions', __name__, url_prefix='/api/transactions')

def require_login():
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    return None

@bp.route('', methods=['GET'])
def get_transactions():
    err = require_login()
    if err:
        return err
    return jsonify(Transaction.get_all(session['user_id']))

@bp.route('', methods=['POST'])
def add_transaction():
    err = require_login()
    if err:
        return err
    data = request.get_json()
    for field in ['amount', 'category', 'type', 'date']:
        if field not in data or not data[field]:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    if data['type'] not in ['income', 'expense']:
        return jsonify({'error': 'Type must be either income or expense'}), 400
    try:
        transaction_id = Transaction.create(
            session['user_id'],
            float(data['amount']),
            data['category'],
            data['type'],
            data['date'],
            data.get('description', '')
        )
        return jsonify({'id': transaction_id, 'message': 'Transaction added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    err = require_login()
    if err:
        return err
    try:
        deleted = Transaction.delete(session['user_id'], transaction_id)
        if not deleted:
            return jsonify({'error': 'Transaction not found'}), 404
        return jsonify({'message': 'Transaction deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
