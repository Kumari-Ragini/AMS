from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os
import logging
from config import Config
from models import init_db
from routes.auth import auth_bp
from routes.enrollment import enrollment_bp
from routes.attendance import attendance_bp
from routes.admin import admin_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__, 
                static_folder='../frontend',
                static_url_path='')
    
    # Load configuration
    app.config.from_object(Config)
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Create necessary directories
    os.makedirs(Config.FACE_ENCODINGS_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
    
    # Initialize database
    init_db()
    logger.info("Database initialized successfully")
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(enrollment_bp, url_prefix='/api/enroll')
    app.register_blueprint(attendance_bp, url_prefix='/api/attendance')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    # Serve frontend
    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'login.html')
    
    @app.route('/<path:path>')
    def serve_static(path):
        return send_from_directory(app.static_folder, path)
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'Smart Attendance System is running'
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(e):
        logger.error(f"Internal server error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=Config.DEBUG)