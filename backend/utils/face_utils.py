import face_recognition
import cv2
import numpy as np
import pickle
import os
from config import Config
import logging

logger = logging.getLogger(__name__)

class FaceRecognitionSystem:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_ids = []
        self.tolerance = Config.TOLERANCE
        self.model = Config.MODEL
    
    def load_known_faces(self):
        """Load all enrolled face encodings"""
        self.known_face_encodings = []
        self.known_face_ids = []
        
        if not os.path.exists(Config.FACE_ENCODINGS_DIR):
            return
        
        for filename in os.listdir(Config.FACE_ENCODINGS_DIR):
            if filename.endswith('.pkl'):
                filepath = os.path.join(Config.FACE_ENCODINGS_DIR, filename)
                try:
                    with open(filepath, 'rb') as f:
                        data = pickle.load(f)
                        self.known_face_encodings.append(data['encoding'])
                        self.known_face_ids.append(data['student_id'])
                except Exception as e:
                    logger.error(f"Error loading face encoding {filename}: {e}")
        
        logger.info(f"Loaded {len(self.known_face_encodings)} face encodings")
    
    def enroll_face(self, image_data, student_id):
        """
        Enroll a new face
        image_data: numpy array of image
        student_id: unique identifier for student
        """
        try:
            # Detect faces in the image
            face_locations = face_recognition.face_locations(image_data, model=self.model)
            
            if len(face_locations) == 0:
                return False, "No face detected in the image"
            
            if len(face_locations) > 1:
                return False, "Multiple faces detected. Please ensure only one face is visible"
            
            # Get face encoding
            face_encodings = face_recognition.face_encodings(image_data, face_locations)
            
            if len(face_encodings) == 0:
                return False, "Could not generate face encoding"
            
            encoding = face_encodings[0]
            
            # Save encoding
            encoding_path = os.path.join(Config.FACE_ENCODINGS_DIR, f"{student_id}.pkl")
            with open(encoding_path, 'wb') as f:
                pickle.dump({
                    'student_id': student_id,
                    'encoding': encoding
                }, f)
            
            logger.info(f"Face enrolled successfully for student {student_id}")
            return True, encoding_path
            
        except Exception as e:
            logger.error(f"Error enrolling face: {e}")
            return False, str(e)
    
    def recognize_face(self, image_data):
        """
        Recognize a face from image
        Returns: (student_id, confidence) or (None, 0)
        """
        try:
            # Load known faces if not loaded
            if len(self.known_face_encodings) == 0:
                self.load_known_faces()
            
            if len(self.known_face_encodings) == 0:
                return None, 0, "No enrolled faces found"
            
            # Detect faces
            face_locations = face_recognition.face_locations(image_data, model=self.model)
            
            if len(face_locations) == 0:
                return None, 0, "No face detected"
            
            # Get encodings
            face_encodings = face_recognition.face_encodings(image_data, face_locations)
            
            if len(face_encodings) == 0:
                return None, 0, "Could not generate face encoding"
            
            # Compare with known faces
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(
                    self.known_face_encodings, 
                    face_encoding, 
                    tolerance=self.tolerance
                )
                face_distances = face_recognition.face_distance(
                    self.known_face_encodings, 
                    face_encoding
                )
                
                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)
                    
                    if matches[best_match_index]:
                        student_id = self.known_face_ids[best_match_index]
                        confidence = float(1 - face_distances[best_match_index])
                        
                        logger.info(f"Face recognized: {student_id} with confidence {confidence}")
                        return student_id, confidence, "Success"
            
            return None, 0, "Face not recognized"
            
        except Exception as e:
            logger.error(f"Error recognizing face: {e}")
            return None, 0, str(e)
    
    def detect_face_in_frame(self, image_data):
        """Simple face detection for live video"""
        try:
            face_locations = face_recognition.face_locations(image_data, model='hog')
            return len(face_locations) > 0, face_locations
        except Exception as e:
            logger.error(f"Error detecting face: {e}")
            return False, []

# Global instance
face_system = FaceRecognitionSystem()