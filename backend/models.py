import sqlite3
from datetime import datetime
from config import Config
import logging

logger = logging.getLogger(__name__)

def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table for authentication
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'admin',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            department TEXT,
            email TEXT,
            phone TEXT,
            face_encoding_path TEXT,
            enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Attendance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            check_in_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date TEXT NOT NULL,
            status TEXT DEFAULT 'Present',
            confidence REAL,
            FOREIGN KEY (student_id) REFERENCES students(student_id),
            UNIQUE(student_id, date)
        )
    ''')
    
    # Insert default admin user (password: admin123)
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO users (username, password, role)
            VALUES ('admin', 'admin123', 'admin')
        ''')
    except sqlite3.IntegrityError:
        pass
    
    conn.commit()
    conn.close()
    logger.info("Database tables created successfully")

class Student:
    @staticmethod
    def create(student_id, name, department, email, phone, face_encoding_path):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO students (student_id, name, department, email, phone, face_encoding_path)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (student_id, name, department, email, phone, face_encoding_path))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            logger.error(f"Error creating student: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_all():
        conn = get_db_connection()
        students = conn.execute('SELECT * FROM students WHERE is_active = 1').fetchall()
        conn.close()
        return [dict(s) for s in students]
    
    @staticmethod
    def get_by_id(student_id):
        conn = get_db_connection()
        student = conn.execute('SELECT * FROM students WHERE student_id = ?', (student_id,)).fetchone()
        conn.close()
        return dict(student) if student else None

class Attendance:
    @staticmethod
    def mark_present(student_id, confidence, date=None):
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO attendance (student_id, date, confidence, status)
                VALUES (?, ?, ?, 'Present')
                ON CONFLICT(student_id, date) DO UPDATE SET
                    check_in_time = CURRENT_TIMESTAMP,
                    confidence = excluded.confidence
            ''', (student_id, date, confidence))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error marking attendance: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def get_today_attendance():
        today = datetime.now().strftime('%Y-%m-%d')
        conn = get_db_connection()
        records = conn.execute('''
            SELECT a.*, s.name, s.department
            FROM attendance a
            JOIN students s ON a.student_id = s.student_id
            WHERE a.date = ?
            ORDER BY a.check_in_time DESC
        ''', (today,)).fetchall()
        conn.close()
        return [dict(r) for r in records]
    
    @staticmethod
    def get_statistics():
        today = datetime.now().strftime('%Y-%m-%d')
        conn = get_db_connection()
        
        total_students = conn.execute('SELECT COUNT(*) as count FROM students WHERE is_active = 1').fetchone()['count']
        present_today = conn.execute('SELECT COUNT(*) as count FROM attendance WHERE date = ?', (today,)).fetchone()['count']
        
        conn.close()
        
        absent = total_students - present_today
        rate = round((present_today / total_students * 100), 2) if total_students > 0 else 0
        
        return {
            'total_students': total_students,
            'present': present_today,
            'absent': absent,
            'attendance_rate': rate
        }