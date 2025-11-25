from flask import Blueprint, jsonify
from models import Attendance, Student
import logging

logger = logging.getLogger(__name__)
admin_bp = Blueprint('admin', __name__)

@attendance_bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    """Get complete dashboard data"""
    try:
        stats = Attendance.get_statistics()
        recent_attendance = Attendance.get_today_attendance()[:10]
        
        return jsonify({
            'statistics': stats,
            'recent_attendance': recent_attendance
        }), 200
    except Exception as e:
        logger.error(f"Error fetching dashboard data: {e}")
        return jsonify({'error': 'Internal server error'}), 500