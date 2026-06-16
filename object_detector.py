from ultralytics import YOLO
import os
import torch
import logging

# Silence ultralytics logging to keep the console clean
logging.getLogger("ultralytics").setLevel(logging.ERROR)

# Path to your custom trained model
MODEL_PATH = r"C:\pythonprojects\runs\detect\pii_final_model\weights\best.pt"
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# Load custom model with a fallback
if os.path.exists(MODEL_PATH):
    model = YOLO(MODEL_PATH).to(device)
else:
    print(f"⚠️ Warning: Custom model not found at {MODEL_PATH}. Falling back to nano.")
    model = YOLO("yolov8n.pt").to(device)


def detect_pii(image_source):
    """
    Detects specific card components (chip, numbers, etc.)
    and returns exact coordinates for surgical blurring.
    """
    results = model.predict(
        source=image_source,
        conf=0.20,  # Balanced confidence to avoid false positives on random text
        iou=0.45,
        imgsz=640,
        device=device,
        verbose=False
    )[0]

    detected_items = []

    # These are the labels your model likely uses for Credit Cards
    # We mark them as sensitive so the system knows to blur them.
    for box in results.boxes:
        class_id = int(box.cls[0])
        label = model.names[class_id].lower()
        coords = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
        conf_score = round(float(box.conf[0]), 2)

        detected_items.append({
            "label": label,
            "confidence": conf_score,
            "bbox": [int(c) for c in coords],
            # If it's a card number, chip, or expiry, it gets flagged for the blur engine
            "is_sensitive": True
        })

    return detected_items


# Quick print to confirm device usage on startup
print(f"🚀 YOLO Detector initialized on: {device.upper()}")