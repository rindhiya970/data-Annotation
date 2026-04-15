import os
from datetime import timedelta

# Get the base directory (where config.py is located)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration class for Flask application."""
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # Database - Default to SQLite for development
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(BASE_DIR, "app.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Application
    DEBUG = False
    TESTING = False
    
    # File Upload Configuration
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_FILE_SIZE', 100 * 1024 * 1024))  # 100MB default (for videos)
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'mp4', 'mov', 'avi'}
    
    # Video Processing Configuration
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'mov', 'avi'}
    MAX_VIDEO_DURATION = int(os.environ.get('MAX_VIDEO_DURATION', 300))  # 300 seconds (5 minutes) default
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration-specific setup."""
        # Ensure upload directory exists
        upload_path = app.config['UPLOAD_FOLDER']
        os.makedirs(upload_path, exist_ok=True)
        max_size_mb = app.config['MAX_CONTENT_LENGTH'] / (1024 * 1024)
        print(f"[CONFIG] Upload folder: {upload_path}")
        print(f"[CONFIG] Max file size: {max_size_mb:.0f}MB")
        print(f"[CONFIG] Database: {app.config['SQLALCHEMY_DATABASE_URI']}")


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    # Use SQLite for development
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        f'sqlite:///{os.path.join(BASE_DIR, "app.db")}'


class ProductionConfig(Config):
    """Production configuration."""
    
    # Use environment variables with safe fallbacks (will be validated in init_app)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'CHANGE-ME-IN-PRODUCTION'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'CHANGE-ME-IN-PRODUCTION'
    
    @staticmethod
    def init_app(app):
        """Initialize production application with validation."""
        # Call parent init
        Config.init_app(app)
        
        # Validate required environment variables at runtime (only when actually used)
        if app.config['SECRET_KEY'] == 'CHANGE-ME-IN-PRODUCTION':
            raise ValueError("No SECRET_KEY set for production environment. Please set the SECRET_KEY environment variable.")
        if app.config['JWT_SECRET_KEY'] == 'CHANGE-ME-IN-PRODUCTION':
            raise ValueError("No JWT_SECRET_KEY set for production environment. Please set the JWT_SECRET_KEY environment variable.")


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
