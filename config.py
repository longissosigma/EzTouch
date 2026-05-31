# Chứa các tham số cấu hình (độ nhạy, ngưỡng click, kích thước màn hình)

import pyautogui

# Kích thước màn hình hệ điều hành
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

# Cấu hình Camera góc quét rộng vật lý
CAM_WIDTH, CAM_HEIGHT = 1280, 720

# --- THAM SỐ LỌC NHIỄU NỀN TỐI GIẢN ---
FILTER_FREQ = 30.0  
FILTER_MIN_CUTOFF = 0.5   
FILTER_BETA = 0.20        
FILTER_D_CUTOFF = 1.0  

# Ngưỡng nghiêng đầu để chọn chế độ (Độ)
ROLL_SELECT_LEFT = -18.0   
ROLL_SELECT_RIGHT = 18.0   
SELECT_HOLD_DURATION = 2.0 

# Thời gian theo dõi chốt tâm mũi động
AUTOCENTER_STABLE_DURATION = 4.0  

# --- CHẾ ĐỘ HOẠT ĐỘNG ---
CURRENT_MODE = "UNDECIDED"      

# --- 🌟 TỐI ƯU TIMING: MỞ RỘNG VÙNG THỜI GIAN NHẤP NHẢ ĐỂ CLICK NHẠY HƠN ---
CLICK_MAX_DURATION = 0.55  # Dưới 0.55 giây nhấp nhả mồm là ăn chắc 1 cú click đơn
DRAG_MIN_DURATION = 1.3    # Giữ mồm mở liên tục trên 1.3 giây sẽ kích hoạt cuộn chuột

# --- THỜI GIAN QUẢN LÝ TỰ ĐỘNG KHÓA/MỞ ---
FACE_ABSENCE_DURATION = 2.0  
HOT_CORNER_DURATION = 3.0    
RESUME_MOUTH_DURATION = 3.0  

# Vùng an toàn quy chuẩn (0.25) quanh tâm thật
FRAME_INNER_X1 = 0.25
FRAME_INNER_X2 = 0.75
FRAME_INNER_Y1 = 0.25
FRAME_INNER_Y2 = 0.75

# Biên toán học ảo giúp nhích nhẹ đầu chuột bay hết màn hình
MATH_DEADZONE_REDUCTION = 0.11

# Biến toàn cục dùng cho Calibration
DYNAMIC_MOUTH_THRESH = 0.045  
CALIBRATED_CENTER_X = 0.5
CALIBRATED_CENTER_Y = 0.5