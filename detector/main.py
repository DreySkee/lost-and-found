from ultralytics import YOLO
import cv2
import time
import requests
import os
import numpy as np

# Configuration
TARGET_CLASSES = {"bottle", "book", "teddy bear", "backpack", "cell phone"}
SERVER_URL = "http://127.0.0.1:8080/upload"

def main():
    """Entry point for the detector script"""
    # Load model
    model = YOLO("yolov8n.pt")
    # model = YOLO("yolov8n-oiv7.pt")

    # Init webcam
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise RuntimeError("Could not access webcam")

    # Tracking state
    last_detect_time = {}
    stable_counter = {}
    last_boxes = {}

    STABLE_FRAMES = 5       # must see object 5 frames in a row
    COOLDOWN_SEC = 3        # per object type
    MOTION_THR = 20         # pixels difference tolerance

    captured = False  # flag to stop after first pic save

    print("[INFO] Starting detection... press ESC to exit.")

    while True:
        ret, frame = cap.read()
        
        if not ret:
            break

        # Get class indices for bottle, book, teddy bear
        target_ids = [i for i, name in model.names.items() if name in TARGET_CLASSES if name in TARGET_CLASSES]
        results = model(frame, classes=target_ids, verbose=False)
        # results = model(frame)

        # results = model(frame, verbose=False)
        annotated = results[0].plot()
        cv2.imshow("Lost & Found AI", annotated)

        current_time = time.time()
        detections = results[0].boxes

        for box in detections:
            cls = int(box.cls[0])
            label = model.names[cls]
            conf = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            if label not in TARGET_CLASSES or conf < 0.5:
                continue

            # Skip if still on cooldown
            if label in last_detect_time and current_time - last_detect_time[label] < COOLDOWN_SEC:
                continue

            # Compare with previous bounding box (check stability)
            new_box = np.array([x1, y1, x2, y2])
            if label in last_boxes:
                diff = np.abs(last_boxes[label] - new_box).mean()
                if diff < MOTION_THR:
                    stable_counter[label] = stable_counter.get(label, 0) + 1
                else:
                    stable_counter[label] = 0
            else:
                stable_counter[label] = 0

            last_boxes[label] = new_box

            # Only save if object was stable for enough frames
            if stable_counter[label] >= STABLE_FRAMES:
                crop = frame[y1:y2, x1:x2]
                ts = int(current_time)
                # filename = f"{label}_{ts}.jpg"
                filename = f"capture_{label}_{ts}.jpg"
                # filepath = os.path.join(CAPTURE_DIR, filename)
                cv2.imwrite(filename, crop)
                print(f"[CAPTURED] {label} stable crop saved {filename}")

                with open(filename, "rb") as f:
                    requests.post(SERVER_URL, files={"file": f},
                                  data={"label": label, "confidence": conf})

                last_detect_time[label] = current_time
                stable_counter[label] = 0  # reset

                # Cleanup: delete original capture
                os.remove(filename)
                print(f"[CLEANED] {filename}")
                
                captured = True
                break 

        if captured or cv2.waitKey(1) == 27:  # ESC to quit
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
