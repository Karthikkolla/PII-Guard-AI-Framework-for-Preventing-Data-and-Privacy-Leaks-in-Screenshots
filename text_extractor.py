import os
import cv2
import paddle
import numpy as np
from paddleocr import PaddleOCR

# Force CPU only
paddle.set_device('cpu')
os.environ['FLAGS_use_onednn'] = '0'
os.environ['FLAGS_mkl_num_threads'] = '1'

# Initialize OCR
ocr = PaddleOCR(
    use_angle_cls=True,
    lang="en",
    enable_mkldnn=False,
    use_gpu=False,
    show_log=False
)


def preprocess_for_ocr(image):
    """
    Advanced preprocessing to improve PaddleOCR character recognition.
    """
    # 1. Scaling: Increase size for small banking fonts (300 DPI equivalent)
    h, w = image.shape[:2]
    image = cv2.resize(image, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)

    # 2. Grayscale & CLAHE (Adaptive Contrast)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # 3. Noise Reduction & Binarization
    blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return thresh, 2.0  # Return processed image and the scale factor used


def extract_text_with_indices(image):
    try:
        # Pre-process image before OCR
        processed_img, scale_factor = preprocess_for_ocr(image)

        results = ocr.ocr(processed_img, cls=True)
        if not results or results[0] is None:
            return "", []

        full_text = ""
        ocr_items = []
        current_cursor = 0

        for line in results[0]:
            text = line[1][0]
            points = line[0]

            # Adjust BBOX back to original image scale
            x_coords = [p[0] / scale_factor for p in points]
            y_coords = [p[1] / scale_factor for p in points]
            bbox = [min(x_coords), min(y_coords), max(x_coords), max(y_coords)]

            start_idx = current_cursor
            end_idx = start_idx + len(text)

            ocr_items.append({
                "text": text,
                "bbox": bbox,
                "char_start": start_idx,
                "char_end": end_idx
            })

            full_text += text + " "
            current_cursor = end_idx + 1

        return full_text.strip(), ocr_items

    except Exception as e:
        print(f"OCR Engine Error: {e}")
        return "", []


def get_pii_boxes_advanced(ocr_items, pii_results):
    blur_data = []
    for pii in pii_results:
        for item in ocr_items:
            # Check overlap between NLP PII results and OCR character range
            if (item["char_start"] < pii.end and item["char_end"] > pii.start):
                blur_data.append({
                    "bbox": item["bbox"],
                    "label": pii.entity_type,
                    "text": item["text"]
                })
    return blur_data