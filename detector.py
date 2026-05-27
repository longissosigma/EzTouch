# Wrapper xử lý MediaPipe Face Mesh để trích xuất tọa độ mũi và miệng

import cv2
import mediapipe as mp
import math

class FaceDetector:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )

    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return self.face_mesh.process(rgb_frame)

    def get_nose_position(self, results):
        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]
            nose_tip = face_landmarks.landmark[1]
            return nose_tip.x, nose_tip.y
        return None, None

    def get_mouth_open_ratio(self, results):
        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]
            top_lip = face_landmarks.landmark[13]
            bottom_lip = face_landmarks.landmark[14]
            mouth_dist = math.hypot(top_lip.x - bottom_lip.x, top_lip.y - bottom_lip.y)
            
            left_eye = face_landmarks.landmark[33]
            right_eye = face_landmarks.landmark[263]
            eye_dist = math.hypot(left_eye.x - right_eye.x, left_eye.y - right_eye.y)
            
            if eye_dist == 0: return 0
            return mouth_dist / eye_dist
        return 0

    def get_head_roll(self, results):
        """Tính góc nghiêng đầu (Roll) dựa trên độ lệch tọa độ 2 mắt."""
        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]
            left_eye = face_landmarks.landmark[33]
            right_eye = face_landmarks.landmark[263]
            
            # Tính toán góc bằng hàm atan2
            delta_x = right_eye.x - left_eye.x
            delta_y = right_eye.y - left_eye.y
            angle_rad = math.atan2(delta_y, delta_x)
            angle_deg = math.degrees(angle_rad)
            
            return angle_deg
        return 0.0