from app import db

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    markup = db.Column(db.Float, default=0.0)  # porcentaje de ganancia vigente

    batches = db.relationship('Batch', backref='product', cascade="all, delete-orphan")

    def total_stock(self):
        return sum(b.quantity for b in self.batches)