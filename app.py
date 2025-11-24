import os
from flask import Flask, render_template

app = Flask(__name__)

# --- BASE DE DATOS: CATÁLOGO DE AUTOS ---
CATALOGO = [
    {
        'id': 1,
        'nombre': 'Aspiradora TurboCar Pro',
        'precio': 24990,
        'antes': 49990,
        'imagen': 'https://http2.mlstatic.com/D_NQ_NP_967683-MLC72561023773_112023-O.webp',
        'descripcion': 'Potencia ciclónica para tu auto. Aspira polvo y líquidos en segundos.'
    },
    {
        'id': 2,
        'nombre': 'Gel Limpiador Mágico',
        'precio': 9990,
        'antes': 15990,
        'imagen': 'https://m.media-amazon.com/images/I/71wI-g7k1ZL._AC_SL1500_.jpg', 
        'descripcion': 'Atrapa el polvo de las rejillas de aire y lugares difíciles. No deja residuos.'
    },
    {
        'id': 3,
        'nombre': 'Organizador Asiento Premium',
        'precio': 19990,
        'antes': 29990,
        'imagen': 'https://m.media-amazon.com/images/I/71Y-V7-yIWL._AC_SL1500_.jpg',
        'descripcion': 'Mantén el orden con múltiples bolsillos para tablets, botellas y juguetes.'
    },
    {
        'id': 4,
        'nombre': 'Restaurador de Plásticos',
        'precio': 12990,
        'antes': 18990,
        'imagen': 'https://m.media-amazon.com/images/I/71+yC5+0cBL._AC_SL1500_.jpg',
        'descripcion': 'Devuelve el color negro intenso a tus parachoques y tablero gastado.'
    }
]

@app.route('/')
def home():
    # Muestra la vitrina con todos los productos
    return render_template('home.html', catalogo=CATALOGO)

@app.route('/producto/<int:id_prod>')
def producto(id_prod):
    # Busca el producto específico por ID
    producto_encontrado = next((p for p in CATALOGO if p["id"] == id_prod), None)
    if producto_encontrado:
        return render_template('index.html', producto=producto_encontrado)
    else:
        return "Producto no encontrado", 404

if __name__ == '__main__':
    app.run(debug=True)