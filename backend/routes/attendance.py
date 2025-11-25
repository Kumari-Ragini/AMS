from flask import Blueprint, request, jsonify
import cv2
import numpy as np
import base64
from models import Student, Attendance
from utils.face_utils import face_system
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/mark', methods=['POST'])
def mark_attendance():
    """Mark attendance by scanning face"""
    try:
        data = request.get_json()
        
        if 'image' not in data:
            return jsonify({'error': 'No image provided'}), 400
        
        # Decode image
        try:
            image_data = base64.b64decode(data['image'].split(',')[1])
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        except Exception as e:
            logger.error(f"Error decoding image: {e}")
            return jsonify({'error': 'Invalid image data'}), 400
        
        # Recognize face
        student_id, confidence, message = face_system.recognize_face(image_rgb)
        
        if student_id is None:
            return jsonify({'error': message, 'recognized': False}), 200
        
        # Get student details
        student = Student.get_by_id(student_id)
        if not student:
            return jsonify({'error': 'Student not found in database'}), 404
        
        # Mark attendance
        success = Attendance.mark_present(student_id, confidence)
        
        if not success:
            return jsonify({'error': 'Failed to mark attendance'}), 500
        
        logger.info(f"Attendance marked for {student_id}")
        return jsonify({
            'recognized': True,
            'student': student,
            'confidence': round(confidence * 100, 2),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'message': 'Attendance marked successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error marking attendance: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@attendance_bp.route('/today', methods=['GET'])
def get_today_attendance():
    """Get today's attendance records"""
    try:
        records = Attendance.get_today_attendance()
        return jsonify(records), 200
    except Exception as e:
        logger.error(f"Error fetching attendance: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@attendance_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """Get attendance statistics"""
    try:
        stats = Attendance.get_statistics()
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Error fetching statistics: {e}")
        return jsonify({'error': 'Internal server error'}), 500