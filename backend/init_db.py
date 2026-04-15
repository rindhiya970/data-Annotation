"""Initialize database with tables and test user."""

import os
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.file import File
from app.models.video import Video
from app.models.frame import Frame
from app.models.annotation import Annotation


def init_database():
    """Create all database tables and add test user."""
    app = create_app('development')
    
    with app.app_context():
        # Delete existing database file
        db_path = os.path.join(app.root_path, 'app.db')
        if os.path.exists(db_path):
            print(f"Deleting existing database: {db_path}")
            os.remove(db_path)
        
        print("Creating all tables...")
        db.create_all()
        
        print("Creating test user with ID=1...")
        test_user = User(email='test@example.com')
        test_user.set_password('password123')
        
        db.session.add(test_user)
        db.session.commit()
        
        print(f"✅ Test user created with ID: {test_user.id}")
        print(f"✅ Email: test@example.com")
        print(f"✅ Password: password123")
        print(f"✅ Database file: {db_path}")
        print(f"✅ Database initialized successfully!")
        print(f"✅ You can now upload files!")


if __name__ == '__main__':
    init_database()
