from flask import Blueprint, request, jsonify, session, send_file
from models.transaction import Transaction
import io
import xlsxwriter
from datetime import datetime

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

@bp.route('/<int:transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    err = require_login()
    if err:
        return err
    try:
        transaction = Transaction.get_by_id(session['user_id'], transaction_id)
        if not transaction:
            return jsonify({'error': 'Transaction not found'}), 404
        return jsonify(transaction), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:transaction_id>', methods=['PUT'])
def update_transaction(transaction_id):
    err = require_login()
    if err:
        return err
    data = request.get_json()
    
    # Validate required fields
    for field in ['amount', 'category', 'type', 'date']:
        if field not in data or not data[field]:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Validate transaction type
    if data['type'] not in ['income', 'expense']:
        return jsonify({'error': 'Type must be either income or expense'}), 400
    
    try:
        updated = Transaction.update(
            session['user_id'],
            transaction_id,
            float(data['amount']),
            data['category'],
            data['type'],
            data['date'],
            data.get('description', '')
        )
        
        if not updated:
            return jsonify({'error': 'Transaction not found'}), 404
        
        return jsonify({'message': 'Transaction updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/download', methods=['POST'])
def download_filtered_transactions():
    """Download filtered transactions as Excel file"""
    err = require_login()
    if err:
        return err
    
    try:
        # Get filter parameters from request
        data = request.get_json()
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        # Get all transactions for the user
        all_transactions = Transaction.get_all(session['user_id'])
        
        # Apply date filtering
        filtered_transactions = []
        for transaction in all_transactions:
            transaction_date = datetime.strptime(transaction['date'], '%Y-%m-%d').date()
            
            # Check if transaction falls within date range
            include = True
            if start_date:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                if transaction_date < start_date_obj:
                    include = False
            
            if end_date and include:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                if transaction_date > end_date_obj:
                    include = False
            
            if include:
                filtered_transactions.append(transaction)
        
        # Create Excel file in memory
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Transactions')
        
        # Add headers
        headers = ['Date', 'Type', 'Category', 'Amount', 'Description']
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4CAF50',
            'color': 'white',
            'border': 1
        })
        
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header, header_format)
        
        # Add data formatting
        income_format = workbook.add_format({
            'color': '#4CAF50',
            'border': 1
        })
        expense_format = workbook.add_format({
            'color': '#f44336',
            'border': 1
        })
        regular_format = workbook.add_format({
            'border': 1
        })
        currency_format = workbook.add_format({
            'num_format': '₹#,##0.00',
            'border': 1
        })
        
        # Add transaction data
        for row_num, transaction in enumerate(filtered_transactions, start=1):
            # Format date
            date_obj = datetime.strptime(transaction['date'], '%Y-%m-%d')
            formatted_date = date_obj.strftime('%d/%m/%Y')
            worksheet.write(row_num, 0, formatted_date, regular_format)
            
            # Type with color formatting
            transaction_type = transaction['type'].capitalize()
            type_format = income_format if transaction['type'] == 'income' else expense_format
            worksheet.write(row_num, 1, transaction_type, type_format)
            
            # Category
            worksheet.write(row_num, 2, transaction['category'], regular_format)
            
            # Amount with currency formatting and sign
            amount_value = transaction['amount']
            if transaction['type'] == 'expense':
                amount_value = -amount_value
            worksheet.write(row_num, 3, amount_value, currency_format)
            
            # Description
            description = transaction.get('description', '') or '-'
            worksheet.write(row_num, 4, description, regular_format)
        
        # Adjust column widths
        worksheet.set_column('A:A', 12)  # Date
        worksheet.set_column('B:B', 10)  # Type
        worksheet.set_column('C:C', 20)  # Category
        worksheet.set_column('D:D', 15)  # Amount
        worksheet.set_column('E:E', 30)  # Description
        
        # Add summary at the bottom if there are transactions
        if filtered_transactions:
            summary_row = len(filtered_transactions) + 2
            
            # Calculate totals
            total_income = sum(t['amount'] for t in filtered_transactions if t['type'] == 'income')
            total_expense = sum(t['amount'] for t in filtered_transactions if t['type'] == 'expense')
            net_balance = total_income - total_expense
            
            # Add summary headers
            summary_format = workbook.add_format({
                'bold': True,
                'bg_color': '#f0f0f0',
                'border': 1
            })
            
            worksheet.write(summary_row, 0, 'SUMMARY', summary_format)
            worksheet.write(summary_row + 1, 0, 'Total Income:', summary_format)
            worksheet.write(summary_row + 1, 1, total_income, currency_format)
            worksheet.write(summary_row + 2, 0, 'Total Expenses:', summary_format)
            worksheet.write(summary_row + 2, 1, total_expense, currency_format)
            worksheet.write(summary_row + 3, 0, 'Net Balance:', summary_format)
            
            balance_format = workbook.add_format({
                'bold': True,
                'color': '#4CAF50' if net_balance >= 0 else '#f44336',
                'num_format': '₹#,##0.00',
                'border': 1
            })
            worksheet.write(summary_row + 3, 1, net_balance, balance_format)
        
        workbook.close()
        output.seek(0)
        
        # Generate filename based on filter
        filename = 'transactions'
        if start_date and end_date:
            filename += f'_{start_date}_to_{end_date}'
        elif start_date:
            filename += f'_from_{start_date}'
        elif end_date:
            filename += f'_until_{end_date}'
        else:
            filename += '_all'
        filename += '.xlsx'
        
        return send_file(
            output, 
            download_name=filename, 
            as_attachment=True, 
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
