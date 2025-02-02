from flask import Blueprint, request, Response, jsonify, stream_with_context
import os
from noplacelikehomely.config import load_config

stream_bp = Blueprint("stream", __name__, url_prefix="/stream")

def generate_audio(file_path, chunk_size=4096):
    with open(file_path, "rb") as audio:
        while True:
            data = audio.read(chunk_size)
            if not data:
                break
            yield data

@stream_bp.route("/play")
def stream_audio():
    file_name = request.args.get("file")
    if not file_name:
        return jsonify({"error": "Missing file parameter"}), 400
    config = load_config()
    # Get multiple audio directories from config; fallback to a default folder.
    audio_folders = config.get("audio_folders", [])
    if not audio_folders:
        audio_folders = ["~/noplacelike/audio"]
    # Expand user directories and search for file
    for folder in audio_folders:
        folder = os.path.expanduser(folder)
        file_path = os.path.join(folder, file_name)
        if os.path.exists(file_path):
            # Optionally determine mimetype based on extension
            return Response(stream_with_context(generate_audio(file_path)), mimetype="audio/mpeg")
    return jsonify({"error": "File not found"}), 404

@stream_bp.route("/list")
def list_audio():
    config = load_config()
    audio_folders = config.get("audio_folders", [])
    if not audio_folders:
        audio_folders = ["~/noplacelike/audio"]
    aggregated = {}
    for folder in audio_folders:
        folder = os.path.expanduser(folder)
        try:
            files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        except Exception:
            files = []
        aggregated[folder] = files
    return jsonify({"files": aggregated})
