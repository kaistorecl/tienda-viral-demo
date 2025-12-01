import os
import logging
from functools import wraps
from flask import Flask, jsonify, request, abort, render_template
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
    
    # FIX CRÍTICO PARA RENDER: SQLAlchemy requiere 'postgresql://'
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # CLAVE DE SEGURIDAD
    app.config['ADMIN_API_KEY'] = os.environ.get('ADMIN_API_KEY', 'default_insegura_cambiar_en_prod')

    db.init_app(app)

    # Crear tablas automáticamente al iniciar
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

    # Propiedad auxiliar para el frontend (HTML espera 'imagen' y 'precio_antes')
    @property
    def serialize_for_template(self):
        return {
            'id': self.id,
            'sku': self.sku,
            'nombre': self.name,
            'precio': self.price,
            'antes': self.price * 1.4, # Simulación de precio "antes" (+40%) para marketing
            'stock': self.stock,
            'descripcion': self.description,
            'imagen': self.image_url or "https://via.placeholder.com/400"
        }

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
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('X-API-KEY')
        from flask import current_app
        if auth_header != current_app.config['ADMIN_API_KEY']:
            logger.warning(f"Intento de acceso no autorizado desde {request.remote_addr}")
            return jsonify({'error': 'No autorizado'}), 401
        return f(*args, **kwargs)
    return decorated_function

# --- Rutas ---

def register_routes(app):
    
    # 1. RUTA PRINCIPAL (Frontend HTML)
    @app.route('/')
    def index():
        """Renderiza la tienda visual (home.html)"""
        try:
            query = request.args.get('q') # Captura búsqueda del usuario
            
            if query:
                # Búsqueda insensible a mayúsculas
                products_db = Product.query.filter(Product.name.ilike(f'%{query}%')).all()
            else:
                products_db = Product.query.all()

            # Convertimos objetos DB a formato amigable para el template
            catalogo = [p.serialize_for_template for p in products_db]

            return render_template('home.html', catalogo=catalogo, busqueda_actual=query)
        except Exception as e:
            logger.error(f"Error cargando home: {e}")
            return "Error cargando la tienda", 500

    # 2. RUTA DE PRODUCTO (Frontend HTML)
    @app.route('/producto/<int:product_id>')
    def product_detail(product_id):
        """Renderiza la ficha de producto (index.html)"""
        try:
            product_db = Product.query.get_or_404(product_id)
            return render_template('index.html', producto=product_db.serialize_for_template)
        except Exception as e:
            logger.error(f"Error cargando producto {product_id}: {e}")
            return "Producto no encontrado", 404

    # 3. API SYNC (Backend para GAS)
    @app.route('/api/sync', methods=['POST'])
    @require_api_key
    def sync_products():
        """Endpoint para recibir datos desde Google Apps Script"""
        data = request.get_json()
        
        if not data or 'items' not in data:
            return jsonify({'error': 'JSON inválido'}), 400

        items = data['items']
        updated_count = 0
        created_count = 0

        try:
            for item in items:
                sku = item.get('sku')
                if not sku: continue 

                product = Product.query.filter_by(sku=sku).first()
                
                # Mapeo de datos entrantes
                p_name = item.get('title', item.get('name', 'Sin Nombre'))
                p_price = float(item.get('price', 0.0))
                p_stock = int(item.get('stock', item.get('inventory', 0)))
                p_desc = item.get('description', '')
                p_img = item.get('image', '')

                if product:
                    product.name = p_name
                    product.price = p_price
                    product.stock = p_stock
                    product.description = p_desc
                    product.image_url = p_img
                    updated_count += 1
                else:
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
            return jsonify({'message': 'OK', 'created': created_count, 'updated': updated_count}), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

# Inicialización para Gunicorn
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
