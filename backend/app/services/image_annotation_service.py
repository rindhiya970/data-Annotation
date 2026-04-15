"""Image annotation service for handling image-specific annotation logic."""

from app.extensions import db
from app.models.annotation import Annotation
from app.models.file import File


def create_image_annotation(data, user_id):
    """
    Create annotation on an uploaded image.
    
    Args:
        data (dict): Annotation data containing file_id, label, x, y, width, height
        user_id (int): ID of the user creating the annotation
        
    Returns:
        Annotation: Created annotation object
        
    Raises:
        ValueError: If validation fails
    """
    # Validate required fields
    required_fields = ['file_id', 'label', 'x', 'y', 'width', 'height']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
    
    # Extract data
    file_id = data['file_id']
    label = data['label']
    
    # Validate label
    if not label or not label.strip():
        raise ValueError("Label cannot be empty")
    
    # Validate numeric fields
    try:
        x = float(data['x'])
        y = float(data['y'])
        width = float(data['width'])
        height = float(data['height'])
    except (TypeError, ValueError):
        raise ValueError("Coordinates and dimensions must be numeric values")
    
    # Validate x, y >= 0
    if x < 0:
        raise ValueError("X coordinate must be greater than or equal to 0")
    if y < 0:
        raise ValueError("Y coordinate must be greater than or equal to 0")
    
    # Validate width, height > 0
    if width <= 0:
        raise ValueError("Width must be greater than 0")
    if height <= 0:
        raise ValueError("Height must be greater than 0")
    
    # Fetch file and validate
    file_record = File.query.filter_by(id=file_id, user_id=user_id).first()
    if not file_record:
        raise ValueError("File not found or access denied")
    
    # Ensure file is an image (not video)
    if file_record.file_type != 'image':
        raise ValueError("File must be an image. Use video frame annotation for videos")
    
    # Create annotation record
    annotation = Annotation(
        user_id=user_id,
        file_id=file_id,
        video_id=None,
        frame_id=None,
        label=label.strip(),
        x=x,
        y=y,
        width=width,
        height=height
    )
    
    # Commit to database
    db.session.add(annotation)
    db.session.commit()
    
    return annotation


def get_image_annotations(file_id, user_id):
    """
    Get all annotations for a specific image file.
    
    Args:
        file_id (int): ID of the image file
        user_id (int): ID of the user (for authorization)
        
    Returns:
        list: List of annotation dictionaries
        
    Raises:
        ValueError: If file not found or access denied
    """
    # Verify file exists and belongs to user
    file_record = File.query.filter_by(id=file_id, user_id=user_id).first()
    if not file_record:
        raise ValueError("File not found or access denied")
    
    # Ensure file is an image
    if file_record.file_type != 'image':
        raise ValueError("File is not an image")
    
    # Fetch annotations for this image
    annotations = Annotation.query.filter_by(
        file_id=file_id,
        user_id=user_id
    ).order_by(Annotation.created_at).all()
    
    return [annotation.to_dict() for annotation in annotations]
