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

    @app.route("/search")
    def serve_search():
        """Serve search.html"""
        static_dir = os.path.join(BASE_DIR, "..", "client", "static")
        search_file = os.path.join(static_dir, "search.html")
        if os.path.exists(search_file):
            return send_from_directory(static_dir, "search.html")
        return {"error": "Search page not found"}, 404

    @app.route("/search.css")
    def serve_search_css():
        """Serve search.css"""
        static_dir = os.path.join(BASE_DIR, "..", "client", "static")
        css_file = os.path.join(static_dir, "search.css")
        if os.path.exists(css_file):
            return send_from_directory(static_dir, "search.css")
        return {"error": "CSS file not found"}, 404

    @app.route("/")
    def home():
        # Serve React app index.html
        static_dir = os.path.join(BASE_DIR, "static")
        if os.path.exists(static_dir):
            return send_from_directory(static_dir, "index.html")
        return {"status": "ok", "message": "Lost & Found AI backend running - React app not built yet. Run: cd client && npm install && npm run build"}
    
    # Catch-all route for React Router (must be last, after all API routes)
    @app.route("/<path:path>")
    def serve_react_app(path):
        # Skip API routes and static assets
        if any(path.startswith(prefix) for prefix in ["api/", "detector/", "upload", "metadata", "uploads/"]):
            return {"error": "Not found"}, 404
        
        static_dir = os.path.join(BASE_DIR, "static")
        # If requesting a static file (JS, CSS, etc.), serve it
        static_file_path = os.path.join(static_dir, path)
        if os.path.exists(static_file_path) and os.path.isfile(static_file_path):
            return send_from_directory(static_dir, path)
        # Otherwise, serve index.html for client-side routing
        if os.path.exists(static_dir):
            return send_from_directory(static_dir, "index.html")
        return {"error": "Not found"}, 404

    return app


def main():
    """Entry point for the start script"""
    app = create_app()
    app.run(host="0.0.0.0", port=8080, debug=True)


if __name__ == "__main__":
    main()

