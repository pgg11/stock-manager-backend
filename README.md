# Stock Manager Backend

Aplicación backend en **Flask + SQLite** para la gestión de stock, compras y ventas de un emprendimiento de frutos secos.  
Incluye control de precios históricos y cálculo de ganancias en un rango de fechas.

## 🚀 Tecnologías usadas
- Python 3
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- SQLite

## 📦 Instalación

1. Clonar el repositorio:
   ```bash
   git clone git@github.com:pgg11/stock-manager-backend.git
   cd stock-manager-backend

2. Crear entorno virtual e instalar dependencias:
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

3. Inicializar la base de datos:
    flask db upgrade

4. Ejecutar la aplicación:
    python run.py

Por defecto corre en http://127.0.0.1:5000.

## 📂 Estructura del proyecto

    stock-manager-backend/
    ├── app/
    │   ├── __init__.py
    │   ├── models/
    │   │   ├── product.py
    │   │   ├── batch.py
    │   │   ├── purchase.py
    │   │   ├── sale.py
    │   │   ├── sale_item.py
    │   │   └── price_history.py
    │   └── routes/
    │       ├── product_routes.py
    │       ├── purchase_routes.py
    │       ├── sale_routes.py
    │       ├── price_history_routes.py
    │       └── profit_routes.py
    ├── migrations/
    ├── run.py
    ├── requirements.txt
    └── README.md

## 📌 Endpoints principales

Productos

    GET /products → listar productos y lotes

    POST /products → crear producto

    PUT /products/<id> → actualizar nombre/markup

Compras

    POST /purchases → registrar compra

    GET /purchases → listar compras

    DELETE /purchases/<id> → anular compra (si es posible)

Ventas

    POST /sales → registrar venta (con items)

    GET /sales → listar ventas

    DELETE /sales/<id> → anular venta y reponer stock

Historial de precios

    GET /price-history/<product_id> → consultar historial de un producto

Ganancias

    GET /profits?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD