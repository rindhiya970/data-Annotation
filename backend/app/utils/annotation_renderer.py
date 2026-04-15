"""Utility functions for rendering annotations on images and videos using OpenCV."""

import cv2
import numpy as np


def draw_annotation(image, annotation, color=(0, 255, 0), thickness=2, font_scale=0.6):
    """
    Draw a single bounding box annotation on an image.
    
    Args:
        image (numpy.ndarray): OpenCV image array
        annotation (dict): Annotation data with x, y, width, height, label
        color (tuple): BGR color for bounding box (default: green)
        thickness (int): Line thickness for bounding box
        font_scale (float): Font scale for label text
        
    Returns:
        numpy.ndarray: Image with annotation drawn
    """
    # Extract coordinates
    x = int(annotation['x'])
    y = int(annotation['y'])
    width = int(annotation['width'])
    height = int(annotation['height'])
    label = annotation['label']
    
    # Draw bounding box
    cv2.rectangle(image, (x, y), (x + width, y + height), color, thickness)
    
    # Prepare label text
    label_text = f"{label}"
    
    # Get text size for background
    (text_width, text_height), baseline = cv2.getTextSize(
        label_text, 
        cv2.FONT_HERSHEY_SIMPLEX, 
        font_scale, 
        thickness=1
    )
    
    # Draw label background
    cv2.rectangle(
        image,
        (x, y - text_height - baseline - 5),
        (x + text_width + 5, y),
        color,
        -1  # Filled rectangle
    )
    
    # Draw label text
    cv2.putText(
        image,
        label_text,
        (x + 2, y - baseline - 2),
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        (255, 255, 255),  # White text
        thickness=1,
        lineType=cv2.LINE_AA
    )
    
    return image


def draw_annotations(image, annotations, color=(0, 255, 0), thickness=2, font_scale=0.6):
    """
    Draw multiple annotations on an image.
    
    Args:
        image (numpy.ndarray): OpenCV image array
        annotations (list): List of annotation dictionaries
        color (tuple): BGR color for bounding boxes
        thickness (int): Line thickness
        font_scale (float): Font scale for labels
        
    Returns:
        numpy.ndarray: Image with all annotations drawn
    """
    # Create a copy to avoid modifying original
    annotated_image = image.copy()
    
    # Draw each annotation
    for annotation in annotations:
        annotated_image = draw_annotation(
            annotated_image, 
            annotation, 
            color, 
            thickness, 
            font_scale
        )
    
    return annotated_image


def get_color_for_label(label, seed=None):
    """
    Generate a consistent color for a given label.
    
    Args:
        label (str): Label text
        seed (int, optional): Random seed for reproducibility
        
    Returns:
        tuple: BGR color tuple
    """
    # Use label hash as seed for consistent colors
    if seed is None:
        seed = hash(label) % 256
    
    np.random.seed(seed)
    color = tuple(np.random.randint(50, 255, 3).tolist())
    
    return color


def draw_annotations_with_colors(image, annotations, thickness=2, font_scale=0.6):
    """
    Draw annotations with different colors per label.
    
    Args:
        image (numpy.ndarray): OpenCV image array
        annotations (list): List of annotation dictionaries
        thickness (int): Line thickness
        font_scale (float): Font scale
        
    Returns:
        numpy.ndarray: Image with colored annotations
    """
    annotated_image = image.copy()
    
    for annotation in annotations:
        color = get_color_for_label(annotation['label'])
        annotated_image = draw_annotation(
            annotated_image,
            annotation,
            color,
            thickness,
            font_scale
        )
    
    return annotated_image
