import os
import sys
import numpy as np
from typing import List, Dict, Any, Tuple
from ultralytics import YOLO
import cv2

# Add project root to path to access model files
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(PROJECT_ROOT, "yolov8n.pt")

# Configuration
TARGET_CLASSES = {"bottle", "book", "teddy bear", "backpack", "bag", "cell phone"}
CONFIDENCE_THRESHOLD = 0.01

# Global model instance (lazy loaded)
_model = None


def get_model():
    """Get or load YOLO model (singleton pattern)"""
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
        _model = YOLO(MODEL_PATH)
    return _model


def detect_objects(image_path: str) -> List[Dict[str, Any]]:
    """
    Detect objects in an image using YOLO
    
    Args:
        image_path: Path to the image file
        
    Returns:
        List of detected objects with label, confidence, and bounding box
    """
    try:
        if not os.path.exists(image_path):
            print(f"[ERROR] Image file not found: {image_path}")
            return []
        
        model = get_model()
        
        # Run inference
        results = model(image_path, verbose=False)

        # if not results or len(results) == 0:
        #     return []
        
        detections = []
        all_detections = []  # For debugging
        
        for result in results:
            if result.boxes is None or len(result.boxes) == 0:
                continue
                
            boxes = result.boxes
            for box in boxes:
                try:
                    # Handle tensor conversion - try .item() if it's a tensor, otherwise use direct access
                    cls_val = box.cls[0]
                    conf_val = box.conf[0]
                    
                    cls = int(cls_val.item() if hasattr(cls_val, 'item') else cls_val)
                    label = model.names[cls]
                    conf = float(conf_val.item() if hasattr(conf_val, 'item') else conf_val)
                    
                    # Store all detections for debugging
                    all_detections.append({"label": label, "confidence": conf})
                    
                    # Filter by target classes and confidence
                    if label in TARGET_CLASSES and conf >= CONFIDENCE_THRESHOLD:
                        xyxy = box.xyxy[0]
                        # Handle tensor conversion for bbox coordinates
                        if hasattr(xyxy[0], 'item'):
                            x1, y1, x2, y2 = [int(xyxy[i].item()) for i in range(4)]
                        else:
                            x1, y1, x2, y2 = map(int, xyxy[:4])
                            
                        detections.append({
                            "label": label,
                            "confidence": conf,
                            "bbox": [x1, y1, x2, y2]
                        })
                except Exception as e:
                    print(f"[WARNING] Error processing box: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
        
        if detections:
            print(f"[INFO] Found {len(detections)} target objects: {[d['label'] for d in detections]}")
        else:
            print(f"[INFO] No target objects found. All detections: {all_detections[:5]}")  # Show first 5
        
        return detections
    except Exception as e:
        import traceback
        print(f"[ERROR] Detection failed: {e}")
        print(traceback.format_exc())
        return []

