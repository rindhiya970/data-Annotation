"""YOLO format converter utility for bounding box annotations.

Production-safe implementation:
- Sequential class IDs (0...N-1)
- Deterministic mapping per export
- No hashing
- No random IDs
- YOLO training compatible
"""

import logging

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# CLASS MAPPING UTILITIES (DATASET-SAFE)
# ------------------------------------------------------------------

def build_label_class_map(annotations):
    """
    Build a sequential, deterministic label → class_id mapping.

    Rules:
    - Normalize labels (strip + lowercase)
    - Remove empty labels
    - Sort alphabetically
    - Assign sequential IDs starting from 0

    Args:
        annotations (list): List of annotation dictionaries

    Returns:
        dict: {normalized_label: class_id}
    """
    labels = set()

    for ann in annotations:
        label = ann.get("label")
        if label and isinstance(label, str):
            normalized = label.strip().lower()
            if normalized:
                labels.add(normalized)

    sorted_labels = sorted(labels)

    label_map = {label: idx for idx, label in enumerate(sorted_labels)}

    logger.info(f"Generated class mapping: {label_map}")

    return label_map


# ------------------------------------------------------------------
# YOLO CONVERSION
# ------------------------------------------------------------------

def convert_bbox_to_yolo(annotation, img_width, img_height, label_map):
    """
    Convert bounding box annotation to YOLO format.

    YOLO format:
    <class_id> <x_center> <y_center> <width> <height>

    All values normalized between 0 and 1.

    Args:
        annotation (dict): Must contain label, x, y, width, height
        img_width (int)
        img_height (int)
        label_map (dict): Precomputed label → class_id mapping

    Returns:
        str: YOLO formatted line
    """

    if img_width <= 0 or img_height <= 0:
        raise ValueError(f"Invalid image dimensions: {img_width}x{img_height}")

    required_fields = ["label", "x", "y", "width", "height"]
    for field in required_fields:
        if field not in annotation:
            raise ValueError(f"Missing required field: {field}")

    try:
        label = annotation["label"]
        normalized_label = label.strip().lower()

        if normalized_label not in label_map:
            raise ValueError(f"Label '{label}' not found in class mapping")

        class_id = label_map[normalized_label]

        x = float(annotation["x"])
        y = float(annotation["y"])
        width = float(annotation["width"])
        height = float(annotation["height"])

        if width <= 0 or height <= 0:
            raise ValueError(
                f"Invalid bounding box dimensions: width={width}, height={height}"
            )

        # Prevent negative coordinates
        x = max(0.0, x)
        y = max(0.0, y)

        # Convert to YOLO center format
        x_center = x + (width / 2.0)
        y_center = y + (height / 2.0)

        # Normalize
        x_center_norm = x_center / img_width
        y_center_norm = y_center / img_height
        width_norm = width / img_width
        height_norm = height / img_height

        # Clamp to [0,1]
        x_center_norm = max(0.0, min(1.0, x_center_norm))
        y_center_norm = max(0.0, min(1.0, y_center_norm))
        width_norm = max(0.0, min(1.0, width_norm))
        height_norm = max(0.0, min(1.0, height_norm))

        yolo_line = (
            f"{class_id} "
            f"{x_center_norm:.6f} "
            f"{y_center_norm:.6f} "
            f"{width_norm:.6f} "
            f"{height_norm:.6f}"
        )

        return yolo_line

    except (TypeError, ValueError) as e:
        raise ValueError(f"Error converting annotation: {str(e)}")


def convert_annotations_to_yolo(annotations, img_width, img_height):
    """
    Convert multiple annotations to YOLO format.

    This function:
    - Builds dataset-safe class mapping
    - Converts all annotations
    - Skips invalid entries safely

    Args:
        annotations (list)
        img_width (int)
        img_height (int)

    Returns:
        tuple:
            - yolo_text (str)
            - label_map (dict)
    """

    if not annotations:
        logger.info("No annotations provided")
        return "", {}

    label_map = build_label_class_map(annotations)

    yolo_lines = []

    for idx, ann in enumerate(annotations):
        try:
            yolo_line = convert_bbox_to_yolo(
                ann, img_width, img_height, label_map
            )
            yolo_lines.append(yolo_line)
        except ValueError as e:
            logger.error(f"Skipping annotation {idx}: {e}")
            continue

    return "\n".join(yolo_lines), label_map


# ------------------------------------------------------------------
# CLASSES.TXT GENERATION
# ------------------------------------------------------------------

def generate_classes_file(label_map):
    """
    Generate YOLO classes.txt file content.

    Format:
        One label per line
        Line number = class_id

    Args:
        label_map (dict)

    Returns:
        str
    """

    if not label_map:
        return ""

    # Sort by class_id
    sorted_labels = sorted(label_map.items(), key=lambda x: x[1])

    lines = [label for label, _ in sorted_labels]

    return "\n".join(lines)
