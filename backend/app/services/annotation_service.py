"""Annotation service."""

from app.extensions import db
from app.models.annotation import Annotation
from app.models.file import File
from app.models.frame import Frame
from app.models.video import Video


def create_annotation(data, user_id):
    uid = int(user_id)
    required = ['file_id', 'label', 'x', 'y', 'width', 'height']
    missing = [f for f in required if f not in data]
    if missing:
        raise ValueError(f"Missing fields: {', '.join(missing)}")
    label = str(data['label']).strip()
    if not label:
        raise ValueError("Label cannot be empty")
    try:
        x, y, w, h = float(data['x']), float(data['y']), float(data['width']), float(data['height'])
    except (TypeError, ValueError):
        raise ValueError("Coordinates must be numeric")
    if w <= 0 or h <= 0:
        raise ValueError("Width and height must be positive")
    file_id = int(data['file_id'])
    file = File.query.filter_by(id=file_id, user_id=uid).first()
    if not file:
        raise ValueError("File not found or access denied")
    annotation = Annotation(user_id=uid, file_id=file_id, label=label, x=x, y=y, width=w, height=h)
    db.session.add(annotation)
    db.session.commit()
    return annotation


def create_frame_annotation(data, user_id):
    uid = int(user_id)
    required = ['frame_id', 'video_id', 'label', 'x', 'y', 'width', 'height']
    missing = [f for f in required if f not in data]
    if missing:
        raise ValueError(f"Missing fields: {', '.join(missing)}")
    label = str(data['label']).strip()
    if not label:
        raise ValueError("Label cannot be empty")
    try:
        x, y, w, h = float(data['x']), float(data['y']), float(data['width']), float(data['height'])
    except (TypeError, ValueError):
        raise ValueError("Coordinates must be numeric")
    if w <= 0 or h <= 0:
        raise ValueError("Width and height must be positive")
    frame_id = int(data['frame_id'])
    video_id = int(data['video_id'])
    video = Video.query.filter_by(id=video_id, user_id=uid).first()
    if not video:
        raise ValueError("Video not found or access denied")
    frame = Frame.query.filter_by(id=frame_id, video_id=video_id).first()
    if not frame:
        raise ValueError("Frame not found")
    annotation = Annotation(
        user_id=uid, video_id=video_id, frame_id=frame_id,
        label=label, x=x, y=y, width=w, height=h
    )
    db.session.add(annotation)
    db.session.commit()
    return annotation


def get_annotations_by_file(file_id, user_id):
    uid = int(user_id)
    file = File.query.filter_by(id=file_id, user_id=uid).first()
    if not file:
        raise ValueError("File not found or access denied")
    annotations = Annotation.query.filter_by(file_id=file_id).order_by(Annotation.created_at).all()
    return [a.to_dict() for a in annotations]


def get_annotations_by_frame(frame_id, user_id):
    uid = int(user_id)
    frame = Frame.query.filter_by(id=frame_id).first()
    if not frame:
        raise ValueError("Frame not found")
    video = Video.query.filter_by(id=frame.video_id, user_id=uid).first()
    if not video:
        raise ValueError("Access denied")
    annotations = Annotation.query.filter_by(frame_id=frame_id).order_by(Annotation.created_at).all()
    return [a.to_dict() for a in annotations]


def update_annotation(annotation_id, data, user_id):
    uid = int(user_id)
    annotation = Annotation.query.filter_by(id=annotation_id).first()
    if not annotation:
        raise ValueError("Annotation not found")
    if annotation.user_id != uid:
        raise ValueError("Access denied")
    if 'label' in data:
        label = str(data['label']).strip()
        if not label:
            raise ValueError("Label cannot be empty")
        annotation.label = label
    for field in ['x', 'y', 'width', 'height']:
        if field in data:
            try:
                val = float(data[field])
            except (TypeError, ValueError):
                raise ValueError(f"{field} must be numeric")
            if field in ('width', 'height') and val <= 0:
                raise ValueError(f"{field} must be positive")
            setattr(annotation, field, val)
    db.session.commit()
    return annotation


def delete_annotation(annotation_id, user_id):
    uid = int(user_id)
    annotation = Annotation.query.filter_by(id=annotation_id).first()
    if not annotation:
        raise ValueError("Annotation not found")
    if annotation.user_id != uid:
        raise ValueError("Access denied")
    db.session.delete(annotation)
    db.session.commit()
    return True
