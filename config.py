# Chứa các tham số cấu hình (độ nhạy, ngưỡng click, kích thước màn hình)

import pyautogui

# Kích thước màn hình hệ điều hành
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

# Cấu hình Camera
CAM_WIDTH, CAM_HEIGHT = 640, 480

# --- THAM SỐ LỌC NHIỄU NỀN MẶC ĐỊNH ---
FILTER_FREQ = 30.0  
FILTER_MIN_CUTOFF = 0.08  
FILTER_BETA = 0.12        
FILTER_D_CUTOFF = 1.0  

# --- Ngưỡng nghiêng đầu để chọn chế độ (Độ) ---
ROLL_SELECT_LEFT = -18.0   
ROLL_SELECT_RIGHT = 18.0   
SELECT_HOLD_DURATION = 2.0 

# --- THỜI GIAN THEO DÕI CHỐT TÂM MŨI ĐỘNG CHUẨN XÁC ---
AUTOCENTER_STABLE_DURATION = 4.0  # Mũi đứng im tại một vị trí trong 4 giây sẽ tự động làm tâm

# --- 🌟 CHẾ ĐỘ HOẠT ĐỘNG ĐỘNG (SẼ TỰ ĐỘNG THAY ĐỔI THEO TỪNG CHẾ ĐỘ) ---
CURRENT_MODE = "UNDECIDED"      # UNDECIDED, PARKINSON, hoặc REGULAR
MOUSE_LERP_BASE_ALPHA = 0.35  
MOUSE_ACCEL_FACTOR = 1.0  

# --- CẤU HÌNH GESTURE TIMING (GIÂY) ---
CLICK_MAX_DURATION = 0.40  
DRAG_MIN_DURATION = 1.2    

# --- THỜI GIAN QUẢN LÝ TỰ ĐỘNG KHÓA/MỞ ---
FACE_ABSENCE_DURATION = 2.0  
HOT_CORNER_DURATION = 3.0    
RESUME_MOUTH_DURATION = 3.0  

# --- 🌟 VÙNG TƯƠNG TÁC HIỂN THỊ TRÊN CAMERA (SẼ ĐƯỢC TÍNH TOÁN ĐỘNG QUANH TÂM THẬT) ---
FRAME_INNER_X1 = 0.25
FRAME_INNER_X2 = 0.75
FRAME_INNER_Y1 = 0.25
FRAME_INNER_Y2 = 0.75

# --- 🌟 BIÊN TOÁN HỌC ẢO TỐI ƯU SIÊU TỐC (CHỐNG MỎI CỔ CHO NGƯỜI KHÔNG RUN) ---
# Tăng từ 0.09 lên 0.14 cho Regular Mode để thu nhỏ biên độ lắc đầu thực tế của người dùng
MATH_DEADZONE_REDUCTION = 0.09

# --- BIẾN TOÀN CỤC ĐƯỢC DÙNG CHO CALIBRATION ĐỘNG ---
DYNAMIC_MOUTH_THRESH = 0.045  
CALIBRATED_CENTER_X = 0.5
CALIBRATED_CENTER_Y = 0.5