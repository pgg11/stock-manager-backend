from datetime import datetime
from app import db

class PriceHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    cost = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.now)