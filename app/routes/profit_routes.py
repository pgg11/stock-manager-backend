from flask import Blueprint, request, jsonify
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.batch import Batch
from app.models.product import Product
from datetime import datetime

profits_bp = Blueprint("profits", __name__)

@profits_bp.route("/profits", methods=["GET"])
def get_profits():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    try:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
    except Exception:
        return jsonify({"error": "Formato de fecha inválido"}), 400

    sales = Sale.query.filter(Sale.date >= start, Sale.date <= end).all()

    result = []
    total_profit = 0.0

    for s in sales:
        items = []
        sale_total = 0.0
        sale_profit = 0.0

        for item in s.items:
            product = Product.query.get(item.product_id)
            batch = Batch.query.get(item.batch_id)
            cost = batch.cost if batch else 0.0
            profit = (item.price_at_sale - cost) * item.quantity

            subtotal = item.price_at_sale * item.quantity

            items.append({
                "product_id": item.product_id,
                "product_name": product.name if product else f"#{item.product_id}",
                "quantity": round(item.quantity, 2),
                "unit_price": round(item.price_at_sale, 2),
                "subtotal": round(subtotal, 2),
                "cost": round(cost, 2)
            })

            sale_total += subtotal
            sale_profit += profit

        total_profit += sale_profit
        result.append({
            "sale_id": s.id,
            "date": s.date.isoformat(),
            "items": items,
            "total": round(sale_total, 2),
            "profit": round(sale_profit, 2)
        })

    return jsonify({
        "sales": result,
        "total_profit": round(total_profit, 2)
    })