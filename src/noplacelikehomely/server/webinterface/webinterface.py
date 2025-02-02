import os
from flask import Blueprint, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename

api_bp = Blueprint("api", __name__, url_prefix="/api")

# Global in-memory clipboard storage
CLIPBOARD = ""

# Configure file upload folder (ensure this folder exists in your project root)
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@api_bp.route("/clipboard", methods=["GET", "POST"])
def clipboard():
    global CLIPBOARD
    if request.method == "POST":
        data = request.get_json()
        CLIPBOARD = data.get("text", "")
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
