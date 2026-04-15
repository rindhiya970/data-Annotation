"""Video processing routes for video frame extraction."""

import os
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.file import File
from app.models.video import Video
from app.models.frame import Frame
from app.services.video_processing_service import extract_frames_from_video, validate_video_file

# Create Blueprint (no url_prefix here, it's added during registration)
video_bp = Blueprint('videos', __name__)


@video_bp.route('', methods=['GET'])
@jwt_required()
def list_videos():
    """
    List all videos for the authenticated user.
    
    Returns:
        JSON response with list of videos
    """
    try:
        # Get current user ID from JWT
        user_id = get_jwt_identity()
        
        # Fetch all videos for the user
        videos = Video.query.filter_by(user_id=user_id).order_by(Video.created_at.desc()).all()
        
        # Build response
        videos_list = [
            {
                'video_id': video.id,
                'filename': video.filename,
                'fps': video.fps,
                'total_frames': video.total_frames,
                'duration': video.duration,
                'created_at': video.created_at.isoformat() if video.created_at else None
            }
            for video in videos
        ]
        
        return jsonify({
            'success': True,
            'message': 'Videos retrieved successfully',
            'data': {
                'videos': videos_list,
                'count': len(videos_list)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'data': None
        }), 500


@video_bp.route('/process', methods=['POST'])
@jwt_required()
def process_video():
    """
    Process an uploaded video file to extract frames.
    
    Expected JSON payload:
        file_id (int): ID of the uploaded video file
        
    Returns:
        JSON response with standardized format
    """
    try:
        # Get current user ID from JWT
        user_id = get_jwt_identity()
        
        # Get request data
        data = request.get_json()
        
        if not data or 'file_id' not in data:
            return jsonify({
                'success': False,
                'message': 'file_id is required',
                'data': None
            }), 400
        
        file_id = data['file_id']
        
        # Validate file exists and belongs to user
        file_record = File.query.filter_by(id=file_id, user_id=user_id).first()
        
        if not file_record:
            return jsonify({
                'success': False,
                'message': 'File not found or access denied',
                'data': None
            }), 404
        
        # Ensure file is a video
        if file_record.file_type != 'video':
            return jsonify({
                'success': False,
                'message': 'File is not a video. Only video files can be processed',
                'data': None
            }), 400
        
        # Check if video already processed (prevent duplicate processing)
        existing_video = Video.query.filter_by(file_id=file_id).first()
        if existing_video:
            return jsonify({
                'success': False,
                'message': 'Video has already been processed',
                'data': {
                    'video_id': existing_video.id
                }
            }), 400
        
        # Get video file path
        video_path = file_record.file_path
        
        if not os.path.exists(video_path):
            return jsonify({
                'success': False,
                'message': 'Video file not found on disk',
                'data': None
            }), 404
        
        # Validate video file extension
        if not validate_video_file(file_record.original_filename):
            return jsonify({
                'success': False,
                'message': 'Invalid video file type',
                'data': None
            }), 400
        
        # Create video record first to get video_id
        video_record = Video(
            user_id=user_id,
            file_id=file_id,
            filename=file_record.original_filename,
            filepath=video_path,
            fps=0,  # Temporary, will update after processing
            total_frames=0,  # Temporary, will update after processing
            duration=0  # Temporary, will update after processing
        )
        
        db.session.add(video_record)
        db.session.flush()  # Get video_id without committing
        
        # Create output directory for frames safely
        frames_dir = os.path.join('uploads', 'frames', f'video_{video_record.id}')
        frames_dir_full = os.path.join(os.getcwd(), frames_dir)

        # If a leftover dir exists from a failed attempt, clean it up
        if os.path.exists(frames_dir_full):
            import shutil
            shutil.rmtree(frames_dir_full)
        
        # Get max video duration from config
        max_duration = current_app.config.get('MAX_VIDEO_DURATION', 300)
        
        # Process video using OpenCV service with duration limit
        fps, total_frames, duration, error = extract_frames_from_video(
            video_path, 
            frames_dir_full
        )
        
        if error:
            db.session.rollback()
            # Clean up directory if it was created
            if os.path.exists(frames_dir_full):
                try:
                    import shutil
                    shutil.rmtree(frames_dir_full)
                except:
                    pass
            return jsonify({
                'success': False,
                'message': f'Video processing failed: {error}',
                'data': None
            }), 400
        
        # Update video record with actual values
        video_record.fps = fps
        video_record.total_frames = total_frames
        video_record.duration = duration
        
        # Create Frame records for each extracted frame
        frame_records = []
        for frame_num in range(1, total_frames + 1):
            frame_filename = f"frame_{frame_num:04d}.jpg"
            frame_path = os.path.join(frames_dir_full, frame_filename)
            
            # Verify frame file exists
            if not os.path.exists(frame_path):
                db.session.rollback()
                return jsonify({
                    'success': False,
                    'message': f'Frame {frame_num} was not created successfully',
                    'data': None
                }), 500
            
            frame_record = Frame(
                video_id=video_record.id,
                frame_number=frame_num,
                frame_path=frame_path
            )
            frame_records.append(frame_record)
        
        # Bulk insert frame records
        db.session.bulk_save_objects(frame_records)
        
        # Commit all changes
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Video processed successfully',
            'data': {
                'video_id': video_record.id,
                'total_frames': total_frames,
                'fps': fps,
                'duration': duration
            }
        }), 201
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Internal server error: {str(e)}',
            'data': None
        }), 500


