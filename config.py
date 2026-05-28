# Chứa các tham số cấu hình (độ nhạy, ngưỡng click, kích thước màn hình)

# Chứa các tham số cấu hình (độ nhạy, ngưỡng click, kích thước màn hình)

# Chứa các tham số cấu hình (độ nhạy, ngưỡng click, kích thước màn hình)

import pyautogui

# Kích thước màn hình hệ điều hành
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

# Cấu hình Camera
CAM_WIDTH, CAM_HEIGHT = 640, 480

# --- LỌC NHIỄU VÀ LÀM MỊN NÂNG CAO (ONE EURO & ADAPTIVE LERP) ---
FILTER_FREQ = 30.0  
FILTER_MIN_CUTOFF = 0.5  
FILTER_BETA = 0.05  
FILTER_D_CUTOFF = 1.0  

# Ngưỡng Alpha nền cho LERP thích ứng (Sẽ tự co giãn động trong code)
MOUSE_LERP_BASE_ALPHA = 0.15  

# --- GIỚI HẠN TĂNG TỐC CHUỘT (ACCELERATION) ---
MOUSE_ACCEL_FACTOR = 1.6  

# --- CẤU HÌNH GESTURE TIMING (GIÂY) ---
CLICK_MAX_DURATION = 0.5  # Há mồm dưới 0.5s => Click đơn
DRAG_MIN_DURATION = 1.5   # Giữ há mồm trên 1.5s => Kéo thả (Drag & Drop)

# --- THỜI GIAN QUẢN LÝ TỰ ĐỘNG KHÓA/MỞ ---
FACE_ABSENCE_DURATION = 2.0  # Mất người dùng 2s tự động Pause
HOT_CORNER_DURATION = 3.0    # Giữ góc trên bên trái 3s để Pause
RESUME_MOUTH_DURATION = 3.0  # Há mồm 3s khi đang khóa để Resume

# --- VÙNG TƯƠNG TÁC TRUNG TÂM (SẼ ĐƯỢC CẬP NHẬT ĐỘNG BỞI CALIBRATION) ---
FRAME_INNER_X1 = 0.35
FRAME_INNER_X2 = 0.65
FRAME_INNER_Y1 = 0.35
FRAME_INNER_Y2 = 0.65

# --- BIẾN TOÀN CỤC ĐƯỢC DÙNG CHO CALIBRATION ĐỘNG ---
DYNAMIC_MOUTH_THRESH = 0.06  
CALIBRATED_CENTER_X = 0.5
CALIBRATED_CENTER_Y = 0.5