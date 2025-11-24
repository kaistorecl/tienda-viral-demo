import os
from flask import Flask, render_template, request, redirect

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
    # 1. Capturamos lo que el usuario escribió en el buscador (si escribió algo)
    busqueda = request.args.get('q')
    
    # 2. Si hay búsqueda, filtramos el catálogo
    if busqueda:
        # Convertimos todo a minúsculas para que "GEL" y "gel" sean lo mismo
        busqueda = busqueda.lower()
        productos_filtrados = [
            p for p in CATALOGO 
            if busqueda in p['nombre'].lower() or busqueda in p['descripcion'].lower()
        ]
    else:
        # Si no buscó nada, mostramos todo
        productos_filtrados = CATALOGO

    # 3. Enviamos a la web los productos (filtrados o todos) y el término buscado
    return render_template('home.html', catalogo=productos_filtrados, busqueda_actual=busqueda)

@app.route('/producto/<int:id_prod>')
def producto(id_prod):
    # Busca el producto específico por ID
    producto_encontrado = next((p for p in CATALOGO if p["id"] == id_prod), None)
    
    if producto_encontrado:
        return render_template('index.html', producto=producto_encontrado)
    else:
        return "<h1>Producto no encontrado :(</h1><a href='/'>Volver al inicio</a>", 404

if __name__ == '__main__':
    app.run(debug=True)