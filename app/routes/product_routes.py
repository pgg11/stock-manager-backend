from flask import Blueprint, request, jsonify
from app import db
from app.models.product import Product
from app.models.batch import Batch
from app.models.price_history import PriceHistory

product_bp = Blueprint('product', __name__)

@product_bp.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    result = []
    for p in products:
        batches = [{'id': b.id, 'cost': b.cost, 'quantity': b.quantity, 'date_added': b.date_added.isoformat()}
                   for b in sorted(p.batches, key=lambda x: (-x.cost, x.date_added))]
        result.append({
            'id': p.id,
            'name': p.name,
            'markup': p.markup,
            'total_stock': p.total_stock(),
            'batches': batches
        })
    return jsonify(result)

@product_bp.route('/products', methods=['POST'])
def add_product():
    data = request.get_json()
    name = data.get('name')
    markup = float(data.get('markup', 0.0))
    if not name:
        return jsonify({'error': 'name es requerido'}), 400

    # producto sin lotes al crear; los lotes llegan vía compras
    p = Product(name=name, markup=markup)
    db.session.add(p)
    db.session.commit()
    return jsonify({'message': 'Producto creado', 'id': p.id}), 201

@product_bp.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json()

    if 'name' in data:
        product.name = data['name']

    if 'markup' in data:
        product.markup = float(data['markup'])

        # 👇 Registrar en PriceHistory si hay lotes
        if product.batches:
            highest_cost = max(b.cost for b in product.batches)
            ph = PriceHistory(
                product_id=product.id,
                cost=highest_cost,
                price=highest_cost * (1 + product.markup / 100.0)
            )
            db.session.add(ph)

    db.session.commit()
    return jsonify({'message': 'Producto actualizado'})