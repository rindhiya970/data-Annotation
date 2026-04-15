"""AI-based auto annotation service using YOLOv8."""

import os
import logging

logger = logging.getLogger(__name__)

# ── Model singleton ───────────────────────────────────────────────────────────
# Loaded once at module import time; reused for every request.
_model = None


def _get_model():
    """Return the YOLO model, loading it on first call."""
    global _model
    if _model is None:
        try:
            from ultralytics import YOLO
            _model = YOLO("yolov8n.pt")   # downloads automatically on first run
            logger.info("[ai_service] YOLOv8n model loaded successfully")
        except Exception as e:
            logger.error(f"[ai_service] Failed to load YOLO model: {e}")
            raise RuntimeError(f"Could not load YOLO model: {e}")
    return _model


# ── Public API ────────────────────────────────────────────────────────────────

def detect_objects(image_path: str) -> list:
    """
    Run YOLOv8 inference on an image and return detections.

    Args:
        image_path: Absolute path to the image file.

    Returns:
        List of dicts, each with keys:
            label  – COCO class name (str)
            x      – top-left x in pixels (float)
            y      – top-left y in pixels (float)
            width  – box width  in pixels (float)
            height – box height in pixels (float)

    Raises:
        FileNotFoundError: if image_path does not exist.
        RuntimeError:      if the model fails to run inference.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    model = _get_model()

    try:
        results = model(image_path, verbose=False)
    except Exception as e:
        raise RuntimeError(f"YOLO inference failed: {e}")

    detections = []

    for result in results:
        boxes      = result.boxes
        class_names = result.names   # {class_id: class_name}

        for box in boxes:
            # xyxy → x, y, w, h
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            x = x1
            y = y1
            w = x2 - x1
            h = y2 - y1

            class_id   = int(box.cls[0].item())
            label      = class_names.get(class_id, str(class_id))
            confidence = round(float(box.conf[0].item()), 4)

            detections.append({
                "label":      label,
                "x":          round(x, 2),
                "y":          round(y, 2),
                "width":      round(w, 2),
                "height":     round(h, 2),
                "confidence": confidence,
            })

    return detections
