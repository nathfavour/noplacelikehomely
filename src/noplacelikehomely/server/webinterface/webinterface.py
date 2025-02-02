import os
from flask import Blueprint, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename
from noplacelikehomely.config import load_config  # New import

api_bp = Blueprint("api", __name__, url_prefix="/api")

# Global in-memory clipboard storage
CLIPBOARD = ""

# Load config and set upload folder from config (expanding '~')
config = load_config()
UPLOAD_FOLDER = os.path.expanduser(config.get("upload_folder", "~/noplacelike/uploads"))
# Optionally, similar logic could be applied for a downloads folder if needed.
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@api_bp.route("/clipboard", methods=["GET", "POST"])
def clipboard():
    global CLIPBOARD
    if request.method == "POST":
        data = request.get_json()
        text = data.get("text", "")
        CLIPBOARD = text
        try:
            import pyperclip
            pyperclip.copy(text)  # Mirror shared clipboard to server system clipboard
        except ImportError:
            # pyperclip not installed; skipping system clipboard update
            pass
        return jsonify({"status": "success"}), 200
    return jsonify({"text": CLIPBOARD})

@api_bp.route("/files", methods=["GET", "POST"])
def files():
    if request.method == "POST":
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "Empty filename"}), 400
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        return jsonify({"status": "success", "filename": filename}), 200

    # List files in the upload folder
    try:
        files_list = os.listdir(UPLOAD_FOLDER)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"files": files_list})

@api_bp.route("/files/<filename>", methods=["GET"])
def download_file(filename):
    filename = secure_filename(filename)
    try:
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
    except Exception:
        return jsonify({"error": "File not found"}), 404
