from flask import Blueprint, send_from_directory, current_app

image_bp = Blueprint("image_bp", __name__)


@image_bp.route("/uploads/<path:filename>")
def uploaded_file(filename):
    """Serve uploaded images"""
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)

