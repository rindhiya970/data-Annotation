"""User model for authentication and user management."""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db


class User(db.Model):
    """User model for storing user account information."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        """String representation of User object."""
        return f'<User {self.email}>'
    
    def set_password(self, password):
        """Hash and set the user's password.
        
        Args:
            password (str): Plain text password to hash and store
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches stored hash.
        
        Args:
            password (str): Plain text password to verify
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert User object to dictionary for JSON serialization.
        
        Returns:
            dict: User data without sensitive information
        """
        return {
            'id': self.id,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }