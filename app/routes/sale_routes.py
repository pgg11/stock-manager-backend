from flask import Blueprint, request, jsonify
from app import db
from app.models.product import Product
from app.models.sale import Sale, SaleItem

sale_bp = Blueprint('sale', __name__)

@sale_bp.route('/sales', methods=['POST'])
def create_sale():
    data = request.get_json()
    items = data.get('items', [])

    if not items:
        return jsonify({'error': 'Debe incluir al menos un producto'}), 400

    total = 0
    sale_items = []

    for item in items:
        product = Product.query.get(item['product_id'])
        if not product or product.quantity < item['quantity']:
            return jsonify({'error': f"Stock insuficiente o producto no encontrado: {item['product_id']}"}), 400

        subtotal = product.price * item['quantity']
        total += subtotal

        sale_item = SaleItem(
            product_id=product.id,
            quantity=item['quantity'],
            price_at_sale=product.price
        )
        sale_items.append(sale_item)
        product.quantity -= item['quantity']

    sale = Sale(total=total)
    sale.items = sale_items

    db.session.add(sale)
    db.session.commit()

    return jsonify({'message': 'Venta registrada', 'total': total}), 201

@sale_bp.route('/sales', methods=['GET'])
def get_sales():
    sales = Sale.query.order_by(Sale.date.desc()).all()
    result = []

    for sale in sales:
        items = [{
            'product_name': item.product.name,
            'quantity': item.quantity,
            'price_at_sale': item.price_at_sale
        } for item in sale.items]

        result.append({
            'id': sale.id,
            'date': sale.date.strftime('%Y-%m-%d %H:%M'),
            'total': sale.total,
            'items': items
        })

    return jsonify(result)

@sale_bp.route('/sales/<int:sale_id>', methods=['DELETE'])
def delete_sale(sale_id):
    sale = Sale.query.get_or_404(sale_id)

    # Revertir el stock de cada producto de la venta
    for item in sale.items:
        product = Product.query.get(item.product_id)
        if product:
            product.quantity += item.quantity

    db.session.delete(sale)
    db.session.commit()

    return jsonify({'message': f'Venta {sale_id} eliminada y stock revertido'})