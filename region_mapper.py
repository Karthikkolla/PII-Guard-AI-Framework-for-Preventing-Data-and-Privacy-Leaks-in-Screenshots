import numpy as np


def collect_regions(nlp_boxes, yolo_objects, faces, padding=3, img_shape=None):
    all_regions = []
    h, w = img_shape if img_shape else (None, None)

    # Helper to process any detection source
    def process_item(item, source_label):
        # 1. Extract Bounding Box
        if isinstance(item, dict):
            bbox = item.get("bbox")
            label = item.get("label", source_label)
        else:
            bbox = item
            label = source_label

        if bbox and len(bbox) == 4:
            # 2. Handle [x, y, w, h] vs [x1, y1, x2, y2]
            x1, y1, x2, y2 = bbox
            # If coordinates are very small (width/height style), convert them
            if x2 < 10 or y2 < 10:  # Heuristic for tiny boxes or w/h format
                pass  # Adjust if your model uses normalized coordinates

            # Ensure x2/y2 are actual points, not widths
            # If x2 is smaller than x1, it's definitely [x, y, w, h]
            if x2 < x1:
                x2 = x1 + x2
                y2 = y1 + y2

            return {
                "bbox": apply_padding([x1, y1, x2, y2], padding, h, w),
                "label": label
            }
        return None

    # Process everything into the pool
    for source, tag in [(nlp_boxes, "TEXT"), (yolo_objects, "YOLO"), (faces, "FACE")]:
        for item in source:
            region = process_item(item, tag)
            if region:
                all_regions.append(region)

    return all_regions


def apply_padding(bbox, padding, max_h, max_w):
    x1, y1, x2, y2 = bbox
    x1, y1 = x1 - padding, y1 - padding
    x2, y2 = x2 + padding, y2 + padding
    if max_h is not None and max_w is not None:
        x1, x2 = np.clip([x1, x2], 0, max_w)
        y1, y2 = np.clip([y1, y2], 0, max_h)
    return [int(x1), int(y1), int(x2), int(y2)]