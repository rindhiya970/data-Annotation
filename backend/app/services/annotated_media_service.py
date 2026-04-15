"""Service for generating annotated images and videos."""

import os
import cv2
import tempfile
from app.models.file import File
from app.models.video import Video
from app.models.frame import Frame
from app.models.annotation import Annotation
from app.utils.annotation_renderer import draw_annotations_with_colors


def generate_annotated_image(file_id, user_id):
    """
    Generate annotated image with bounding boxes.
    
    Args:
        file_id (int): ID of the image file
        user_id (int): ID of the user (for authorization)
        
    Returns:
        tuple: (image_bytes, filename, error_message)
               Returns (bytes, filename, None) on success
               Returns (None, None, error_message) on failure
    """
    # Verify file exists and belongs to user
    file_record = File.query.filter_by(id=file_id, user_id=user_id).first()
    if not file_record:
        return None, None, "File not found or access denied"
    
    # Ensure file is an image
    if file_record.file_type != 'image':
        return None, None, "File is not an image"
    
    # Verify file exists on disk
    if not os.path.exists(file_record.file_path):
        return None, None, "Image file not found on disk"
    
    # Prevent path traversal
    file_path = os.path.abspath(file_record.file_path)
    if not file_path.startswith(os.path.abspath(os.getcwd())):
        return None, None, "Invalid file path"
    
    try:
        # Load image
        image = cv2.imread(file_path)
        if image is None:
            return None, None, "Failed to load image"
        
        # Fetch annotations for this image
        annotations = Annotation.query.filter_by(
            file_id=file_id,
            user_id=user_id
        ).all()
        
        # Convert annotations to dict format
        annotation_dicts = [ann.to_dict() for ann in annotations]
        
        # Draw annotations on image
        if annotation_dicts:
            annotated_image = draw_annotations_with_colors(image, annotation_dicts)
        else:
            annotated_image = image
        
        # Encode image to bytes
        success, buffer = cv2.imencode('.jpg', annotated_image)
        if not success:
            return None, None, "Failed to encode annotated image"
        
        image_bytes = buffer.tobytes()
        
        # Generate filename
        base_name = os.path.splitext(file_record.original_filename)[0]
        filename = f"{base_name}_annotated.jpg"
        
        return image_bytes, filename, None
        
    except Exception as e:
        return None, None, f"Error generating annotated image: {str(e)}"


def generate_annotated_video(video_id, user_id):
    """
    Generate annotated video with bounding boxes on frames.
    
    Args:
        video_id (int): ID of the video
        user_id (int): ID of the user (for authorization)
        
    Returns:
        tuple: (video_path, filename, error_message)
               Returns (temp_path, filename, None) on success
               Returns (None, None, error_message) on failure
    """
    # Verify video exists and belongs to user
    video_record = Video.query.filter_by(id=video_id, user_id=user_id).first()
    if not video_record:
        return None, None, "Video not found or access denied"
    
    # Verify video file exists on disk
    if not os.path.exists(video_record.filepath):
        return None, None, "Video file not found on disk"
    
    # Prevent path traversal
    video_path = os.path.abspath(video_record.filepath)
    if not video_path.startswith(os.path.abspath(os.getcwd())):
        return None, None, "Invalid file path"
    
    try:
        # Open original video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return None, None, "Failed to open video file"
        
        # Get video properties
        fps = video_record.fps
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = video_record.total_frames
        
        # Create temporary output file
        temp_fd, temp_path = tempfile.mkstemp(suffix='.mp4', prefix='annotated_')
        os.close(temp_fd)
        
        # Initialize video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_path, fourcc, fps, (width, height))
        
        if not out.isOpened():
            cap.release()
            return None, None, "Failed to initialize video writer"
        
        # Fetch all frames for this video
        frames = Frame.query.filter_by(video_id=video_id).order_by(Frame.frame_number).all()
        frame_map = {frame.frame_number: frame.id for frame in frames}
        
        # Fetch all annotations for this video
        annotations = Annotation.query.filter_by(
            video_id=video_id,
            user_id=user_id
        ).all()
        
        # Group annotations by frame_id
        annotations_by_frame = {}
        for ann in annotations:
            if ann.frame_id not in annotations_by_frame:
                annotations_by_frame[ann.frame_id] = []
            annotations_by_frame[ann.frame_id].append(ann.to_dict())
        
        # Process each frame
        frame_number = 1
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Get frame_id for current frame_number
            frame_id = frame_map.get(frame_number)
            
            # Draw annotations if they exist for this frame
            if frame_id and frame_id in annotations_by_frame:
                frame_annotations = annotations_by_frame[frame_id]
                frame = draw_annotations_with_colors(frame, frame_annotations)
            
            # Write frame to output video
            out.write(frame)
            
            frame_number += 1
        
        # Release resources
        cap.release()
        out.release()
        
        # Generate filename
        base_name = os.path.splitext(video_record.filename)[0]
        filename = f"{base_name}_annotated.mp4"
        
        return temp_path, filename, None
        
    except Exception as e:
        # Clean up temp file if it exists
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
        
        return None, None, f"Error generating annotated video: {str(e)}"
