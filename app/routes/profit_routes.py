from flask import Blueprint, request, jsonify
from datetime import datetime
from app.models.sale import Sale
from app.models.price_history import PriceHistory
from app import db

profit_bp = Blueprint('profit', __name__)

@profit_bp.route('/profits', methods=['GET'])
def get_profits():
    """
    Parámetros:
    - start_date (YYYY-MM-DD)
    - end_date (YYYY-MM-DD)
    Ejemplo: /profits?start_date=2025-01-01&end_date=2025-12-31
    """

    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    if not start_date_str or not end_date_str:
        return jsonify({'error': 'start_date y end_date son requeridos'}), 400

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Formato de fecha inválido, usar YYYY-MM-DD'}), 400

    # Traer ventas en rango
    sales = Sale.query.filter(Sale.date >= start_date, Sale.date <= end_date).all()

    total_profit = 0.0
    details = {}

    for sale in sales:
        print(sale)
        for item in sale.items:
            # Buscar costo vigente en el momento de la venta
            cost_entry = (
                PriceHistory.query
                .filter(PriceHistory.product_id == item.product_id, PriceHistory.date <= sale.date)
                .order_by(PriceHistory.date.desc())
                .first()
            )
            if not cost_entry:
                continue  # sin costo registrado -> no se puede calcular

            cost = cost_entry.cost
            revenue = item.price_at_sale * item.quantity
            expense = cost * item.quantity
            profit = revenue - expense

            total_profit += profit

            if item.product_id not in details:
                details[item.product_id] = {
                    'product_id': item.product_id,
                    'revenue': 0.0,
                    'expense': 0.0,
                    'profit': 0.0
                }
            details[item.product_id]['revenue'] += revenue
            details[item.product_id]['expense'] += expense
            details[item.product_id]['profit'] += profit

    return jsonify({
        'start_date': start_date_str,
        'end_date': end_date_str,
        'total_profit': total_profit,
        'details': list(details.values())
    })