import os
import logging
from functools import wraps
from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

# --- Configuración de Logs ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Inicialización de la Base de Datos ---
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # --- Configuración ---
    # Render provee DATABASE_URL. Si no existe, usa SQLite local para pruebas.
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///local_store.db')
    
    # FIX CRÍTICO PARA RENDER: SQLAlchemy requiere 'postgresql://', Render a veces da 'postgres://'
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # CLAVE DE SEGURIDAD: Define esto en las variables de entorno de Render
    app.config['ADMIN_API_KEY'] = os.environ.get('ADMIN_API_KEY', 'default_insegura_cambiar_en_prod')

    db.init_app(app)

    # Crear tablas automáticamente al iniciar (simple para este caso de uso)
    with app.app_context():
        db.create_all()
        logger.info("Base de datos inicializada correctamente.")

    # Registrar rutas
    register_routes(app)
    
    return app

# --- Modelos ---

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(500), nullable=True)

    def to_dict(self):
        return {
            'sku': self.sku,
            'name': self.name,
            'price': self.price,
            'stock': self.stock,
            'description': self.description,
            'image_url': self.image_url
        }

# --- Decorador de Seguridad ---

def require_api_key(f):
    """Protege el endpoint para que solo GAS pueda llamar."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Buscamos la key en los headers
        auth_header = request.headers.get('X-API-KEY')
        from flask import current_app
        if auth_header != current_app.config['ADMIN_API_KEY']:
            logger.warning(f"Intento de acceso no autorizado desde {request.remote_addr}")
            return jsonify({'error': 'No autorizado'}), 401
        return f(*args, **kwargs)
    return decorated_function

# --- Rutas ---

def register_routes(app):
    
    @app.route('/')
    def index():
        """Endpoint público para ver la tienda."""
        try:
            products = Product.query.all()
            return jsonify({
                'status': 'online',
                'product_count': len(products),
                'products': [p.to_dict() for p in products]
            })
        except Exception as e:
            logger.error(f"Error al obtener productos: {e}")
            return jsonify({'error': 'Error interno'}), 500

    @app.route('/api/sync', methods=['POST'])
    @require_api_key
    def sync_products():
        """
        Recibe un JSON con una lista de productos desde Apify/GAS.
        Actualiza si existe (upsert) o crea si es nuevo.
        Estructura esperada: { "items": [ { "sku": "...", "name": "...", ... } ] }
        """
        data = request.get_json()
        
        if not data or 'items' not in data:
            return jsonify({'error': 'JSON inválido o falta la clave "items"'}), 400

        items = data['items']
        updated_count = 0
        created_count = 0

        try:
            for item in items:
                sku = item.get('sku')
                if not sku:
                    continue # Saltar items sin SKU

                # Buscar producto existente
                product = Product.query.filter_by(sku=sku).first()
                
                # Datos a guardar (con valores por defecto seguros)
                p_name = item.get('title', item.get('name', 'Sin Nombre'))
                p_price = float(item.get('price', 0.0))
                p_stock = int(item.get('stock', item.get('inventory', 0)))
                p_desc = item.get('description', '')
                p_img = item.get('image', '')

                if product:
                    # Actualizar
                    product.name = p_name
                    product.price = p_price
                    product.stock = p_stock
                    product.description = p_desc
                    product.image_url = p_img
                    updated_count += 1
                else:
                    # Crear
                    new_product = Product(
                        sku=sku,
                        name=p_name,
                        price=p_price,
                        stock=p_stock,
                        description=p_desc,
                        image_url=p_img
                    )
                    db.session.add(new_product)
                    created_count += 1
            
            db.session.commit()
            logger.info(f"Sincronización completada: {created_count} creados, {updated_count} actualizados.")
            
            return jsonify({
                'message': 'Sincronización exitosa',
                'created': created_count,
                'updated': updated_count
            }), 200

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error durante la sincronización: {e}")
            return jsonify({'error': str(e)}), 500

# Necesario para Gunicorn en Render
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