@video_bp.route('/<int:video_id>/frames', methods=['GET'])
@jwt_required()
def get_video_frames(video_id):
    """
    Fetch all frames for a specific video.
    
    Args:
        video_id (int): ID of the video
        
    Returns:
        JSON response with standardized format
    """
    try:
        # Get current user ID from JWT
        user_id = get_jwt_identity()
        
        # Validate video exists and belongs to user
        video_record = Video.query.filter_by(id=video_id, user_id=user_id).first()
        
        if not video_record:
            return jsonify({
                'success': False,
                'message': 'Video not found or access denied',
                'data': None
            }), 404
        
        # Fetch frames ordered by frame_number
        frames = Frame.query.filter_by(video_id=video_id).order_by(Frame.frame_number).all()
        
        # Build response
        frames_list = [
            {
                'frame_id': frame.id,
                'frame_number': frame.frame_number,
                'frame_path': frame.frame_path
            }
            for frame in frames
        ]
        
        return jsonify({
            'success': True,
            'message': 'Frames retrieved successfully',
            'data': {
                'video_id': video_id,
                'total_frames': len(frames_list),
                'frames': frames_list
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'data': None
        }), 500


@video_bp.route('/by-file/<int:file_id>', methods=['GET'])
@jwt_required()
def get_video_by_file(file_id):
    """Get video record for a given file_id."""
    try:
        user_id = get_jwt_identity()
        uid = int(user_id)
        video = Video.query.filter_by(file_id=file_id, user_id=uid).first()
        if not video:
            return jsonify({'success': False, 'message': 'Video not processed yet'}), 404
        frames = Frame.query.filter_by(video_id=video.id).order_by(Frame.frame_number).all()
        return jsonify({
            'success': True,
            'data': {
                'video': video.to_dict(),
                'frames': [f.to_dict() for f in frames]
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': 'Internal server error'}), 500


@video_bp.route('/frame-image/<int:frame_id>', methods=['GET'])
def serve_frame_image(frame_id):
    """Serve a frame image file. Accepts JWT via Authorization header or ?token= query param."""
    from flask import send_file, request as req
    from flask_jwt_extended import decode_token
    try:
        # Try header first, then query param
        token = None
        auth_header = req.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
        elif req.args.get('token'):
            token = req.args.get('token')
        
        if not token:
            return jsonify({'success': False, 'message': 'Missing token'}), 401
        
        decoded = decode_token(token)
        uid = int(decoded['sub'])
        
        frame = Frame.query.filter_by(id=frame_id).first()
        if not frame:
            return jsonify({'success': False, 'message': 'Frame not found'}), 404
        video = Video.query.filter_by(id=frame.video_id, user_id=uid).first()
        if not video:
            return jsonify({'success': False, 'message': 'Access denied'}), 403
        frame_path = os.path.abspath(frame.frame_path)
        if not os.path.exists(frame_path):
            return jsonify({'success': False, 'message': 'Frame file not found'}), 404
        return send_file(frame_path, mimetype='image/jpeg')
    except Exception as e:
        return jsonify({'success': False, 'message': 'Internal server error'}), 500
