"""Annotation routes."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.annotation import Annotation
from app.services.annotation_service import (
    create_annotation, get_annotations_by_file,
    get_annotations_by_frame, create_frame_annotation,
    update_annotation, delete_annotation
)

annotation_bp = Blueprint('annotations', __name__)


@annotation_bp.route('/file/<int:file_id>', methods=['GET'])
@jwt_required()
def get_file_annotations(file_id):
    try:
        user_id = get_jwt_identity()
        annotations = get_annotations_by_file(file_id, user_id)
        return jsonify({'success': True, 'data': annotations}), 200
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 404
    except Exception:
        return jsonify({'success': False, 'message': 'Internal server error'}), 500


@annotation_bp.route('/video/<int:video_id>/frame-counts', methods=['GET'])
@jwt_required()
def get_video_frame_counts(video_id):
    """Return annotation counts per frame for a video as {frame_id: count}."""
    try:
        from app.models.video import Video
        from sqlalchemy import func
        user_id = get_jwt_identity()
        uid = int(user_id)
        video = Video.query.filter_by(id=video_id, user_id=uid).first()
        if not video:
            return jsonify({'success': False, 'message': 'Video not found'}), 404
        rows = (db.session.query(Annotation.frame_id, func.count(Annotation.id))
                .filter(Annotation.video_id == video_id)
                .group_by(Annotation.frame_id)
                .all())
        counts = {str(frame_id): count for frame_id, count in rows}
        return jsonify({'success': True, 'data': counts}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': 'Internal server error'}), 500


@annotation_bp.route('/frame/<int:frame_id>', methods=['GET'])
@jwt_required()
def get_frame_annotations(frame_id):
    try:
        user_id = get_jwt_identity()
        annotations = get_annotations_by_frame(frame_id, user_id)
        return jsonify({'success': True, 'data': annotations}), 200
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 404
    except Exception:
        return jsonify({'success': False, 'message': 'Internal server error'}), 500


@annotation_bp.route('', methods=['POST'])
@jwt_required()
def create_annotation_route():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        if 'frame_id' in data:
            annotation = create_frame_annotation(data, user_id)
        else:
            annotation = create_annotation(data, user_id)
        return jsonify({'success': True, 'data': annotation.to_dict()}), 201
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception:
        return jsonify({'success': False, 'message': 'Internal server error'}), 500


@annotation_bp.route('/<int:annotation_id>', methods=['PUT'])
@jwt_required()
def update_annotation_route(annotation_id):
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        annotation = update_annotation(annotation_id, data, user_id)
        return jsonify({'success': True, 'data': annotation.to_dict()}), 200
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception:
        return jsonify({'success': False, 'message': 'Internal server error'}), 500


@annotation_bp.route('/<int:annotation_id>', methods=['DELETE'])
@jwt_required()
def delete_annotation_route(annotation_id):
    try:
        user_id = get_jwt_identity()
        delete_annotation(annotation_id, user_id)
        return jsonify({'success': True, 'message': 'Deleted'}), 200
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 404
    except Exception:
        return jsonify({'success': False, 'message': 'Internal server error'}), 500


# ── AUTO-ANNOTATE (NEW) ───────────────────────────────────────────────────────

@annotation_bp.route('/auto-annotate/<int:file_id>', methods=['POST'])
@jwt_required()
def auto_annotate(file_id):
    """
    Run YOLOv8 on an uploaded image and return detections.
    Detections are NOT saved to the DB automatically - the client
    decides which ones to keep and calls POST /api/annotations to save.

    Returns:
        {
          "success": true,
          "data": [
            { "label": "person", "x": 10, "y": 20, "width": 80, "height": 120, "confidence": 0.91 },
            ...
          ]
        }
    """
    try:
        import os
        from app.models.file import File
        from app.services.ai_service import detect_objects

        user_id = get_jwt_identity()
        uid = int(user_id)

        file_record = File.query.filter_by(id=file_id, user_id=uid).first()
        if not file_record:
            return jsonify({'success': False, 'message': 'File not found or access denied'}), 404

        if file_record.file_type != 'image':
            return jsonify({'success': False, 'message': 'Auto-annotation only supports image files'}), 400

        image_path = os.path.abspath(file_record.file_path)

        detections = detect_objects(image_path)

        return jsonify({
            'success': True,
            'data': detections,
            'count': len(detections)
        }), 200

    except FileNotFoundError as e:
        return jsonify({'success': False, 'message': str(e)}), 404
    except RuntimeError as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': 'Internal server error'}), 500


# ── AUTO-ANNOTATE FRAME (NEW) ─────────────────────────────────────────────────

@annotation_bp.route('/auto-annotate-frame/<int:frame_id>', methods=['POST'])
@jwt_required()
def auto_annotate_frame(frame_id):
    """
    Run YOLOv8 on a video frame and return detections.
    NOT saved to DB - client appends and saves manually.
    """
    try:
        import os
        from app.models.frame import Frame
        from app.models.video import Video
        from app.services.ai_service import detect_objects

        user_id = get_jwt_identity()
        uid = int(user_id)

        frame = Frame.query.filter_by(id=frame_id).first()
        if not frame:
            return jsonify({'success': False, 'message': 'Frame not found'}), 404

        # Verify ownership via video
        video = Video.query.filter_by(id=frame.video_id, user_id=uid).first()
        if not video:
            return jsonify({'success': False, 'message': 'Access denied'}), 403

        frame_path = os.path.abspath(frame.frame_path)
        detections = detect_objects(frame_path)

        return jsonify({
            'success': True,
            'data': detections,
            'count': len(detections)
        }), 200

    except FileNotFoundError as e:
        return jsonify({'success': False, 'message': str(e)}), 404
    except RuntimeError as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    except Exception:
        return jsonify({'success': False, 'message': 'Internal server error'}), 500
