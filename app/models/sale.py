from datetime import datetime
from app import db

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.Float, nullable=False)

    items = db.relationship('SaleItem', backref='sale', cascade="all, delete-orphan")