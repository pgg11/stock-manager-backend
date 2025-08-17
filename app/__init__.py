from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stock.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Importar modelos (necesario para crear las tablas)
    from .models import product, sale

    # Registrar rutas
    from .routes.product_routes import product_bp
    from .routes.sale_routes import sale_bp
    app.register_blueprint(product_bp)
    app.register_blueprint(sale_bp)

    return app