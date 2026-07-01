import os
import requests
from flask import Flask, request, jsonify
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip

app = Flask(__name__)

@app.route('/fabricar', methods=['POST'])
def fabricar_activo():
    try:
        # 1. Desempaquetar los textos (Form data)
        titulo = request.form.get('titulo', 'EL SECRETO ESTOICO')
        imagen_url = request.form.get('imagen_url')
        
        # 2. Desempaquetar y guardar el archivo de audio
        if 'audio' not in request.files:
            return jsonify({"status": "error", "mensaje": "Falta el archivo de audio"}), 400
        
        archivo_audio = request.files['audio']
        ruta_audio = "audio_recibido.mp3"
        archivo_audio.save(ruta_audio)

        # 3. Descargar la imagen generada por Leonardo AI
        ruta_imagen = "imagen_base.jpg"
        if imagen_url:
            respuesta_img = requests.get(imagen_url)
            with open(ruta_imagen, 'wb') as f:
                f.write(respuesta_img.content)
        else:
            return jsonify({"status": "error", "mensaje": "Falta la URL de la imagen"}), 400

        # 4. Fabricar la Miniatura (Estampado del Título)
        ruta_fuente = "Anton-Regular.ttf"
        ruta_miniatura = "miniatura_final.jpg"
        
        if os.path.exists(ruta_fuente) and os.path.exists(ruta_imagen):
            imagen = Image.open(ruta_imagen)
            dibujo = ImageDraw.Draw(imagen)
            
            ancho_img, alto_img = imagen.size
            tamano_fuente = int(ancho_img * 0.111)
            fuente = ImageFont.truetype(ruta_fuente, tamano_fuente)
            
            # Posición 3.9% X y 36.68% Y
            pos_x = ancho_img * 0.039
            pos_y = alto_img * 0.3668
            
            # Sombra y Texto Principal
            dibujo.text((pos_x+5, pos_y+5), titulo, font=fuente, fill="black")
            dibujo.text((pos_x, pos_y), titulo, font=fuente, fill="#fff9f8")
            
            imagen.save(ruta_miniatura)

        # 5. Fabricar el Video (Unión de Audio e Imagen)
        ruta_video = "video_final.mp4"
        audio_clip = AudioFileClip(ruta_audio)
        image_clip = ImageClip(ruta_imagen).set_duration(audio_clip.duration)
        
        video = image_clip.set_audio(audio_clip)
        # Renderizamos a 1 fps para optimizar la memoria del servidor gratuito
        video.write_videofile(ruta_video, fps=1, codec="libx264", audio_codec="aac")
        
        # Limpieza de memoria
        audio_clip.close()
        image_clip.close()

        return jsonify({
            "status": "éxito", 
            "mensaje": "Activo digital y miniatura creados exitosamente en el servidor."
        })
        
    except Exception as e:
        return jsonify({"status": "error", "mensaje": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
