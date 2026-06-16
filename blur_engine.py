import cv2
import numpy as np

def blur_sensitive_content(image, bboxes, blur_strength=0.3):
    """
    Surgically blurs detected boxes and captures original pixels for restoration.
    """
    if image is None or not bboxes:
        return image, []

    output = image.copy()
    h, w = image.shape[:2]
    restoration_key = [] # List to store the 'Lock & Key' data

    for bbox in bboxes:
        # 1. Coordinate Extraction
        x1, y1, x2, y2 = map(int, bbox)
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)

        if x2 <= x1 or y2 <= y1:
            continue

        # 2. Extract ROI & SAVE ORIGINAL PIXELS
        roi = output[y1:y2, x1:x2]
        original_pixels = roi.copy()
        restoration_key.append({
            'bbox': (x1, y1, x2, y2),
            'pixels': original_pixels
        })

        # 3. Calculate Thickness (Kernel Size)
        roi_h, roi_w = roi.shape[:2]
        ksize = int(max(roi_h, roi_w) * blur_strength)
        if ksize % 2 == 0: ksize += 1
        ksize = max(3, ksize)

        # 4. Apply Blur
        blurred_roi = cv2.medianBlur(roi, ksize)
        output[y1:y2, x1:x2] = blurred_roi

    return output, restoration_key