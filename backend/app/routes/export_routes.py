"""Export routes for exporting annotations in various formats."""

import os
import logging
from flask import Blueprint, jsonify, Response, send_file, after_this_request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.export_service import export_annotations_json, export_annotations_csv

# Create Blueprint (no url_prefix here, it's added during registration)
export_bp = Blueprint('export', __name__)

logger = logging.getLogger(__name__)

# ---------------------------
# BASIC EXPORTS
# ---------------------------

@export_bp.route('/json', methods=['GET'])
@jwt_required()
def export_json():
    try:
        user_id = get_jwt_identity()
        export_data = export_annotations_json(user_id)

        return jsonify({
            'success': True,
            'message': 'Annotations exported successfully',
            'data': {
                'count': export_data['total_annotations'],
                'annotations': export_data['annotations']
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'data': None
        }), 500


@export_bp.route('/csv', methods=['GET'])
@jwt_required()
def export_csv():
    try:
        user_id = get_jwt_identity()
        csv_string = export_annotations_csv(user_id)

        return Response(
            csv_string,
            mimetype='text/csv',
            headers={
                'Content-Disposition': 'attachment; filename=annotations.csv'
            }
        )

    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'data': None
        }), 500


# ---------------------------
# ANNOTATED MEDIA EXPORT
# ---------------------------

@export_bp.route('/annotated-image/<int:file_id>', methods=['GET'])
@jwt_required()
def export_annotated_image(file_id):
    try:
        user_id = get_jwt_identity()

        from app.services.annotated_media_service import generate_annotated_image

        image_bytes, filename, error = generate_annotated_image(file_id, user_id)

        if error:
            status_code = 404 if 'not found' in error.lower() or 'access denied' in error.lower() else 400
            return jsonify({
                'success': False,
                'message': error,
                'data': None
            }), status_code

        return Response(
            image_bytes,
            mimetype='image/jpeg',
            headers={
                'Content-Disposition': f'attachment; filename={filename}'
            }
        )

    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'data': None
        }), 500


@export_bp.route('/annotated-video/<int:video_id>', methods=['GET'])
@jwt_required()
def export_annotated_video(video_id):
    try:
        user_id = get_jwt_identity()

        from app.services.annotated_media_service import generate_annotated_video

        temp_path, filename, error = generate_annotated_video(video_id, user_id)

        if error:
            status_code = 404 if 'not found' in error.lower() or 'access denied' in error.lower() else 400
            return jsonify({
                'success': False,
                'message': error,
                'data': None
            }), status_code

        @after_this_request
        def cleanup(response):
            try:
                os.remove(temp_path)
                logger.info(f"Cleaned up temp video: {temp_path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temp video: {str(e)}")
            return response

        return send_file(
            temp_path,
            as_attachment=True,
            download_name=filename,
            mimetype='video/mp4'
        )

    except Exception as e:
        logger.error(f"Annotated video export error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'data': None
        }), 500


# ---------------------------
# YOLO FORMAT EXPORT
# ---------------------------

@export_bp.route('/yolo/image/<int:file_id>', methods=['GET'])
@jwt_required()
def export_yolo_image(file_id):
    try:
        user_id = get_jwt_identity()

        from app.services.yolo_export_service import generate_yolo_for_image

        logger.info(f"YOLO export requested for image {file_id} by user {user_id}")

        yolo_content, filename, error = generate_yolo_for_image(file_id, user_id)

        if error:
            status_code = 404 if 'not found' in error.lower() or 'access denied' in error.lower() else 400
            return jsonify({
                'success': False,
                'message': error,
                'data': None
            }), status_code

        return Response(
            yolo_content,
            mimetype='text/plain',
            headers={
                'Content-Disposition': f'attachment; filename={filename}'
            }
        )

    except Exception as e:
        logger.error(f"YOLO image export error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'data': None
        }), 500


@export_bp.route('/yolo/dataset', methods=['GET'])
@jwt_required()
def export_yolo_dataset():
    """Export ALL annotated images as a YOLO dataset ZIP (images/ + labels/ + classes.txt)."""
    try:
        user_id = get_jwt_identity()
        from app.services.yolo_export_service import generate_yolo_dataset_zip

        zip_path, filename, error = generate_yolo_dataset_zip(user_id)

        if error:
            return jsonify({'success': False, 'message': error}), 400

        @after_this_request
        def cleanup(response):
            try:
                os.remove(zip_path)
            except Exception:
                pass
            return response

        return send_file(zip_path, as_attachment=True, download_name=filename, mimetype='application/zip')

    except Exception as e:
        logger.error(f"Dataset export error: {str(e)}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500


@export_bp.route('/yolo/video/<int:video_id>', methods=['GET'])
@jwt_required()
def export_yolo_video(video_id):
    try:
        user_id = get_jwt_identity()

        from app.services.yolo_export_service import generate_yolo_for_video

        logger.info(f"YOLO export requested for video {video_id} by user {user_id}")

        zip_path, filename, error = generate_yolo_for_video(video_id, user_id)

        if error:
            status_code = 404 if 'not found' in error.lower() or 'access denied' in error.lower() else 400
            return jsonify({
                'success': False,
                'message': error,
                'data': None
            }), status_code

        @after_this_request
        def cleanup(response):
            try:
                os.remove(zip_path)
                logger.info(f"Cleaned up temp ZIP: {zip_path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temp ZIP: {str(e)}")
            return response

        return send_file(
            zip_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/zip'
        )

    except Exception as e:
        logger.error(f"YOLO video export error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'data': None
        }), 500
