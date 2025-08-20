from datetime import datetime
from app import db

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    # "add_batch": se agregó un lote nuevo más barato
    # "consolidate": se consolidaron lotes a un costo más alto
    action = db.Column(db.String(20), nullable=False)

    # Para poder validar/anular:
    # - Si action == "add_batch": guardamos el batch_id creado.
    created_batch_id = db.Column(db.Integer, db.ForeignKey('batch.id'), nullable=True)

    # - Si action == "consolidate": guardamos un snapshot JSON (como TEXT) de los lotes previos
    #   para poder restaurarlos si no hubo operaciones posteriores.
    prev_batches_snapshot = db.Column(db.Text, nullable=True)

    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product = db.relationship('Product', backref='purchases')

    # datos de la compra (para auditoría)
    unit_cost = db.Column(db.Float, nullable=False)    # costo del lote comprado (por kg)
    quantity = db.Column(db.Float, nullable=False)     # cantidad en kg comprada