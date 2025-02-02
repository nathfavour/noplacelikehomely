import os
from flask import Blueprint, Response, request, render_template_string, send_file, current_app, jsonify, stream_with_context
from noplacelikehomely.config import load_config

stream_bp = Blueprint("stream", __name__, url_prefix="/stream")

# Load configured audio folder
config = load_config()
AUDIO_FOLDER = os.path.expanduser(config.get("audio_folder", "~/noplacelike/audio"))
os.makedirs(AUDIO_FOLDER, exist_ok=True)

def generate_audio(file_path, chunk_size=4096):
    with open(file_path, "rb") as audio:
        while True:
            data = audio.read(chunk_size)
            if not data:
                break
            yield data

@stream_bp.route("/control")
def control_page():
    # List available audio files in the AUDIO_FOLDER
    try:
        files = [f for f in os.listdir(AUDIO_FOLDER) if os.path.isfile(os.path.join(AUDIO_FOLDER, f))]
    except Exception as e:
        files = []
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Audio Streaming Control</title>
            <meta charset="UTF-8">
            <style>
                /* Basic styles */
                body { font-family: sans-serif; padding: 1rem; }
                .file-list { margin: 1rem 0; }
                .file-item { margin: 0.5rem 0; }
                .button { padding: 0.5rem 1rem; background: #4444ff; color: white; border: none; cursor: pointer; }
            </style>
        </head>
        <body>
            <h1>Audio Streaming Control</h1>
            <div class="file-list">
                {% if files %}
                    <ul>
                    {% for file in files %}
                        <li class="file-item">
                            {{ file }} 
                            <button onclick="startStream('{{ file }}')" class="button">Stream</button>
                        </li>
                    {% endfor %}
                    </ul>
                {% else %}
                    <p>No audio files found in the configured folder.</p>
                {% endif %}
            </div>
            <audio id="audioPlayer" controls style="width:100%;"></audio>
            <script>
                function startStream(fileName) {
                    const audio = document.getElementById('audioPlayer');
                    // Set the source to the streaming endpoint with the selected file
                    audio.src = '/stream/play?file=' + encodeURIComponent(fileName);
                    audio.play();
                }
            </script>
        </body>
        </html>
    ''', files=files)

@stream_bp.route("/play")
def stream_audio():
    # Expect query parameter 'file'
    file_name = request.args.get("file")
    if not file_name:
        return jsonify({"error": "Missing file parameter"}), 400
    file_path = os.path.join(AUDIO_FOLDER, file_name)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    # Optionally, set mime_type based on file extension; default to audio/mpeg
    mime_type = "audio/mpeg" if file_name.lower().endswith(".mp3") else "application/octet-stream"
    return Response(stream_with_context(generate_audio(file_path)),
                    mimetype=mime_type)

@stream_bp.route("/list")
def list_audio():
    try:
        files = [f for f in os.listdir(AUDIO_FOLDER) if os.path.isfile(os.path.join(AUDIO_FOLDER, f))]
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"files": files})
