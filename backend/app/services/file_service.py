"""File upload service for handling file operations."""

import os
import uuid
import traceback
from werkzeug.utils import secure_filename
from flask import current_app
from app.extensions import db
from app.models.file import File


def save_uploaded_file(file_storage, user_id):
    """Save uploaded file and create database record."""
    try:
        print(f"[FILE_SERVICE] Starting upload for user_id={user_id}")
        
        if not file_storage or not file_storage.filename:
            return None, "No file provided"

        original_filename = file_storage.filename.strip()
        print(f"[FILE_SERVICE] Original filename: {original_filename}")
        
        if not original_filename:
            return None, "Filename cannot be empty"

        if '.' not in original_filename:
            return None, "File must have an extension"
        
        extension = original_filename.rsplit('.', 1)[1].lower()
        allowed = current_app.config.get('ALLOWED_EXTENSIONS', set())
        print(f"[FILE_SERVICE] Extension: {extension}, Allowed: {allowed}")
        
        if extension not in allowed:
            return None, f"File type not allowed. Allowed: {', '.join(sorted(allowed))}"

        # Determine file type
        video_extensions = {'mp4', 'mov', 'avi'}
        image_extensions = {'jpg', 'jpeg', 'png'}
        
        if extension in image_extensions:
            file_type = 'image'
        elif extension in video_extensions:
            file_type = 'video'
        else:
            file_type = 'unknown'
        
        print(f"[FILE_SERVICE] File type: {file_type}")

        # Generate secure filename
        unique_id = uuid.uuid4().hex[:12]
        safe_name = secure_filename(original_filename.rsplit('.', 1)[0])
        stored_filename = f"{unique_id}_{safe_name}.{extension}"
        print(f"[FILE_SERVICE] Stored filename: {stored_filename}")
        
        # Get upload folder
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        print(f"[FILE_SERVICE] Upload folder: {upload_folder}")
        
        # Full file path
        file_path = os.path.join(upload_folder, stored_filename)
        print(f"[FILE_SERVICE] Full path: {file_path}")

        # Save file to disk
        file_storage.save(file_path)
        print(f"[FILE_SERVICE] File saved to disk")

        # Create database record
        file_record = File(
            original_filename=original_filename,
            stored_filename=stored_filename,
            file_path=file_path,
            file_type=file_type,
            user_id=user_id
        )

        db.session.add(file_record)
        db.session.commit()
        print(f"[FILE_SERVICE] DB record committed with ID: {file_record.id}")

        return file_record, None

    except Exception as e:
        print(f"[FILE_SERVICE ERROR]")
        print(traceback.format_exc())
        db.session.rollback()
        
        if 'file_path' in locals() and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass

        return None, f"Error saving file: {str(e)}"


def get_user_files(user_id, file_type=None):
    """Fetch all files uploaded by a user."""
    query = File.query.filter_by(user_id=user_id)
    if file_type:
        query = query.filter_by(file_type=file_type)
    return query.order_by(File.created_at.desc()).all()


def get_file_by_id(file_id, user_id):
    """Get a specific file by ID for a user."""
    return File.query.filter_by(id=file_id, user_id=user_id).first()
