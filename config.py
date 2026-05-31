# config.py
import pyautogui

# Kích thước màn hình hệ điều hành
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

# Cấu hình Camera góc quét rộng vật lý
CAM_WIDTH, CAM_HEIGHT = 1280, 720

# --- THAM SỐ LỌC NHIỄU NỀN MẶC ĐỊNH ---
FILTER_FREQ = 30.0  
FILTER_MIN_CUTOFF = 0.5   
FILTER_BETA = 0.20        
FILTER_D_CUTOFF = 1.0  

# --- 🌟 CẬP NHẬT: THAM SỐ NGHIÊNG ĐẦU CHỌN CHẾ ĐỘ GIẢM VỀ 3.0 GIÂY ---
ROLL_SELECT_LEFT = -18.0   
ROLL_SELECT_RIGHT = 18.0   
SELECT_HOLD_DURATION = 3.0 # Đã sửa từ 3.6s về 3.0s

# Thời gian theo dõi chốt tâm mũi động trong 3 giây
AUTOCENTER_STABLE_DURATION = 3.0  

# --- TÍNH NĂNG BÀN PHÍM ẢO & DWELL CLICK ---
DWELL_DURATION = 2.0              
DWELL_PIXEL_RADIUS = 8            
is_keyboard_open = False          

# Thời gian tích lũy cử chỉ lắc đầu mở phím (3 giây)
SHAKE_WINDOW_DURATION = 3.0

KEYBOARD_LAYOUT = [
    ["A", "B", "C", "D", "E", "F"],
    ["G", "H", "I", "J", "K", "L"],
    ["M", "N", "O", "P", "Q", "R"],
    ["S", "T", "U", "V", "W", "X"],
    ["Y", "Z", "SPACE", "BACKSPACE", "ENTER", "MOVE", "CLOSE"]
]

# --- MÁY TRẠNG THÁI HỆ THỐNG ---
system_state = "RUNNING"          
prev_system_state = "RUNNING"     

# --- TIMING CỬ CHỈ SINH HỌC ---
CLICK_MAX_DURATION = 0.55  
DRAG_MIN_DURATION = 1.3    
HOT_CORNER_DURATION = 3.0    
RESUME_MOUTH_DURATION = 3.0  
FACE_ABSENCE_DURATION = 2.0       

# Vùng an toàn quy chuẩn (0.25) quanh tâm thật sau Calibration
FRAME_INNER_X1 = 0.25
FRAME_INNER_X2 = 0.75
FRAME_INNER_Y1 = 0.25
FRAME_INNER_Y2 = 0.75

MATH_DEADZONE_REDUCTION = 0.11
DYNAMIC_MOUTH_THRESH = 0.045  
CALIBRATED_CENTER_X = 0.5
CALIBRATED_CENTER_Y = 0.5

# Hệ số di chuyển chuột động dựa trên Chế độ người dùng chọn
CURRENT_MODE = "UNDECIDED"