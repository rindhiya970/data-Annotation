"""Video processing service using OpenCV."""

import os
import cv2


def validate_video_file(video_path, allowed_extensions=None):
    """
    Validate video file exists and has allowed extension.
    
    Args:
        video_path (str): Path to the video file
        allowed_extensions (set): Set of allowed extensions (e.g., {'mp4', 'avi'})
        
    Returns:
        tuple: (is_valid, error_message)
               Returns (True, None) if valid
               Returns (False, error_message) if invalid
    """
    # Check if file exists
    if not os.path.exists(video_path):
        return False, "Video file not found"
    
    # Check if it's a file (not a directory)
    if not os.path.isfile(video_path):
        return False, "Path is not a file"
    
    # Validate extension if provided
    if allowed_extensions:
        _, ext = os.path.splitext(video_path)
        ext = ext.lower().lstrip('.')
        
        if ext not in allowed_extensions:
            return False, f"Invalid video extension. Allowed: {', '.join(sorted(allowed_extensions))}"
    
    return True, None


def extract_frames_from_video(video_path, output_dir, max_duration=None):
    """
    Extract frames from a video file using OpenCV.
    
    Args:
        video_path (str): Path to the video file
        output_dir (str): Directory where frames will be saved
        max_duration (float, optional): Maximum allowed video duration in seconds
        
    Returns:
        tuple: (fps, total_frames, duration, error_message)
               Returns (fps, total_frames, duration, None) on success
               Returns (None, None, None, error_message) on failure
    """
    # Validate video path exists
    if not os.path.exists(video_path):
        return None, None, None, "Video file not found"
    
    # Validate it's a file
    if not os.path.isfile(video_path):
        return None, None, None, "Path is not a valid file"
    
    # Ensure output directory exists safely
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        # Verify directory was created and is writable
        if not os.path.isdir(output_dir):
            return None, None, None, "Failed to create output directory"
        
        if not os.access(output_dir, os.W_OK):
            return None, None, None, "Output directory is not writable"
            
    except Exception as e:
        return None, None, None, f"Failed to create output directory: {str(e)}"
    
    # Open video file
    video_capture = None
    try:
        video_capture = cv2.VideoCapture(video_path)
        
        if not video_capture.isOpened():
            return None, None, None, "Failed to open video file. File may be corrupted or unsupported format"
        
        # Get video properties
        fps = video_capture.get(cv2.CAP_PROP_FPS)
        total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Validate FPS
        if fps <= 0:
            return None, None, None, "Invalid FPS value. Video may be corrupted"
        
        # Validate frame count
        if total_frames <= 0:
            return None, None, None, "Invalid frame count. Video may be corrupted"
        
        # Calculate duration in seconds
        duration = total_frames / fps
        
        # Check duration limit if specified
        if max_duration is not None and duration > max_duration:
            return None, None, None, f"Video duration ({duration:.1f}s) exceeds maximum allowed duration ({max_duration}s)"
        
        # Extract frames
        frame_number = 0
        
        while True:
            success, frame = video_capture.read()
            
            if not success:
                break
            
            # Generate frame filename with zero-padding
            frame_filename = f"frame_{frame_number + 1:04d}.jpg"
            frame_path = os.path.join(output_dir, frame_filename)
            
            # Save frame as JPG
            success = cv2.imwrite(frame_path, frame)
            
            if not success:
                return None, None, None, f"Failed to save frame {frame_number + 1}"
            
            frame_number += 1
        
        # Verify all frames were extracted
        if frame_number != total_frames:
            total_frames = frame_number
        
        # Verify at least some frames were extracted
        if frame_number == 0:
            return None, None, None, "No frames were extracted from video"
        
        return fps, total_frames, duration, None
        
    except Exception as e:
        return None, None, None, f"Error processing video: {str(e)}"
        
    finally:
        # Release video capture object
        if video_capture is not None:
            video_capture.release()


def get_video_metadata(video_path):
    """
    Get metadata from a video file without extracting frames.
    
    Args:
        video_path (str): Path to the video file
        
    Returns:
        tuple: (fps, total_frames, duration, error_message)
               Returns (fps, total_frames, duration, None) on success
               Returns (None, None, None, error_message) on failure
    """
    if not os.path.exists(video_path):
        return None, None, None, "Video file not found"
    
    video_capture = None
    try:
        video_capture = cv2.VideoCapture(video_path)
        
        if not video_capture.isOpened():
            return None, None, None, "Failed to open video file"
        
        # Get video properties
        fps = video_capture.get(cv2.CAP_PROP_FPS)
        total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if fps <= 0:
            return None, None, None, "Invalid FPS value"
        
        duration = total_frames / fps
        
        return fps, total_frames, duration, None
        
    except Exception as e:
        return None, None, None, f"Error reading video metadata: {str(e)}"
        
    finally:
        if video_capture is not None:
            video_capture.release()
