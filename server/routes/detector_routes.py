from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from datetime import datetime, timezone
import os
import base64
from utils.metadata_utils import load_metadata, save_metadata
from utils.openai_utils import generate_item_description

detector_bp = Blueprint("detector_bp", __name__)


def to_title_case(value: str):
    if not value:
        return value
    return " ".join(word.capitalize() for word in value.split())


@detector_bp.route("/detector/detect", methods=["POST", "OPTIONS"])
def detect_image():
    """Process an image and generate item description"""
    if request.method == "OPTIONS":
        response = jsonify({})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        return response, 200

    def build_response(payload, status=200):
        resp = jsonify(payload)
        resp.headers.add("Access-Control-Allow-Origin", "*")
        resp.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        resp.headers.add("Access-Control-Allow-Headers", "Content-Type")
        return resp, status

    description_warning = None

    try:
        if "image" not in request.files and "imageData" not in request.form:
            return build_response({"error": "No image provided"}, 400)
        
        # Handle base64 image data from webcam
        if "imageData" in request.form:
            image_data = request.form["imageData"]
            # Remove data URL prefix if present
            if "," in image_data:
                image_data = image_data.split(",")[1]
            
            # Decode base64 image
            image_bytes = base64.b64decode(image_data)
            
            # Save temporary image (use UTC to ensure consistency across timezones)
            ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            temp_filename = f"temp_capture_{ts}.jpg"
            temp_path = os.path.join(current_app.config["UPLOAD_FOLDER"], temp_filename)
            
            with open(temp_path, "wb") as f:
                f.write(image_bytes)
        else:
            # Handle file upload (use UTC to ensure consistency across timezones)
            file = request.files["image"]
            ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            temp_filename = secure_filename(f"temp_{ts}_{file.filename}")
            temp_path = os.path.join(current_app.config["UPLOAD_FOLDER"], temp_filename)
            file.save(temp_path)
        
        # Generate OpenAI description if available
        print(f"[INFO] Processing image: {temp_path}")
        item_description = None
        description_warning = None
        
        try:
            item_description = generate_item_description(temp_path)
            if item_description:
                print(f"[DEBUG] Item description received: {item_description}")
            else:
                description_warning = "AI description service returned no result. Item saved without description."
                print(f"[DEBUG] Item description is None (API may not be configured or failed)")
        except Exception as e:
            description_warning = "Unable to reach the AI description service. Item saved without automatic description."
            print(f"[WARNING] Could not generate description: {e}")
            import traceback
            traceback.print_exc()

        # Save the image with proper name
        category = item_description.get("category") if item_description else "item"
        filename = secure_filename(f"{category}_{ts}.jpg")
        file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        os.rename(temp_path, file_path)
        
        # Build metadata record
        image_url = f"http://{request.host}/uploads/{filename}"
        raw_label = item_description.get("label") if item_description else None
        formatted_label = to_title_case(raw_label) if raw_label else None
        record = {
            "timestamp": ts,
            "filename": filename,
            "image_url": image_url,
            "label": formatted_label,
            "category": category,
            "color": item_description.get("color") if item_description else None,
            "condition": item_description.get("condition") if item_description else None,
            "distinctive_features": item_description.get("distinctive_features") if item_description else None
        }
        
        print(f"[DEBUG] Final record: category={record['category']}, color={record['color']}, condition={record['condition']}")
        
        # Save metadata
        data = load_metadata()
        data.append(record)
        save_metadata(data)
        
        response_payload = {
            "success": True,
            "metadata": record
        }
        if description_warning:
            response_payload["warning"] = description_warning

        return build_response(response_payload, 200)
        
    except Exception as e:
        print(f"[ERROR] Detection endpoint failed: {e}")
        return build_response({"error": str(e)}, 500)

