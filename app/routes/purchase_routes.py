import json
from flask import Blueprint, request, jsonify
from app import db
from app.models.product import Product
from app.models.batch import Batch
from app.models.purchase import Purchase
from app.models.price_history import PriceHistory

purchase_bp = Blueprint('purchase', __name__)

def _current_highest_cost(product: Product) -> float | None:
    if not product.batches:
        return None
    return max(b.cost for b in product.batches)

@purchase_bp.route('/purchases', methods=['POST'])
def create_purchase():
    """
    Body esperado:
    {
      "product_id": 1,
      "unit_cost": 1200.0,
      "quantity": 10.5
    }
    Regla:
    - Si unit_cost > costo_máximo_actual -> consolidar: todo el stock existente pasa a unit_cost y se suma la nueva cantidad
    - Si unit_cost <= costo_máximo_actual -> crear un lote nuevo independiente
    """
    data = request.get_json()
    product_id = data.get('product_id')
    unit_cost = data.get('unit_cost')
    quantity = data.get('quantity')

    if not all([product_id, unit_cost is not None, quantity is not None]):
        return jsonify({'error': 'product_id, unit_cost y quantity son requeridos'}), 400

    product = Product.query.get_or_404(product_id)
    unit_cost = float(unit_cost)
    quantity = float(quantity)
    if quantity <= 0 or unit_cost <= 0:
        return jsonify({'error': 'quantity y unit_cost deben ser > 0'}), 400

    highest = _current_highest_cost(product)

    if highest is None:
        # primer lote
        new_batch = Batch(product_id=product.id, cost=unit_cost, quantity=quantity)
        db.session.add(new_batch)
        db.session.flush()  # obtener id
        purchase = Purchase(
            action='add_batch',
            created_batch_id=new_batch.id,
            product_id=product.id,
            unit_cost=unit_cost,
            quantity=quantity
        )
        db.session.add(purchase)

        # registrar en PriceHistory
        ph = PriceHistory(
            product_id=product.id,
            cost=unit_cost,
            price=unit_cost * (1 + product.markup / 100.0)
        )
        db.session.add(ph)

        db.session.commit()
        return jsonify({'message': 'Compra registrada (primer lote)', 'purchase_id': purchase.id}), 201

    if unit_cost > highest:
        # CONSOLIDAR: mover todo a un solo lote con el nuevo costo, sumando la nueva cantidad.
        prev = [{'batch_id': b.id, 'cost': b.cost, 'quantity': b.quantity} for b in product.batches]
        total_qty = sum(b['quantity'] for b in prev) + quantity

        # eliminar lotes previos
        for b in list(product.batches):
            db.session.delete(b)
        db.session.flush()

        # crear lote único consolidado
        consolidated = Batch(product_id=product.id, cost=unit_cost, quantity=total_qty)
        db.session.add(consolidated)
        db.session.flush()

        purchase = Purchase(
            action='consolidate',
            created_batch_id=consolidated.id,
            prev_batches_snapshot=json.dumps(prev),
            product_id=product.id,
            unit_cost=unit_cost,
            quantity=quantity
        )
        db.session.add(purchase)

        # registrar en PriceHistory
        ph = PriceHistory(
            product_id=product.id,
            cost=unit_cost,
            price=unit_cost * (1 + product.markup / 100.0)
        )
        db.session.add(ph)

        db.session.commit()
        return jsonify({'message': 'Compra registrada (consolidación a costo más alto)', 'purchase_id': purchase.id}), 201

    # unit_cost <= highest  -> lote nuevo más barato
    new_batch = Batch(product_id=product.id, cost=unit_cost, quantity=quantity)
    db.session.add(new_batch)
    db.session.flush()
    purchase = Purchase(
        action='add_batch',
        created_batch_id=new_batch.id,
        product_id=product.id,
        unit_cost=unit_cost,
        quantity=quantity
    )
    db.session.add(purchase)

    # registrar en PriceHistory
    ph = PriceHistory(
        product_id=product.id,
        cost=unit_cost,
        price=unit_cost * (1 + product.markup / 100.0)
    )
    db.session.add(ph)

    db.session.commit()
    return jsonify({'message': 'Compra registrada (nuevo lote más barato)', 'purchase_id': purchase.id}), 201


@purchase_bp.route('/purchases', methods=['GET'])
def list_purchases():
    purchases = Purchase.query.order_by(Purchase.date.desc()).all()
    result = []
    for p in purchases:
        result.append({
            'id': p.id,
            'date': p.date.isoformat(),
            'product_id': p.product_id,
            'action': p.action,
            'unit_cost': p.unit_cost,
            'quantity': p.quantity,
            'created_batch_id': p.created_batch_id
        })
    return jsonify(result)


@purchase_bp.route('/purchases/<int:purchase_id>', methods=['DELETE'])
def delete_purchase(purchase_id):
    """
    Anulación con verificación de stock:
    - Si fue "add_batch": solo se puede borrar si el lote creado conserva al menos la cantidad comprada (no fue consumido).
      Se descuenta esa cantidad del lote; si queda en 0, se elimina el lote.
    - Si fue "consolidate": por simplicidad y para no romper trazabilidad,
      solo permitimos borrar si NO hubo ventas ni compras posteriores del mismo producto desde esa fecha,
      y si el lote consolidado conserva el total de stock (nadie vendió).
      En ese caso, restauramos los lotes previos desde el snapshot.
    """
    import datetime
    data_now = datetime.datetime.utcnow()

    p = Purchase.query.get_or_404(purchase_id)
    product = Product.query.get_or_404(p.product_id)

    if p.action == 'add_batch':
        batch = Batch.query.get(p.created_batch_id)
        if not batch:
            return jsonify({'error': 'No se encontró el lote de la compra'}), 409
        if batch.quantity < p.quantity:
            return jsonify({'error': 'No se puede anular: parte del lote ya fue consumido'}), 409

        # revertir
        batch.quantity -= p.quantity
        if batch.quantity == 0:
            db.session.delete(batch)
        db.session.delete(p)
        db.session.commit()
        return jsonify({'message': 'Compra anulada y stock revertido (lote más barato)'}), 200

    if p.action == 'consolidate':
        consolidated = Batch.query.get(p.created_batch_id)
        if not consolidated:
            return jsonify({'error': 'Lote consolidado inexistente; no se puede anular de forma segura'}), 409

        try:
            prev = json.loads(p.prev_batches_snapshot or '[]')
        except Exception:
            prev = []

        expected_total = sum(x['quantity'] for x in prev) + p.quantity
        if consolidated.quantity < expected_total:
            return jsonify({'error': 'No se puede anular: stock del lote consolidado fue consumido'}), 409

        latest_purchase_after = Purchase.query.filter(
            Purchase.product_id == product.id,
            Purchase.id != p.id,
            Purchase.date > p.date
        ).first()
        if latest_purchase_after:
            return jsonify({'error': 'No se puede anular: hay compras posteriores del mismo producto'},), 409

        db.session.delete(consolidated)
        db.session.flush()
        for pb in prev:
            restored = Batch(product_id=product.id, cost=pb['cost'], quantity=pb['quantity'])
            db.session.add(restored)
        db.session.delete(p)
        db.session.commit()
        return jsonify({'message': 'Compra de consolidación anulada y lotes previos restaurados'}), 200

    return jsonify({'error': 'Acción de compra desconocida'}), 400