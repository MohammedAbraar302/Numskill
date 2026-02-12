from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.exceptions import UnprocessableEntity
from models import db, User
from datetime import datetime
import logging
import jwt as pyjwt

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if user already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 409
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 409
        
        # Create new user
        user = User(username=data['username'], email=data['email'])
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Create access token (use string identity to avoid subject-type issues)
        access_token = create_access_token(identity=str(user.id))
        
        logger.info(f"User registered: {user.username}")
        
        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token,
            'user': user.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user with username/email and password"""
    try:
        data = request.get_json()
        
        if not data or not data.get('password'):
            return jsonify({'error': 'Missing username/email and password'}), 400
        
        # Accept either username or email
        user = User.query.filter(
            (User.username == data.get('username')) | 
            (User.email == data.get('email'))
        ).first()
        
        if not user or not user.check_password(data['password']):
            logger.warning(f"Failed login attempt for: {data.get('username') or data.get('email')}")
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create access token (use string identity to avoid subject-type issues)
        access_token = create_access_token(identity=str(user.id))

        # Log token info for debugging (remove in production)
        try:
            logger.debug(f"Generated token for user {user.username}: {access_token}")
            # Try to decode to ensure signature correctness
            payload = pyjwt.decode(access_token, current_app.config.get('JWT_SECRET_KEY'), algorithms=['HS256'])
            logger.debug(f"Token payload: {payload}")
        except Exception as e:
            logger.error(f"Token decode error after creation: {e}")

        logger.info(f"User logged in: {user.username}")

        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """Verify JWT token and return user info"""
    try:
        # Debug: log the Authorization header and attempt manual decode
        auth_header = request.headers.get('Authorization')
        logger.debug(f"Authorization header received: {auth_header}")
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ', 1)[1]
            try:
                decoded = pyjwt.decode(token, current_app.config.get('JWT_SECRET_KEY'), algorithms=['HS256'])
                logger.debug(f"Manual JWT decode success: {decoded}")
            except Exception as e:
                logger.error(f"Manual JWT decode failed: {e}")

        raw_id = get_jwt_identity()
        logger.debug(f"Verifying token for raw identity: {raw_id}")
        try:
            user_id = int(raw_id)
        except Exception:
            user_id = raw_id
        
        user = User.query.get(user_id)
        
        if not user:
            logger.warning(f"User not found for id: {user_id}")
            return jsonify({'error': 'User not found'}), 404
        
        logger.debug(f"Token verified for: {user.username}")
        return jsonify({'user': user.to_dict()}), 200
    
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        raw_id = get_jwt_identity()
        try:
            user_id = int(raw_id)
        except Exception:
            user_id = raw_id
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify(user.to_dict()), 200
    
    except Exception as e:
        logger.error(f"Get profile error: {str(e)}")
        return jsonify({'error': str(e)}), 500
