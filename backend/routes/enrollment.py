from flask import Blueprint, request, jsonify
import cv2
import numpy as np
import base64
from models import Student
from utils.face_utils import face_system
import logging

logger = logging.getLogger(__name__)
enrollment_bp = Blueprint('enrollment', __name__)

@enrollment_bp.route('/register', methods=['POST'])
def register_student():
    """Enroll a new student with face data"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['student_id', 'name', 'department', 'image']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if student already exists
        existing = Student.get_by_id(data['student_id'])
        if existing:
            return jsonify({'error': 'Student ID already exists'}), 400
        
        # Decode base64 image
        try:
            image_data = base64.b64decode(data['image'].split(',')[1])
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        except Exception as e:
            logger.error(f"Error decoding image: {e}")
            return jsonify({'error': 'Invalid image data'}), 400
        
        # Enroll face
        success, result = face_system.enroll_face(image_rgb, data['student_id'])
        
        if not success:
            return jsonify({'error': result}), 400
        
        # Save student to database
        student_id = Student.create(
            student_id=data['student_id'],
            name=data['name'],
            department=data['department'],
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            face_encoding_path=result
        )
        
        if not student_id:
            return jsonify({'error': 'Failed to save student'}), 500
        
        logger.info(f"Student enrolled successfully: {data['student_id']}")
        return jsonify({
            'message': 'Student enrolled successfully',
            'student_id': data['student_id']
        }), 201
        
    except Exception as e:
        logger.error(f"Error in registration: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@enrollment_bp.route('/students', methods=['GET'])
def get_students():
    """Get all enrolled students"""
    try:
        students = Student.get_all()
        return jsonify(students), 200
    except Exception as e:
        logger.error(f"Error fetching students: {e}")
        return jsonify({'error': 'Internal server error'}), 500