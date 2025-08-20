from app import db

class SaleItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sale.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey('batch.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    price_at_sale = db.Column(db.Float, nullable=False)  # precio de venta unitario (costo*markup)