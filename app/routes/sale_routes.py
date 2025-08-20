from flask import Blueprint, request, jsonify
from app import db
from app.models.product import Product
from app.models.batch import Batch
from app.models.sale import Sale
from app.models.sale_item import SaleItem

sale_bp = Blueprint('sale', __name__)

@sale_bp.route('/sales', methods=['POST'])
def create_sale():
    """
    Body esperado:
    {
      "items": [
        {"product_id": 1, "quantity": 3},
        {"product_id": 2, "quantity": 5}
      ]
    }
    Reglas:
    - Se descuenta stock del lote más caro primero.
    - El precio de venta se calcula con (costo_lote * (1 + markup/100)).
    """
    data = request.get_json()
    items_data = data.get('items', [])
    if not items_data:
        return jsonify({'error': 'Debe incluir items'}), 400

    total_sale = 0
    sale = Sale(total=0)
    db.session.add(sale)

    for item in items_data:
        product = Product.query.get(item['product_id'])
        if not product:
            return jsonify({'error': f'Producto {item["product_id"]} no encontrado'}), 404

        qty_needed = float(item['quantity'])
        if qty_needed <= 0:
            return jsonify({'error': 'La cantidad debe ser > 0'}), 400

        # Lotes ordenados: más caro primero
        batches = sorted(product.batches, key=lambda b: (-b.cost, b.date_added))
        qty_to_sell = qty_needed
        for batch in batches:
            if qty_to_sell <= 0:
                break
            if batch.quantity <= 0:
                continue

            take_qty = min(batch.quantity, qty_to_sell)
            sale_price_unit = batch.cost * (1 + product.markup / 100.0)

            sale_item = SaleItem(
                sale=sale,
                product_id=product.id,
                batch_id=batch.id,
                quantity=take_qty,
                price_at_sale=sale_price_unit
            )
            db.session.add(sale_item)

            # Descontar stock
            batch.quantity -= take_qty
            qty_to_sell -= take_qty

            total_sale += take_qty * sale_price_unit

        if qty_to_sell > 0:
            return jsonify({'error': f'Stock insuficiente para producto {product.id}'}), 409

    sale.total = total_sale
    db.session.commit()

    return jsonify({'message': 'Venta registrada', 'sale_id': sale.id, 'total': total_sale}), 201


@sale_bp.route('/sales', methods=['GET'])
def list_sales():
    sales = Sale.query.order_by(Sale.date.desc()).all()
    result = []
    for s in sales:
        items = [{
            'product_id': i.product_id,
            'batch_id': i.batch_id,
            'quantity': i.quantity,
            'price_at_sale': i.price_at_sale
        } for i in s.items]

        result.append({
            'id': s.id,
            'date': s.date.isoformat(),
            'total': s.total,
            'items': items
        })
    return jsonify(result)


@sale_bp.route('/sales/<int:sale_id>', methods=['DELETE'])
def delete_sale(sale_id):
    sale = Sale.query.get_or_404(sale_id)

    # Revertir stock en cada lote
    for item in sale.items:
        batch = Batch.query.get(item.batch_id)
        if batch:
            batch.quantity += item.quantity

    db.session.delete(sale)
    db.session.commit()
    return jsonify({'message': f'Venta {sale_id} anulada y stock revertido'})