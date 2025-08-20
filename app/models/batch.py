from datetime import datetime
from app import db

class Batch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    cost = db.Column(db.Float, nullable=False)        # costo por kg en este lote
    quantity = db.Column(db.Float, nullable=False)    # stock en kg
    date_added = db.Column(db.DateTime, default=datetime.utcnow)