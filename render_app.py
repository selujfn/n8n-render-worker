import os
import requests
import json
from flask import Flask, request, jsonify

# Assurez-vous que ces librairies sont bien installées via requirements.txt
from yt_dlp import YoutubeDL 
from moviepy.editor import * app = Flask(__name__)

# --- Récupération du Webhook N8N ---
# Cette variable sera définie dans l'environnement de Render.com
N8N_RENDER_SUCCESS_WEBHOOK = os.environ.get('N8N_RENDER_SUCCESS_WEBHOOK')

# ======================================================================
# ROUTE : RENDU (Endpoint appelé par n8n)
# ======================================================================

@app.route('/render', methods=['POST'])
def handle_render_command():
    try:
        data = request.get_json()
        
        # Données reçues du nœud Format Output for Render.com
        original_url = data.get('original_url')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        suggested_title = data.get('suggested_title')
        
        if not all([original_url, start_time, end_time]):
             return jsonify({"error": "Missing required data for rendering."}), 
             
        # --- LOGIQUE DE RENDU : À COMPLÉTER ICI ---
        
        # 1. Téléchargement de la vidéo (yt-dlp)
        # 2. Rognage/Montage du clip (moviepy)
        # 3. Téléversement du fichier final vers un stockage cloud (S3, Drive, etc.)
        
        # Le nom du fichier sera le titre suggéré
        output_filename = f"{suggested_title.replace(' ', '_').replace('.', '')}.mp4"
        
        # --- EXEMPLE SIMPLIFIÉ DE TÉLÉCHARGEMENT ET COUPE ---
        
        # 1. Téléchargement (yt-dlp)
        temp_video_path = "input_temp.mp4"
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': temp_video_path,
            'merge_output_format': 'mp4',
            'quiet': True,
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([original_url])

        # 2. Couper le clip (MoviePy)
        clip = VideoFileClip(temp_video_path)
        final_clip = clip.subclip(start_time, end_time)
        
        # 3. Écriture du fichier final
        final_clip.write_videofile(
            output_filename, 
            codec='libx264', 
            audio_codec='aac', 
            temp_audiofile='temp-audio.m4a', 
            remove_temp=True
        )

        # 4. Nettoyage et Téléversement (SIMULÉ)
        # os.remove(temp_video_path)
        # os.remove(output_filename) # Supprimer après téléversement réussi
        
        # REMPLACEZ CECI PAR L'URL DE VOTRE FICHIER TÉLÉVERSÉ
        video_file_url = "https://votre-stockage.com/" + output_filename
        
        # --------------------------------------------------------
        
        # 5. Envoi de la notification de succès à n8n
        if N8N_RENDER_SUCCESS_WEBHOOK:
            success_payload = {
                "success": True,
                "video_file_url": video_file_url, 
                "title": suggested_title
            }
            requests.post(N8N_RENDER_SUCCESS_WEBHOOK, json=success_payload, timeout=10)
            
            return jsonify({"status": "Rendering complete and notification sent to n8n."}), 200
        else:
            return jsonify({"error": "N8N Webhook is not configured on Render.com"}), 500

    except Exception as e:
        print(f"Render Error: {str(e)}")
        return jsonify({"error": f"An error occurred during rendering: {str(e)}"}), 500

if __name__ == '__main__':
    # Le port est défini par Render.com via l'environnement
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
