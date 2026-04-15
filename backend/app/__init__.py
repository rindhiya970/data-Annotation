"""Flask application factory."""

import os
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS

from app.config import config
from app.extensions import db, jwt


def create_app(config_name='default'):
    """Create and configure Flask application.
    
    Args:
        config_name (str): Configuration name to use
        
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    
    # Configure CORS for development - MUST be after JWT init
    CORS(app, 
         origins=["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173", "http://127.0.0.1:5174"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
         supports_credentials=True,
         expose_headers=["Content-Type", "Authorization"],
         max_age=3600)
    
    # Add OPTIONS handler for all routes BEFORE JWT check
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = app.make_default_options_response()
            return response

    # ✅ IMPORTANT: Serve uploaded files publicly
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        """Serve uploaded files from the uploads directory."""
        # Get absolute path to uploads folder
        upload_folder = os.path.join(os.getcwd(), app.config.get('UPLOAD_FOLDER', 'uploads'))
        print(f"[UPLOADS] Serving file: {filename} from {upload_folder}")
        return send_from_directory(upload_folder, filename)

    # Register blueprints with /api prefix
    from app.routes.auth_routes import auth_bp
    from app.routes.file_routes import file_bp
    from app.routes.video_routes import video_bp
    from app.routes.annotation_routes import annotation_bp
    from app.routes.export_routes import export_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(file_bp, url_prefix='/api/files')
    app.register_blueprint(video_bp, url_prefix='/api/videos')
    app.register_blueprint(annotation_bp, url_prefix='/api/annotations')
    app.register_blueprint(export_bp, url_prefix='/api/export')
    
    # Add a simple test endpoint
    @app.route('/api/test', methods=['GET', 'POST'])
    def test_endpoint():
        import sys
        print("\n" + "="*60, file=sys.stderr, flush=True)
        print("[TEST] Test endpoint called!", file=sys.stderr, flush=True)
        print(f"[TEST] Method: {app.current_request.method if hasattr(app, 'current_request') else 'unknown'}", file=sys.stderr, flush=True)
        print("="*60 + "\n", file=sys.stderr, flush=True)
        return jsonify({
            'success': True,
            'message': 'Test endpoint working!',
            'data': {'test': 'ok'}
        }), 200
    
    # Add a MINIMAL upload test endpoint
    @app.route('/api/test-upload', methods=['POST', 'OPTIONS'])
    def test_upload():
        from flask import request
        import sys
        
        if request.method == 'OPTIONS':
            return '', 200
            
        print("\n" + "="*60, file=sys.stderr, flush=True)
        print("[TEST-UPLOAD] Request received!", file=sys.stderr, flush=True)
        print(f"[TEST-UPLOAD] Method: {request.method}", file=sys.stderr, flush=True)
        print(f"[TEST-UPLOAD] Content-Type: {request.content_type}", file=sys.stderr, flush=True)
        print(f"[TEST-UPLOAD] Content-Length: {request.content_length}", file=sys.stderr, flush=True)
        print(f"[TEST-UPLOAD] Files: {request.files}", file=sys.stderr, flush=True)
        print(f"[TEST-UPLOAD] Files keys: {list(request.files.keys())}", file=sys.stderr, flush=True)
        print(f"[TEST-UPLOAD] Form: {request.form}", file=sys.stderr, flush=True)
        print("="*60 + "\n", file=sys.stderr, flush=True)
        
        if 'file' in request.files:
            file = request.files['file']
            return jsonify({
                'success': True,
                'message': 'File received!',
                'data': {
                    'filename': file.filename,
                    'content_type': file.content_type
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'No file in request',
                'data': {
                    'files_keys': list(request.files.keys()),
                    'form_keys': list(request.form.keys())
                }
            }), 400
    
    # Register error handlers
    register_error_handlers(app)
    
    return app


def register_error_handlers(app):
    """Register global error handlers for consistent error responses."""
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'message': 'Resource not found',
            'data': None
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'data': None
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.error(f'Unhandled exception: {str(error)}')
        
        return jsonify({
            'success': False,
            'message': 'An unexpected error occurred',
            'data': None
        }), 500