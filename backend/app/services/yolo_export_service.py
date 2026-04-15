"""YOLO format export service for annotations (production-safe)."""

import os
import cv2
import tempfile
import zipfile
import logging
import shutil
from pathlib import Path

from app.models.file import File
from app.models.video import Video
from app.models.frame import Frame
from app.models.annotation import Annotation
from app.utils.yolo_converter import (
    convert_annotations_to_yolo,
    convert_bbox_to_yolo,
    build_label_class_map,
    generate_classes_file
)

logger = logging.getLogger(__name__)


# ============================================================
# IMAGE YOLO EXPORT
# ============================================================

def generate_yolo_for_image(file_id, user_id):
    try:
        file_record = File.query.filter_by(id=file_id, user_id=user_id).first()
        if not file_record:
            return None, None, "File not found or access denied"

        if file_record.file_type != "image":
            return None, None, "File is not an image"

        file_path = os.path.abspath(file_record.file_path)
        if not os.path.exists(file_path):
            return None, None, "Image file not found"

        image = cv2.imread(file_path)
        if image is None:
            return None, None, "Failed to load image"

        img_height, img_width = image.shape[:2]

        annotations = Annotation.query.filter_by(
            file_id=file_id,
            user_id=user_id
        ).all()

        annotation_dicts = [ann.to_dict() for ann in annotations]

        yolo_text, label_map = convert_annotations_to_yolo(
            annotation_dicts,
            img_width,
            img_height
        )

        base_name = Path(file_record.original_filename).stem
        filename = f"{base_name}.txt"

        return yolo_text, filename, None

    except Exception as e:
        logger.error(f"YOLO image export failed: {e}")
        return None, None, str(e)


# ============================================================
# VIDEO YOLO EXPORT  (frame images + YOLO labels)
# Structure:
#   dataset/
#     images/  <- frame_0001.jpg, frame_0002.jpg ...
#     labels/  <- frame_0001.txt, frame_0002.txt ...
#     classes.txt
#     data.yaml
# ============================================================

