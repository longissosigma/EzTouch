# Chứa các tham số cấu hình (độ nhạy, ngưỡng click, kích thước màn hình)

import pyautogui

# Kích thước màn hình hệ điều hành
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

# Cấu hình Camera
CAM_WIDTH, CAM_HEIGHT = 640, 480

# --- LỌC NHIỄU VÀ LÀM MỊN (ONE EURO & LERP) ---
FILTER_FREQ = 30.0  
FILTER_MIN_CUTOFF = 0.5  
FILTER_BETA = 0.05  
FILTER_D_CUTOFF = 1.0  
MOUSE_LERP_ALPHA = 0.20  # Hệ số Alpha cho thuật toán Linear Interpolation (0.1 -> 0.3)

# --- GIỚI HẠN TĂNG TỐC CHUỘT (ACCELERATION) ---
MOUSE_ACCEL_FACTOR = 1.6  # Hệ số lũy thừa tăng tốc khi ra xa tâm (1.0 là tuyến tính)

# --- CẤU HÌNH GESTURE TIMING (GIÂY) ---
CLICK_MAX_DURATION = 0.5  # Há mồm dưới 0.5s => Click đơn
DRAG_MIN_DURATION = 1.5   # Giữ há mồm trên 1.5s => Kéo thả (Drag & Drop)
LOCK_HOLD_DURATION = 3.0  # Giữ nghiêng đầu 3s để Khóa/Mở

# --- NGƯỠNG NGHIÊNG ĐẦU (ĐỘ) ---
ROLL_THRESHOLD_LEFT = 22.0   # Nghiêng trái > 22 độ (tương đương góc nhìn nghiêng sâu)
ROLL_THRESHOLD_RIGHT = -22.0 # Nghiêng phải > 22 độ

# --- VÙNG TƯƠNG TÁC TRUNG TÂM (SẼ ĐƯỢC CẬP NHẬT ĐỘNG BỞI CALIBRATION) ---
FRAME_INNER_X1 = 0.35
FRAME_INNER_X2 = 0.65
FRAME_INNER_Y1 = 0.35
FRAME_INNER_Y2 = 0.65

# --- BIẾN TOÀN CỤC ĐƯỢC DÙNG CHO CALIBRATION ĐỘNG ---
DYNAMIC_MOUTH_THRESH = 0.06  # Sẽ tự động tính toán lại
CALIBRATED_CENTER_X = 0.5
CALIBRATED_CENTER_Y = 0.5