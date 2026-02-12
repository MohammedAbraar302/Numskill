from flask import Flask, jsonify, send_file
import logging
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import config
import os

# Import blueprints
from auth import auth_bp
from assessment import assessment_bp
from models import db

def create_app(config_name='development'):
    """Application factory"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    JWTManager(app)
    
    # Add JWT error handlers
    jwt = JWTManager(app)

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token has expired'}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': 'Invalid token'}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'error': 'Authorization header is missing'}), 401

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(assessment_bp)
    
    @app.route('/api/health', methods=['GET'])
    def health():
        """Health check endpoint"""
        return jsonify({'status': 'healthy'}), 200
    
    @app.route('/', methods=['GET'])
    def serve_html():
        """Serve the main HTML file"""
        return send_file('index.html')  # Or your HTML filename
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({'error': 'Server error'}), 500
    
    @app.errorhandler(422)
    def handle_unprocessable_entity(e):
        return jsonify({'error': 'Missing or invalid Authorization header'}), 401
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    config_name = os.getenv('FLASK_ENV', 'development')
    app = create_app(config_name)
    # Configure basic logging and run without the reloader to avoid multi-process issues
    logging.basicConfig(level=logging.DEBUG)
    app.run(debug=False, host='0.0.0.0', port=5000)
