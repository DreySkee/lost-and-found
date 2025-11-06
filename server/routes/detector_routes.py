from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import base64
import types
from utils.detector_utils import detect_objects
from utils.metadata_utils import load_metadata, save_metadata
from utils.openai_utils import generate_item_description

detector_bp = Blueprint("detector_bp", __name__)




@detector_bp.route("/detector/detect-realtime", methods=["POST"])
def detect_realtime():
    """Real-time detection endpoint that doesn't save images"""
    try:
        if "imageData" not in request.form:
            return jsonify({"error": "No image data provided"}), 400
        
        image_data = request.form["imageData"]
        # Remove data URL prefix if present
        if "," in image_data:
            image_data = image_data.split(",")[1]
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        
        # Save temporary image for detection (will be cleaned up)
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg', dir=current_app.config["UPLOAD_FOLDER"]) as tmp:
            tmp.write(image_bytes)
            temp_path = tmp.name
        
        try:
            # Detect objects
            detections = detect_objects(temp_path)
            
            return jsonify({
                "success": True,
                "detections": detections
            }), 200
        finally:
            # Clean up temp file
            try:
                os.remove(temp_path)
            except:
                pass
        
    except Exception as e:
        print(f"[ERROR] Real-time detection failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@detector_bp.route("/detector/detect", methods=["POST"])
def detect_image():
    """Process an image with YOLO detector"""
    try:
        if "image" not in request.files and "imageData" not in request.form:
            return jsonify({"error": "No image provided"}), 400
        
        # Handle base64 image data from webcam
        if "imageData" in request.form:
            image_data = request.form["imageData"]
            # Remove data URL prefix if present
            if "," in image_data:
                image_data = image_data.split(",")[1]
            
            # Decode base64 image
            image_bytes = base64.b64decode(image_data)
            
            # Save temporary image
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_filename = f"temp_capture_{ts}.jpg"
            temp_path = os.path.join(current_app.config["UPLOAD_FOLDER"], temp_filename)
            
            with open(temp_path, "wb") as f:
                f.write(image_bytes)
        else:
            # Handle file upload
            file = request.files["image"]
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_filename = secure_filename(f"temp_{ts}_{file.filename}")
            temp_path = os.path.join(current_app.config["UPLOAD_FOLDER"], temp_filename)
            file.save(temp_path)
        
        # Detect objects
        print(f"[INFO] Processing image: {temp_path}")
        detections = detect_objects(temp_path)
        print(f"[INFO] Detections returned: {len(detections)} items")
        
        
        # Get best detection
        if detections:
            best_detection = max(detections, key=lambda x: x["confidence"])
        else:
            best_detection = {}
            best_detection["label"] = None
            best_detection["confidence"] = 0
            best_detection["bbox"] = None
        
        # Save the image with proper name
        label =  best_detection["label"]
        filename = secure_filename(f"{label}_{ts}.jpg")
        file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        os.rename(temp_path, file_path)
        
        # Generate OpenAI description if available
        description = None
        try:
            description = generate_item_description(file_path)
        except Exception as e:
            print(f"[WARNING] Could not generate description: {e}")
        
        # Build metadata record
        image_url = f"http://{request.host}/uploads/{filename}"
        record = {
            "timestamp": ts,
            "filename": filename,
            "image_url": image_url,
            "label": label,
            "confidence": str(best_detection["confidence"]),
            "description": description
        }
        
        # Save metadata
        data = load_metadata()
        data.append(record)
        save_metadata(data)
        
        return jsonify({
            "success": True,
            "detections": detections,
            "primary": {
                "label": label,
                "confidence": best_detection["confidence"],
                "bbox": best_detection["bbox"]
            },
            "metadata": record
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Detection endpoint failed: {e}")
        return jsonify({"error": str(e)}), 500

