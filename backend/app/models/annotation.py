"""Annotation model for storing bounding box annotations."""

from datetime import datetime

from app.extensions import db


class Annotation(db.Model):
    """Annotation model for storing bounding box annotations on images and video frames."""
    
    __tablename__ = 'annotations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'), nullable=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=True)
    frame_id = db.Column(db.Integer, db.ForeignKey('frames.id'), nullable=True)
    label = db.Column(db.String(100), nullable=False)
    x = db.Column(db.Float, nullable=False)
    y = db.Column(db.Float, nullable=False)
    width = db.Column(db.Float, nullable=False)
    height = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('annotations', lazy=True))
    file = db.relationship('File', backref=db.backref('annotations', lazy=True))
    video = db.relationship('Video', backref=db.backref('annotations', lazy=True))
    frame = db.relationship('Frame', backref=db.backref('annotations', lazy=True))
    
    def __repr__(self):
        """String representation of Annotation object."""
        if self.file_id:
            return f'<Annotation {self.id} - {self.label} on File {self.file_id}>'
        return f'<Annotation {self.id} - {self.label} on Frame {self.frame_id}>'
    
    def to_dict(self):
        """Convert Annotation object to dictionary for JSON serialization.
        
        Returns:
            dict: Annotation data for API responses
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'file_id': self.file_id,
            'video_id': self.video_id,
            'frame_id': self.frame_id,
            'label': self.label,
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
