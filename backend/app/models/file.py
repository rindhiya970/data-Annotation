"""File model for storing uploaded file information."""

from datetime import datetime
from app.extensions import db


class File(db.Model):
    """File model for storing file metadata and references."""
    
    __tablename__ = 'files'
    
    id = db.Column(db.Integer, primary_key=True)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    user = db.relationship('User', backref=db.backref('files', lazy=True))
    
    def __repr__(self):
        return f'<File {self.original_filename}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'original_filename': self.original_filename,
            'stored_filename': self.stored_filename,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat()
        }