def generate_yolo_for_video(video_id, user_id):
    temp_dir = None
    temp_zip_path = None

    try:
        uid = int(user_id)

        video_record = Video.query.filter_by(id=video_id, user_id=uid).first()
        if not video_record:
            return None, None, "Video not found or access denied"

        frames = Frame.query.filter_by(video_id=video_id).order_by(Frame.frame_number).all()
        if not frames:
            return None, None, "No frames found for this video"

        annotations = Annotation.query.filter_by(video_id=video_id, user_id=uid).all()
        annotation_dicts = [ann.to_dict() for ann in annotations]

        if not annotation_dicts:
            return None, None, "No annotations found for this video"

        # Build ONE global label map
        label_map = build_label_class_map(annotation_dicts)

        # Group annotations by frame_id
        annotations_by_frame = {}
        for ann in annotation_dicts:
            fid = ann.get("frame_id")
            if fid not in annotations_by_frame:
                annotations_by_frame[fid] = []
            annotations_by_frame[fid].append(ann)

        # Only export frames that have annotations
        annotated_frame_ids = set(annotations_by_frame.keys())

        temp_dir = tempfile.mkdtemp(prefix="yolo_video_export_")
        images_dir = os.path.join(temp_dir, "dataset", "images")
        labels_dir = os.path.join(temp_dir, "dataset", "labels")
        os.makedirs(images_dir, exist_ok=True)
        os.makedirs(labels_dir, exist_ok=True)

        processed = 0

        for frame in frames:
            if frame.id not in annotated_frame_ids:
                continue  # skip unannotated frames

            frame_path = os.path.abspath(frame.frame_path)
            if not os.path.exists(frame_path):
                logger.warning(f"Frame file missing: {frame_path}")
                continue

            frame_image = cv2.imread(frame_path)
            if frame_image is None:
                continue

            img_h, img_w = frame_image.shape[:2]
            stem = f"frame_{frame.frame_number:04d}"

            # Copy frame image into dataset/images/
            dest_img = os.path.join(images_dir, f"{stem}.jpg")
            shutil.copy2(frame_path, dest_img)

            # Build YOLO label lines
            frame_anns = annotations_by_frame.get(frame.id, [])
            lines = []
            for ann in frame_anns:
                try:
                    lines.append(convert_bbox_to_yolo(ann, img_w, img_h, label_map))
                except Exception as e:
                    logger.warning(f"Skipping annotation {ann.get('id')}: {e}")

            with open(os.path.join(labels_dir, f"{stem}.txt"), "w") as f:
                f.write("\n".join(lines))

            processed += 1

        if processed == 0:
            return None, None, "No annotated frames could be processed"

        # classes.txt
        with open(os.path.join(temp_dir, "dataset", "classes.txt"), "w") as f:
            f.write(generate_classes_file(label_map))

        # data.yaml
        sorted_labels = [k for k, _ in sorted(label_map.items(), key=lambda x: x[1])]
        yaml_content = (
            "path: ./dataset\n"
            "train: images\n"
            "val: images\n\n"
            f"nc: {len(sorted_labels)}\n"
            f"names: {sorted_labels}\n"
        )
        with open(os.path.join(temp_dir, "dataset", "data.yaml"), "w") as f:
            f.write(yaml_content)

        # ZIP everything
        temp_fd, temp_zip_path = tempfile.mkstemp(suffix=".zip", prefix="yolo_video_")
        os.close(temp_fd)

        with zipfile.ZipFile(temp_zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(os.path.join(temp_dir, "dataset")):
                for fname in files:
                    full = os.path.join(root, fname)
                    arcname = os.path.relpath(full, temp_dir)
                    zipf.write(full, arcname)

        base_name = Path(video_record.filename).stem
        zip_filename = f"{base_name}_yolo.zip"

        return temp_zip_path, zip_filename, None

    except Exception as e:
        logger.error(f"YOLO video export failed: {e}")
        if temp_zip_path and os.path.exists(temp_zip_path):
            os.remove(temp_zip_path)
        return None, None, str(e)

    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


# ============================================================
# FULL DATASET EXPORT (all user images)
# ============================================================

def generate_yolo_dataset_zip(user_id):
    """Export ALL annotated images for a user as a YOLO dataset ZIP."""
    temp_dir = None
    temp_zip_path = None

    try:
        uid = int(user_id)
        from app.extensions import db

        annotated_file_ids = (
            db.session.query(Annotation.file_id)
            .filter(Annotation.user_id == uid, Annotation.file_id != None)
            .distinct()
            .all()
        )
        file_ids = [r[0] for r in annotated_file_ids]

        if not file_ids:
            return None, None, "No annotated images found"

        all_annotations = Annotation.query.filter(
            Annotation.user_id == uid,
            Annotation.file_id.in_(file_ids)
        ).all()
        all_dicts = [a.to_dict() for a in all_annotations]
        label_map = build_label_class_map(all_dicts)

        temp_dir = tempfile.mkdtemp(prefix="dataset_export_")
        images_dir = os.path.join(temp_dir, "dataset", "images")
        labels_dir = os.path.join(temp_dir, "dataset", "labels")
        os.makedirs(images_dir, exist_ok=True)
        os.makedirs(labels_dir, exist_ok=True)

        processed = 0

        for file_id in file_ids:
            file_record = File.query.filter_by(id=file_id, user_id=uid).first()
            if not file_record:
                continue

            file_path = os.path.abspath(file_record.file_path)
            if not os.path.exists(file_path):
                continue

            img = cv2.imread(file_path)
            if img is None:
                continue

            img_h, img_w = img.shape[:2]
            stem = Path(file_record.original_filename).stem
            ext  = Path(file_record.original_filename).suffix or ".jpg"

            shutil.copy2(file_path, os.path.join(images_dir, f"{stem}{ext}"))

            file_anns = [a for a in all_dicts if a.get("file_id") == file_id]
            lines = []
            for ann in file_anns:
                try:
                    lines.append(convert_bbox_to_yolo(ann, img_w, img_h, label_map))
                except Exception as e:
                    logger.warning(f"Skipping annotation {ann.get('id')}: {e}")

            with open(os.path.join(labels_dir, f"{stem}.txt"), "w") as f:
                f.write("\n".join(lines))

            processed += 1

        if processed == 0:
            return None, None, "No images could be processed"

        with open(os.path.join(temp_dir, "dataset", "classes.txt"), "w") as f:
            f.write(generate_classes_file(label_map))

        sorted_labels = [k for k, _ in sorted(label_map.items(), key=lambda x: x[1])]
        yaml_content = (
            "path: ./dataset\n"
            "train: images\n"
            "val: images\n\n"
            f"nc: {len(sorted_labels)}\n"
            f"names: {sorted_labels}\n"
        )
        with open(os.path.join(temp_dir, "dataset", "data.yaml"), "w") as f:
            f.write(yaml_content)

        temp_fd, temp_zip_path = tempfile.mkstemp(suffix=".zip", prefix="yolo_dataset_")
        os.close(temp_fd)

        with zipfile.ZipFile(temp_zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(os.path.join(temp_dir, "dataset")):
                for fname in files:
                    full = os.path.join(root, fname)
                    arcname = os.path.relpath(full, temp_dir)
                    zipf.write(full, arcname)

        return temp_zip_path, "yolo_dataset.zip", None

    except Exception as e:
        logger.error(f"Dataset ZIP export failed: {e}")
        if temp_zip_path and os.path.exists(temp_zip_path):
            os.remove(temp_zip_path)
        return None, None, str(e)

    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
