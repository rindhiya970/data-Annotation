"""Video model for storing video metadata."""

from datetime import datetime

from app.extensions import db


class Video(db.Model):
    """Video model for storing video processing metadata."""
    
    __tablename__ = 'videos'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'), nullable=False, unique=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    fps = db.Column(db.Float, nullable=False)
    total_frames = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('videos', lazy=True))
    file = db.relationship('File', backref=db.backref('video', uselist=False, lazy=True))
    frames = db.relationship('Frame', backref='video', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        """String representation of Video object."""
        return f'<Video {self.filename}>'
    
    def to_dict(self):
        """Convert Video object to dictionary for JSON serialization.
        
        Returns:
            dict: Video data for API responses
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'file_id': self.file_id,
            'filename': self.filename,
            'filepath': self.filepath,
            'fps': self.fps,
            'total_frames': self.total_frames,
            'duration': self.duration,
            'created_at': self.created_at.isoformat()
        }
