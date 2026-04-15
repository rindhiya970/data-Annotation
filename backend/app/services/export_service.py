"""Export service for exporting annotations in various formats."""

import csv
import io

from app.models.annotation import Annotation
from app.models.video import Video


def export_annotations_json(user_id):
    """
    Export all annotations owned by the user as structured Python dict/list.
    
    Args:
        user_id (int): ID of the user whose annotations to export
        
    Returns:
        dict: Structured data containing user annotations with metadata
    """
    # Fetch all annotations owned by the user
    annotations = Annotation.query.filter_by(user_id=user_id).order_by(
        Annotation.video_id,
        Annotation.frame_id,
        Annotation.created_at
    ).all()
    
    # Build structured export data
    export_data = {
        'user_id': user_id,
        'total_annotations': len(annotations),
        'annotations': []
    }
    
    # Convert each annotation to dict with additional metadata
    for annotation in annotations:
        # Get video to retrieve file_id
        video = Video.query.filter_by(id=annotation.video_id).first()
        file_id = video.file_id if video else None
        
        annotation_data = {
            'id': annotation.id,
            'file_id': file_id,
            'video_id': annotation.video_id,
            'frame_id': annotation.frame_id,
            'label': annotation.label,
            'bounding_box': {
                'x': annotation.x,
                'y': annotation.y,
                'width': annotation.width,
                'height': annotation.height
            },
            'created_at': annotation.created_at.isoformat(),
            'updated_at': annotation.updated_at.isoformat()
        }
        
        export_data['annotations'].append(annotation_data)
    
    return export_data


def export_annotations_csv(user_id):
    """
    Export all annotations owned by the user as CSV string.
    
    Args:
        user_id (int): ID of the user whose annotations to export
        
    Returns:
        str: CSV string with headers and annotation data
    """
    # Fetch all annotations owned by the user
    annotations = Annotation.query.filter_by(user_id=user_id).order_by(
        Annotation.video_id,
        Annotation.frame_id,
        Annotation.created_at
    ).all()
    
    # Create CSV in memory
    output = io.StringIO()
    csv_writer = csv.writer(output)
    
    # Write headers
    headers = [
        'id',
        'file_id',
        'video_id',
        'frame_id',
        'label',
        'x',
        'y',
        'width',
        'height',
        'created_at'
    ]
    csv_writer.writerow(headers)
    
    # Write annotation rows
    for annotation in annotations:
        # Get video to retrieve file_id
        video = Video.query.filter_by(id=annotation.video_id).first()
        file_id = video.file_id if video else ''
        
        row = [
            annotation.id,
            file_id,
            annotation.video_id,
            annotation.frame_id,
            annotation.label,
            annotation.x,
            annotation.y,
            annotation.width,
            annotation.height,
            annotation.created_at.isoformat()
        ]
        csv_writer.writerow(row)
    
    # Get CSV string
    csv_string = output.getvalue()
    output.close()
    
    return csv_string


def export_annotations_by_video_json(video_id, user_id):
    """
    Export annotations for a specific video as structured Python dict/list.
    
    Args:
        video_id (int): ID of the video
        user_id (int): ID of the user (for authorization)
        
    Returns:
        dict: Structured data containing video annotations
        
    Raises:
        ValueError: If video not found or access denied
    """
    # Verify video exists and belongs to user
    video = Video.query.filter_by(id=video_id, user_id=user_id).first()
    if not video:
        raise ValueError("Video not found or access denied")
    
    # Fetch annotations for this video (only user's own annotations)
    annotations = Annotation.query.filter_by(
        video_id=video_id,
        user_id=user_id
    ).order_by(
        Annotation.frame_id,
        Annotation.created_at
    ).all()
    
    # Build structured export data
    export_data = {
        'user_id': user_id,
        'video_id': video_id,
        'file_id': video.file_id,
        'total_annotations': len(annotations),
        'annotations': []
    }
    
    # Convert each annotation to dict
    for annotation in annotations:
        annotation_data = {
            'id': annotation.id,
            'frame_id': annotation.frame_id,
            'label': annotation.label,
            'bounding_box': {
                'x': annotation.x,
                'y': annotation.y,
                'width': annotation.width,
                'height': annotation.height
            },
            'created_at': annotation.created_at.isoformat(),
            'updated_at': annotation.updated_at.isoformat()
        }
        
        export_data['annotations'].append(annotation_data)
    
    return export_data


def export_annotations_by_video_csv(video_id, user_id):
    """
    Export annotations for a specific video as CSV string.
    
    Args:
        video_id (int): ID of the video
        user_id (int): ID of the user (for authorization)
        
    Returns:
        str: CSV string with headers and annotation data
        
    Raises:
        ValueError: If video not found or access denied
    """
    # Verify video exists and belongs to user
    video = Video.query.filter_by(id=video_id, user_id=user_id).first()
    if not video:
        raise ValueError("Video not found or access denied")
    
    # Fetch annotations for this video (only user's own annotations)
    annotations = Annotation.query.filter_by(
        video_id=video_id,
        user_id=user_id
    ).order_by(
        Annotation.frame_id,
        Annotation.created_at
    ).all()
    
    # Create CSV in memory
    output = io.StringIO()
    csv_writer = csv.writer(output)
    
    # Write headers
    headers = [
        'id',
        'file_id',
        'video_id',
        'frame_id',
        'label',
        'x',
        'y',
        'width',
        'height',
        'created_at'
    ]
    csv_writer.writerow(headers)
    
    # Write annotation rows
    for annotation in annotations:
        row = [
            annotation.id,
            video.file_id,
            annotation.video_id,
            annotation.frame_id,
            annotation.label,
            annotation.x,
            annotation.y,
            annotation.width,
            annotation.height,
            annotation.created_at.isoformat()
        ]
        csv_writer.writerow(row)
    
    # Get CSV string
    csv_string = output.getvalue()
    output.close()
    
    return csv_string
