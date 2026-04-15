"""Frame model for storing video frame metadata."""

from datetime import datetime

from app.extensions import db


class Frame(db.Model):
    """Frame model for storing extracted video frame metadata."""
    
    __tablename__ = 'frames'
    
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    frame_number = db.Column(db.Integer, nullable=False)
    frame_path = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        """String representation of Frame object."""
        return f'<Frame {self.frame_number} of Video {self.video_id}>'
    
    def to_dict(self):
        """Convert Frame object to dictionary for JSON serialization.
        
        Returns:
            dict: Frame data for API responses
        """
        return {
            'id': self.id,
            'video_id': self.video_id,
            'frame_number': self.frame_number,
            'frame_path': self.frame_path,
            'created_at': self.created_at.isoformat()
        }
