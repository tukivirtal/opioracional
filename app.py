import os
from flask import Flask, request, jsonify
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

@app.route('/fabricar', methods=['POST'])
def fabricar_activo():
    # 1. Make nos enviará un Webhook con esta información
    datos = request.json
    titulo = datos.get('titulo', 'EL SECRETO ESTOICO')
    
    # Rutas de los archivos
    ruta_fuente = "Anton-Regular.ttf"
    ruta_imagen = "miniatura_base.jpg" # La imagen generada por Leonardo
    ruta_salida = "miniatura_final.jpg"
    
    try:
        # 2. El Motor de la Miniatura (Reemplazo de Creatomate)
        if os.path.exists(ruta_fuente) and os.path.exists(ruta_imagen):
            imagen = Image.open(ruta_imagen)
            dibujo = ImageDraw.Draw(imagen)
            
            # Tamaño de fuente adaptativo (11.1vmin equivalente)
            ancho_img, alto_img = imagen.size
            tamano_fuente = int(ancho_img * 0.111)
            fuente = ImageFont.truetype(ruta_fuente, tamano_fuente)
            
            # Posición exacta: 3.9% en X, 36.68% en Y
            pos_x = ancho_img * 0.039
            pos_y = alto_img * 0.3668
            
            # Sombreado y texto (Color crema base)
            dibujo.text((pos_x+5, pos_y+5), titulo, font=fuente, fill="black") # Sombra
            dibujo.text((pos_x, pos_y), titulo, font=fuente, fill="#fff9f8")   # Texto
            
            imagen.save(ruta_salida)
            
        # Aquí irá el bloque de MoviePy que probamos hoy en Colab
        # ...
        
        return jsonify({
            "status": "éxito", 
            "mensaje": "Activo y miniatura ensamblados correctamente."
        })
        
    except Exception as e:
        return jsonify({"status": "error", "mensaje": str(e)}), 500

if __name__ == '__main__':
    # Render exige que el servidor escuche en el puerto 10000
    app.run(host='0.0.0.0', port=10000)
