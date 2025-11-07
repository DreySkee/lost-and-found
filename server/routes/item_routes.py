from flask import Blueprint, request, jsonify, current_app
import os
from utils.metadata_utils import load_metadata, save_metadata

item_bp = Blueprint("item_bp", __name__)


@item_bp.route("/api/item")
def get_metadata():
    """Serve metadata.json"""
    try:
        metadata = load_metadata()
        response = jsonify(metadata)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@item_bp.route("/api/item/<path:filename>", methods=["DELETE", "OPTIONS"])
def delete_item(filename):
    """Delete an item from metadata and remove the image file"""
    if request.method == "OPTIONS":
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response, 200
    
    try:
        # Load metadata
        metadata = load_metadata()
        
        # Find and remove the item
        item_found = False
        updated_metadata = []
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        
        for item in metadata:
            if item.get('filename') == filename:
                item_found = True
                # Delete the image file
                image_path = os.path.join(upload_folder, filename)
                if os.path.exists(image_path):
                    try:
                        os.remove(image_path)
                        print(f"[INFO] Deleted image file: {image_path}")
                    except Exception as e:
                        print(f"[WARNING] Could not delete image file: {e}")
            else:
                updated_metadata.append(item)
        
        if not item_found:
            response = jsonify({"error": "Item not found"})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 404
        
        # Save updated metadata
        save_metadata(updated_metadata)
        
        response = jsonify({"success": True, "message": "Item deleted successfully"})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 200
        
    except Exception as e:
        print(f"[ERROR] Delete endpoint failed: {e}")
        import traceback
        traceback.print_exc()
        response = jsonify({"error": str(e)})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

