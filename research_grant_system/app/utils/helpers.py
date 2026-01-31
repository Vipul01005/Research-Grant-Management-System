"""
Utility helper functions.
"""
import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app


def allowed_file(filename):
    """Check if the file extension is allowed."""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in current_app.config.get('ALLOWED_EXTENSIONS', set())


def save_uploaded_file(file, subfolder='documents'):
    """
    Save an uploaded file to the uploads folder.
    
    Args:
        file: The uploaded file object from request.files
        subfolder: Subfolder within uploads to save to
        
    Returns:
        tuple: (saved_filename, original_filename) or (None, None) if failed
    """
    if not file or not file.filename:
        return None, None
    
    if not allowed_file(file.filename):
        return None, None
    
    original_filename = secure_filename(file.filename)
    
    # Generate unique filename to prevent collisions
    ext = original_filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    
    # Create subfolder if it doesn't exist
    upload_folder = current_app.config['UPLOAD_FOLDER']
    target_folder = os.path.join(upload_folder, subfolder)
    
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    
    filepath = os.path.join(target_folder, unique_filename)
    file.save(filepath)
    
    return unique_filename, original_filename


def get_file_size(filepath):
    """Get file size in bytes."""
    if os.path.exists(filepath):
        return os.path.getsize(filepath)
    return 0


def delete_uploaded_file(filename, subfolder='documents'):
    """Delete an uploaded file."""
    if not filename:
        return False
    
    upload_folder = current_app.config['UPLOAD_FOLDER']
    filepath = os.path.join(upload_folder, subfolder, filename)
    
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False


def format_file_size(size_bytes):
    """Format file size to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"
