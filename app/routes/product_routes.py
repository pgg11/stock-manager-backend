from flask import Blueprint, request, jsonify
from app import db
from app.models.product import Product

product_bp = Blueprint('product', __name__)

@product_bp.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([
        {'id': p.id, 'name': p.name, 'price': p.price, 'quantity': p.quantity}
        for p in products
    ])

@product_bp.route('/products', methods=['POST'])
def add_product():
    data = request.get_json()
    product = Product(name=data['name'], price=data['price'], quantity=data.get('quantity', 0))
    db.session.add(product)
    db.session.commit()
    return jsonify({'message': 'Producto agregado'}), 201

@product_bp.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    product.name = data.get('name', product.name)
    product.price = data.get('price', product.price)
    product.quantity = data.get('quantity', product.quantity)
    db.session.commit()
    return jsonify({'message': 'Producto actualizado'})

@product_bp.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Producto eliminado'})