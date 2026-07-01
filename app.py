import os
import requests
from flask import Flask, request, jsonify
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip
import cloudinary
import cloudinary.uploader

app = Flask(__name__)

# 🛠️ CONFIGURACIÓN DE CLOUDINARY: Pon tus datos entre las comillas
cloudinary.config( 
  cloud_name = "TU_CLOUD_NAME", 
  api_key = "TU_API_KEY", 
  api_secret = "TU_API_SECRET",
  secure = True
)

@app.route('/fabricar', methods=['POST'])
def fabricar_activo():
    try:
        # 1. Desempaquetar los textos
        titulo = request.form.get('titulo', 'EL SECRETO ESTOICO')
        imagen_url = request.form.get('imagen_url')
        
        # 2. Desempaquetar y guardar el archivo de audio
        if 'audio' not in request.files:
            return jsonify({"status": "error", "mensaje": "Falta el archivo de audio"}), 400
        
        archivo_audio = request.files['audio']
        ruta_audio = "audio_recibido.mp3"
        archivo_audio.save(ruta_audio)

        # 3. Descargar la imagen de Leonardo AI
        ruta_imagen = "imagen_base.jpg"
        if imagen_url:
            respuesta_img = requests.get(imagen_url)
            with open(ruta_imagen, 'wb') as f:
                f.write(respuesta_img.content)
        else:
            return jsonify({"status": "error", "mensaje": "Falta la URL de la imagen"}), 400

        # 4. Fabricar la Miniatura (Estampado)
        ruta_fuente = "Anton-Regular.ttf"
        ruta_miniatura = "miniatura_final.jpg"
        
        if os.path.exists(ruta_fuente) and os.path.exists(ruta_imagen):
            imagen = Image.open(ruta_imagen)
            dibujo = ImageDraw.Draw(imagen)
            
            ancho_img, alto_img = imagen.size
            tamano_fuente = int(ancho_img * 0.111)
            fuente = ImageFont.truetype(ruta_fuente, tamano_fuente)
            
            pos_x = ancho_img * 0.039
            pos_y = alto_img * 0.3668
            
            dibujo.text((pos_x+5, pos_y+5), titulo, font=fuente, fill="black")
            dibujo.text((pos_x, pos_y), titulo, font=fuente, fill="#fff9f8")
            
            imagen.save(ruta_miniatura)

        # 5. Fabricar el Video (Optimizado a 1 FPS para cuidar la RAM)
        ruta_video = "video_final.mp4"
        audio_clip = AudioFileClip(ruta_audio)
        image_clip = ImageClip(ruta_imagen).set_duration(audio_clip.duration)
        
        video = image_clip.set_audio(audio_clip)
        video.write_videofile(ruta_video, fps=1, codec="libx264", audio_codec="aac")
        
        # Cierre preventivo de archivos para liberar memoria RAM inmediatamente
        audio_clip.close()
        image_clip.close()

        # 6. Subida Automática a tu Almacén de Cloudinary
        url_miniatura_publica = ""
        url_video_publica = ""
        
        if os.path.exists(ruta_miniatura):
            upload_img = cloudinary.uploader.upload(ruta_miniatura, resource_type="image")
            url_miniatura_publica = upload_img.get("secure_url", "")
            
        if os.path.exists(ruta_video):
            upload_vid = cloudinary.uploader.upload(ruta_video, resource_type="video")
            url_video_publica = upload_vid.get("secure_url", "")

        # 7. Respuesta de éxito con los enlaces listos para Make
        return jsonify({
            "status": "éxito",
            "mensaje": "Video y miniatura fabricados y almacenados con éxito.",
            "url_video": url_video_publica,
            "url_miniatura": url_miniatura_publica
        })
        
    except Exception as e:
        return jsonify({"status": "error", "mensaje": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
