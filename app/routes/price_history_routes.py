from flask import Blueprint, jsonify
from app.models.price_history import PriceHistory

price_history_bp = Blueprint('price_history', __name__)

@price_history_bp.route('/price-history/<int:product_id>', methods=['GET'])
def get_price_history(product_id):
    history = PriceHistory.query.filter_by(product_id=product_id).order_by(PriceHistory.date.asc()).all()
    result = []
    for h in history:
        result.append({
            'id': h.id,
            'product_id': h.product_id,
            'cost': h.cost,
            'price': h.price,
            'date': h.date.isoformat()
        })
    return jsonify(result)