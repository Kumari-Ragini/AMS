import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # App Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    
    # Database
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database', 'attendance.db')
    
    # Face Recognition
    FACE_ENCODINGS_DIR = os.path.join(os.path.dirname(__file__), 'face_encodings')
    TOLERANCE = float(os.getenv('FACE_TOLERANCE', '0.6'))
    MODEL = os.getenv('FACE_MODEL', 'hog')  # hog or cnn (cnn is more accurate but slower)
    
    # AWS S3 (Optional)
    USE_S3 = os.getenv('USE_S3', 'False') == 'True'
    S3_BUCKET = os.getenv('S3_BUCKET', '')
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    
    # Security
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    
    # Attendance
    ATTENDANCE_WINDOW_HOURS = 24  # Mark attendance within 24 hours