"""File management routes for upload and retrieval."""

import traceback
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.file_service import save_uploaded_file, get_user_files, get_file_by_id

file_bp = Blueprint('files', __name__)


@file_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    """Upload a file (JWT protected)."""
    try:
        print("\n" + "="*60)
        print("[DEBUG] ===== UPLOAD REQUEST RECEIVED =====")
        print(f"[DEBUG] Request method: {request.method}")
        print(f"[DEBUG] Request content_type: {request.content_type}")
        print(f"[DEBUG] Request content_length: {request.content_length}")
        print(f"[DEBUG] Request files: {request.files}")
        print(f"[DEBUG] Request files keys: {list(request.files.keys())}")
        print("="*60 + "\n")

        # Get user ID from JWT token
        user_id = get_jwt_identity()
        print(f"[DEBUG] Using user_id from JWT: {user_id}")

        if 'file' not in request.files:
            print("[ERROR] 'file' key not found in request.files")
            return jsonify({
                'success': False,
                'message': 'No file provided',
                'data': None
            }), 400

        file_storage = request.files['file']
        print(f"[DEBUG] File retrieved: {file_storage.filename}")

        if not file_storage.filename or not file_storage.filename.strip():
            print("[ERROR] Filename is empty")
            return jsonify({
                'success': False,
                'message': 'Filename cannot be empty',
                'data': None
            }), 400

        print(f"[DEBUG] Calling save_uploaded_file...")
        file_record, error = save_uploaded_file(file_storage, user_id)

        if error:
            print(f"[ERROR] save_uploaded_file failed: {error}")
            return jsonify({
                'success': False,
                'message': error,
                'data': None
            }), 400

        print(f"[SUCCESS] File uploaded successfully: ID={file_record.id}")
        return jsonify({
            'success': True,
            'message': 'File uploaded successfully',
            'data': file_record.to_dict()
        }), 201

    except Exception as e:
        print("\n" + "="*60)
        print("[EXCEPTION] Error in upload_file:")
        print(traceback.format_exc())
        print("="*60 + "\n")

        return jsonify({
            'success': False,
            'message': f'Internal server error: {str(e)}',
            'data': None
        }), 500


@file_bp.route('', methods=['GET'])
@jwt_required()
def list_files():
    """List all files for current user (JWT protected)."""
    try:
        # Get user ID from JWT token
        user_id = get_jwt_identity()

        file_type = request.args.get('type')

        if file_type and file_type not in ['image', 'video']:
            return jsonify({
                'success': False,
                'message': 'Invalid file type. Must be "image" or "video"',
                'data': None
            }), 400

        files = get_user_files(user_id, file_type)

        return jsonify({
            'success': True,
            'message': 'Files retrieved successfully',
            'data': {
                'files': [file.to_dict() for file in files],
                'count': len(files)
            }
        }), 200

    except Exception as e:
        print("[EXCEPTION] Error in list_files:")
        print(traceback.format_exc())

        return jsonify({
            'success': False,
            'message': f'Internal server error: {str(e)}',
            'data': None
        }), 500


@file_bp.route('/<int:file_id>', methods=['GET'])
@jwt_required()
def get_file_metadata(file_id):
    """Get metadata for a specific file (JWT protected)."""
    try:
        # Get user ID from JWT token
        user_id = get_jwt_identity()

        file_record = get_file_by_id(file_id, user_id)

        if not file_record:
            return jsonify({
                'success': False,
                'message': 'File not found or access denied',
                'data': None
            }), 404

        return jsonify({
            'success': True,
            'message': 'File retrieved successfully',
            'data': {
                'file': file_record.to_dict()
            }
        }), 200

    except Exception as e:
        print("[EXCEPTION] Error in get_file_metadata:")
        print(traceback.format_exc())

        return jsonify({
            'success': False,
            'message': f'Internal server error: {str(e)}',
            'data': None
        }), 500


@file_bp.route('/<int:file_id>', methods=['DELETE'])
@jwt_required()
def delete_file(file_id):
    """Delete a specific file (JWT protected)."""
    try:
        import os, shutil
        from app.extensions import db
        from app.models.video import Video
        from app.models.frame import Frame
        from app.models.annotation import Annotation

        user_id = get_jwt_identity()
        file_record = get_file_by_id(file_id, user_id)

        if not file_record:
            return jsonify({
                'success': False,
                'message': 'File not found or access denied',
                'data': None
            }), 404

        # If this file has a linked video, delete frames + video first
        video = Video.query.filter_by(file_id=file_id).first()
        if video:
            # Delete frame files from disk
            frames = Frame.query.filter_by(video_id=video.id).all()
            if frames:
                frames_dir = os.path.dirname(os.path.abspath(frames[0].frame_path))
                if os.path.exists(frames_dir):
                    try:
                        shutil.rmtree(frames_dir)
                    except Exception as e:
                        print(f"[DELETE] Warning: could not remove frames dir: {e}")
            # Delete annotations on frames/video
            Annotation.query.filter_by(video_id=video.id).delete()
            Frame.query.filter_by(video_id=video.id).delete()
            db.session.delete(video)
            db.session.flush()

        # Delete image annotations
        Annotation.query.filter_by(file_id=file_id).delete()

        # Delete file from disk
        if os.path.exists(file_record.file_path):
            try:
                os.remove(file_record.file_path)
            except Exception as e:
                print(f"[DELETE] Warning: could not delete file from disk: {e}")

        db.session.delete(file_record)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'File deleted successfully',
            'data': {'deleted_file_id': file_id}
        }), 200

    except Exception as e:
        from app.extensions import db
        db.session.rollback()
        print("[EXCEPTION] Error in delete_file:")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': f'Internal server error: {str(e)}',
            'data': None
        }), 500


@file_bp.route('/annotated', methods=['GET'])
@jwt_required()
def list_annotated_files():
    """Return files that have at least one saved annotation."""
    try:
        from app.extensions import db
        from app.models.annotation import Annotation
        from app.models.file import File
        from app.models.video import Video

        user_id = get_jwt_identity()
        uid = int(user_id)

        # Image files with annotations
        annotated_file_ids = (
            db.session.query(Annotation.file_id)
            .filter(Annotation.user_id == uid, Annotation.file_id != None)
            .distinct()
            .all()
        )
        file_ids = [r[0] for r in annotated_file_ids]

        results = []
        seen_file_ids = set()

        for fid in file_ids:
            f = File.query.filter_by(id=fid, user_id=uid).first()
            if not f:
                continue
            count = Annotation.query.filter_by(file_id=fid, user_id=uid).count()
            d = f.to_dict()
            d['annotation_count'] = count
            results.append(d)
            seen_file_ids.add(fid)

        # Video files with frame annotations
        annotated_video_ids = (
            db.session.query(Annotation.video_id)
            .filter(Annotation.user_id == uid, Annotation.video_id != None)
            .distinct()
            .all()
        )
        for (vid,) in annotated_video_ids:
            video = Video.query.filter_by(id=vid, user_id=uid).first()
            if not video or video.file_id in seen_file_ids:
                continue
            f = File.query.filter_by(id=video.file_id, user_id=uid).first()
            if not f:
                continue
            count = Annotation.query.filter_by(video_id=vid, user_id=uid).count()
            d = f.to_dict()
            d['annotation_count'] = count
            results.append(d)
            seen_file_ids.add(video.file_id)

        results.sort(key=lambda x: x['created_at'], reverse=True)

        return jsonify({
            'success': True,
            'data': {'files': results, 'count': len(results)}
        }), 200

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'success': False, 'message': f'Internal server error: {str(e)}'}), 500
