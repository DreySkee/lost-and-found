from flask import Flask
import os
import sys

# Ensure the server directory is in the path for imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from routes.upload import upload_bp
from routes.image_routes import image_bp

def create_app():
    app = Flask(__name__)

    # Base directory & folders
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

    # Register blueprints
    app.register_blueprint(upload_bp)
    app.register_blueprint(image_bp)

    @app.route("/")
    def home():
        return {"status": "ok", "message": "Lost & Found AI backend running"}

    return app


def main():
    """Entry point for the start script"""
    app = create_app()
    app.run(host="0.0.0.0", port=8080, debug=True)


if __name__ == "__main__":
    main()

