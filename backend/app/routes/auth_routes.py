"""Authentication routes for user signup and login."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

from app.models.user import User
from app.services.auth_service import create_user

# Create Blueprint (no url_prefix here, it's added during registration)
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Register a new user account.
    
    Expected JSON payload:
        email (str): User's email address
        password (str): User's password
        
    Returns:
        JSON response with standardized format
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({
                'success': False,
                'message': 'Email and password are required',
                'data': None
            }), 400
        
        email = data['email'].strip().lower()
        password = data['password']
        
        # Validate email format (basic validation)
        if '@' not in email or len(email) < 5:
            return jsonify({
                'success': False,
                'message': 'Invalid email format',
                'data': None
            }), 400
        
        # Validate password length
        if len(password) < 6:
            return jsonify({
                'success': False,
                'message': 'Password must be at least 6 characters long',
                'data': None
            }), 400
        
        # Create user
        user = create_user(email, password)
        
        if user is None:
            return jsonify({
                'success': False,
                'message': 'User with this email already exists',
                'data': None
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'User created successfully',
            'data': {
                'user': user.to_dict()
            }
        }), 201
        
    except Exception as e:
        # Log the actual error for debugging
        import traceback
        print(f"❌ Signup error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'data': None
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return JWT access token.
    
    Expected JSON payload:
        email (str): User's email address
        password (str): User's password
        
    Returns:
        JSON response with standardized format
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({
                'success': False,
                'message': 'Email and password are required',
                'data': None
            }), 400
        
        email = data['email'].strip().lower()
        password = data['password']
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        # Validate credentials
        if not user or not user.check_password(password):
            return jsonify({
                'success': False,
                'message': 'Invalid email or password',
                'data': None
            }), 401
        
        # Generate JWT access token
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'data': {
                'access_token': access_token,
                'user': user.to_dict()
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'data': None
        }), 500