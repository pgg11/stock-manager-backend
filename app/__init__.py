from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stock.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)

    # Importar modelos
    from .models import product, batch, purchase, sale

    # Registrar rutas
    from .routes.product_routes import product_bp
    from .routes.sale_routes import sale_bp
    from .routes.purchase_routes import purchase_bp
    from .routes.price_history_routes import price_history_bp
    from .routes.profit_routes import profits_bp


    app.register_blueprint(product_bp)
    app.register_blueprint(sale_bp)
    app.register_blueprint(purchase_bp)
    app.register_blueprint(price_history_bp)
    app.register_blueprint(profits_bp)

    return app