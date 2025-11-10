from flask import Flask, send_from_directory, jsonify, request
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Ensure the server directory is in the path for imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from routes.image_routes import image_bp
from routes.detector_routes import detector_bp
from routes.item_routes import item_bp

def create_app():
    app = Flask(__name__, static_folder="static", static_url_path="/static")

    # Base directory & folders
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

    # Register blueprints
    app.register_blueprint(image_bp)
    app.register_blueprint(detector_bp)
    app.register_blueprint(item_bp)

    @app.route("/api/health")
    def health():
        return {"status": "ok", "message": "Lost & Found AI backend running"}

    client_root = os.path.join(BASE_DIR, "..", "client")

    @app.route("/search")
    def serve_search():
        """Serve search.html"""
        search_file = os.path.join(client_root, "search.html")
        if os.path.exists(search_file):
            return send_from_directory(client_root, "search.html")
        return {"error": "Search page not found"}, 404

    @app.route("/search.css")
    def serve_search_css():
        """Serve search.css"""
        css_file = os.path.join(client_root, "search.css")
        if os.path.exists(css_file):
            return send_from_directory(client_root, "search.css")
        return {"error": "CSS file not found"}, 404

    @app.route("/camera")
    def serve_camera():
        """Serve camera.html"""
        camera_file = os.path.join(client_root, "camera.html")
        if os.path.exists(camera_file):
            return send_from_directory(client_root, "camera.html")
        return {"error": "Camera page not found"}, 404

    @app.route("/camera.css")
    def serve_camera_css():
        """Serve camera.css"""
        css_file = os.path.join(client_root, "camera.css")
        if os.path.exists(css_file):
            return send_from_directory(client_root, "camera.css")
        return {"error": "CSS file not found"}, 404

    @app.route("/shared.css")
    def serve_shared_css():
        """Serve shared.css"""
        css_file = os.path.join(client_root, "shared.css")
        if os.path.exists(css_file):
            return send_from_directory(client_root, "shared.css")
        return {"error": "CSS file not found"}, 404

    @app.route("/utils.js")
    def serve_utils_js():
        """Serve utils.js"""
        js_file = os.path.join(client_root, "utils.js")
        if os.path.exists(js_file):
            return send_from_directory(client_root, "utils.js", mimetype="application/javascript")
        return {"error": "JS file not found"}, 404

    @app.route("/")
    def home():
        return serve_search()
    
    # Catch-all route for static files (must be last, after all API routes)
    @app.route("/<path:path>")
    def serve_static_files(path):
        # Skip API routes and static assets
        if any(path.startswith(prefix) for prefix in ["api/", "detector/", "upload", "metadata", "uploads/"]):
            return {"error": "Not found"}, 404

        requested_file = os.path.join(client_root, path)
        if os.path.exists(requested_file) and os.path.isfile(requested_file):
            rel_dir, filename = os.path.split(requested_file)
            return send_from_directory(rel_dir, filename)

        return {"error": "Not found"}, 404

    return app


def main():
    """Entry point for the start script"""
    app = create_app()
    # Use PORT environment variable if available (for production), otherwise default to 8080
    port = int(os.getenv("PORT", 8080))
    # Only enable debug mode if explicitly set via environment variable
    debug = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)


if __name__ == "__main__":
    main()

