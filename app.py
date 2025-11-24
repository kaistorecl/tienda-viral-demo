import os
from flask import Flask, render_template, redirect, request
import stripe

app = Flask(__name__)

# Configuración de Stripe (busca las claves en las variables de entorno)
# Si no encuentra las claves, usa valores vacíos para que no falle al iniciar, pero el pago fallará si no se configuran.
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'clave_falsa_por_ahora')
DOMAIN = os.environ.get('DOMAIN_URL', 'http://127.0.0.1:5000')

# DATOS DEL PRODUCTO (Aspiradora)
PRODUCTO = {
    'nombre': 'Aspiradora TurboCar Pro',
    'precio': 24990,  # En Pesos Chilenos
    'imagen': 'https://http2.mlstatic.com/D_NQ_NP_967683-MLC72561023773_112023-O.webp', # Imagen referencial de MercadoLibre
    'descripcion': 'La aspiradora inalámbrica más potente para tu auto. ¡Limpia en segundos!'
}

@app.route('/')
def index():
    return render_template('index.html', producto=PRODUCTO)

@app.route('/comprar', methods=['POST'])
def comprar():
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'clp',
                    'product_data': {
                        'name': PRODUCTO['nombre'],
                        'images': [PRODUCTO['imagen']],
                    },
                    'unit_amount': PRODUCTO['precio'] * 100, # Stripe usa centavos
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=DOMAIN + '/success',
            cancel_url=DOMAIN + '/',
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        return f"Error de configuración de Stripe: {str(e)}"

@app.route('/success')
def success():
    return "<h1>¡Pago Exitoso! 🚗✨</h1><p>Gracias por tu compra. Te contactaremos pronto.</p>"

if __name__ == '__main__':
    app.run(debug=True)