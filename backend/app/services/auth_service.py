"""Authentication service for user management operations."""

from app.extensions import db
from app.models.user import User


def create_user(email, password):
    """Create a new user account.
    
    Args:
        email (str): User's email address
        password (str): User's plain text password
        
    Returns:
        User or None: Created User object if successful, None if email already exists
    """
    # Check if user with email already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return None
    
    # Create new user
    user = User(email=email)
    user.set_password(password)
    
    # Save to database
    db.session.add(user)
    db.session.commit()
    
    return user