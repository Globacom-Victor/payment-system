from flask import Flask, render_template, request, jsonify
from payment_service_v2 import PaymentServiceV2
from database import get_session
from crypto_api import CryptoAPIException
from datetime import datetime, timedelta
import logging
from sqlalchemy import func
from models import Transaction

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== Dashboard Routes ====================

@app.route('/')
def dashboard():
    """Main payment dashboard"""
    return render_template('dashboard.html')

@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        session = get_session()
        
        # Total transactions
        total_transactions = session.query(Transaction).count()
        
        # Transactions by status
        pending = session.query(Transaction).filter_by(status='pending').count()
        confirmed = session.query(Transaction).filter_by(status='confirmed').count()
        completed = session.query(Transaction).filter_by(status='completed').count()
        failed = session.query(Transaction).filter_by(status='failed').count()
        
        # Total volume in USD (converted)
        total_volume = session.query(func.sum(Transaction.fiat_amount)).filter(
            Transaction.fiat_symbol == 'USD'
        ).scalar() or 0
        
        # Last 7 days transactions
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        transactions_7d = session.query(Transaction).filter(
            Transaction.created_at >= seven_days_ago
        ).count()
        
        return jsonify({
            'success': True,
            'total_transactions': total_transactions,
            'status_breakdown': {
                'pending': pending,
                'confirmed': confirmed,
                'completed': completed,
                'failed': failed
            },
            'total_volume_usd': float(total_volume),
            'transactions_7d': transactions_7d,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@app.route('/api/dashboard/transactions', methods=['GET'])
def get_all_transactions():
    """Get all transactions with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status_filter = request.args.get('status', None)
        crypto_filter = request.args.get('crypto', None)
        
        session = get_session()
        query = session.query(Transaction)
        
        # Apply filters
        if status_filter:
            query = query.filter_by(status=status_filter)
        if crypto_filter:
            query = query.filter_by(crypto_symbol=crypto_filter)
        
        # Get total count
        total = query.count()
        
        # Paginate
        transactions = query.order_by(
            Transaction.created_at.desc()
        ).offset((page - 1) * per_page).limit(per_page).all()
        
        # Format transactions
        formatted_transactions = []
        for tx in transactions:
            formatted_transactions.append({
                'id': tx.id,
                'crypto_symbol': tx.crypto_symbol,
                'fiat_symbol': tx.fiat_symbol,
                'fiat_amount': float(tx.fiat_amount),
                'crypto_amount': float(tx.crypto_amount),
                'wallet_address': tx.wallet_address,
                'exchange_rate': float(tx.exchange_rate),
                'status': tx.status,
                'created_at': tx.created_at.isoformat(),
                'updated_at': tx.updated_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'data': formatted_transactions,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting transactions: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@app.route('/api/dashboard/analytics', methods=['GET'])
def get_analytics():
    """Get analytics data (charts, trends, etc.)"""
    try:
        session = get_session()
        
        # Transaction count by crypto
        crypto_breakdown = session.query(
            Transaction.crypto_symbol,
            func.count(Transaction.id).label('count'),
            func.sum(Transaction.fiat_amount).label('total_volume')
        ).group_by(Transaction.crypto_symbol).all()
        
        crypto_data = []
        for crypto, count, volume in crypto_breakdown:
            crypto_data.append({
                'crypto': crypto,
                'transactions': count,
                'volume': float(volume or 0)
            })
        
        # Transaction status distribution
        status_breakdown = session.query(
            Transaction.status,
            func.count(Transaction.id).label('count')
        ).group_by(Transaction.status).all()
        
        status_data = []
        for status, count in status_breakdown:
            status_data.append({
                'status': status,
                'count': count
            })
        
        # Daily transactions (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        daily_transactions = session.query(
            func.date(Transaction.created_at).label('date'),
            func.count(Transaction.id).label('count'),
            func.sum(Transaction.fiat_amount).label('volume')
        ).filter(
            Transaction.created_at >= thirty_days_ago
        ).group_by(
            func.date(Transaction.created_at)
        ).order_by(
            func.date(Transaction.created_at)
        ).all()
        
        daily_data = []
        for date, count, volume in daily_transactions:
            daily_data.append({
                'date': str(date),
                'transactions': count,
                'volume': float(volume or 0)
            })
        
        return jsonify({
            'success': True,
            'crypto_breakdown': crypto_data,
            'status_breakdown': status_data,
            'daily_transactions': daily_data,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@app.route('/api/dashboard/transaction/<transaction_id>', methods=['GET'])
def get_transaction_detail(transaction_id):
    """Get detailed transaction information"""
    try:
        session = get_session()
        service = PaymentServiceV2(session)
        
        transaction = service.get_transaction_status(transaction_id)
        
        return jsonify({
            'success': True,
            'data': {
                'id': transaction.id,
                'crypto_symbol': transaction.crypto_symbol,
                'fiat_symbol': transaction.fiat_symbol,
                'fiat_amount': float(transaction.fiat_amount),
                'crypto_amount': float(transaction.crypto_amount),
                'wallet_address': transaction.wallet_address,
                'exchange_rate': float(transaction.exchange_rate),
                'status': transaction.status,
                'created_at': transaction.created_at.isoformat(),
                'updated_at': transaction.updated_at.isoformat()
            }
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error getting transaction detail: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@app.route('/api/dashboard/transaction/<transaction_id>/update-status', methods=['POST'])
def update_transaction_status(transaction_id):
    """Update transaction status (admin only)"""
    try:
        data = request.json
        new_status = data.get('status')
        
        if new_status not in ['pending', 'confirmed', 'completed', 'failed']:
            return jsonify({'error': 'Invalid status'}), 400
        
        session = get_session()
        service = PaymentServiceV2(session)
        
        transaction = service.update_transaction_status(transaction_id, new_status)
        
        return jsonify({
            'success': True,
            'message': f'Transaction status updated to {new_status}',
            'data': {
                'id': transaction.id,
                'status': transaction.status,
                'updated_at': transaction.updated_at.isoformat()
            }
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error updating transaction status: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@app.route('/api/dashboard/export', methods=['GET'])
def export_data():
    """Export transactions as CSV"""
    try:
        import csv
        from io import StringIO
        
        session = get_session()
        transactions = session.query(Transaction).order_by(
            Transaction.created_at.desc()
        ).all()
        
        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'Transaction ID', 'Crypto', 'Fiat', 'Fiat Amount', 'Crypto Amount',
            'Exchange Rate', 'Wallet Address', 'Status', 'Created At', 'Updated At'
        ])
        
        for tx in transactions:
            writer.writerow([
                tx.id,
                tx.crypto_symbol,
                tx.fiat_symbol,
                float(tx.fiat_amount),
                float(tx.crypto_amount),
                float(tx.exchange_rate),
                tx.wallet_address,
                tx.status,
                tx.created_at,
                tx.updated_at
            ])
        
        from flask import Response
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=transactions.csv'}
        )
        
    except Exception as e:
        logger.error(f"Error exporting data: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("Starting Payment Dashboard Server...")
    app.run(debug=True, host='0.0.0.0', port=5000)
