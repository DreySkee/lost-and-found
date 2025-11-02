from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from utils.metadata_utils import load_metadata, save_metadata


upload_bp = Blueprint("upload_bp", __name__)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_bp.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "no file uploaded"}), 400

    file = request.files["file"]
    label = request.form.get("label", "unknown")
    conf = request.form.get("confidence", "N/A")

    if file.filename == "":
        return jsonify({"error": "empty filename"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "invalid file type"}), 400

    # Save file
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = secure_filename(f"{label}_{ts}.jpg")
    file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    # Build metadata record
    image_url = f"http://{request.host}/uploads/{filename}"
    record = {
        "timestamp": ts,
        "filename": filename,
        "image_url": image_url,
        "label": label,
        "confidence": conf
    }

    # Save metadata
    data = load_metadata()
    data.append(record)
    save_metadata(data)

    print(f"[UPLOAD] {filename} ({label}, conf={conf}) saved with metadata")

    return jsonify({
        "message": "file uploaded successfully",
        "metadata": record
    }), 200


@upload_bp.route("/metadata", methods=["GET"])
def get_metadata():
    data = load_metadata()
    return jsonify(data), 200
