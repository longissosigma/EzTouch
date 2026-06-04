# config.py
import pyautogui

# Kích thước màn hình hệ điều hành
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

# Cấu hình Camera góc quét rộng vật lý
CAM_WIDTH, CAM_HEIGHT = 1280, 720

# --- THAM SỐ LỌC NHIỄU NỀN MẶC ĐỊNH (TỐI ƯU HÓA CAO CẤP) ---
FILTER_FREQ = 30.0  
FILTER_MIN_CUTOFF = 0.45   # Tăng lực găm giữ chuột khi đứng im
FILTER_BETA = 0.12        # Triệt tiêu hoàn toàn răng cưa nhiễu camera khi di chuyển chậm
FILTER_D_CUTOFF = 1.0  

# --- THAM SỐ NGHIÊNG ĐẦU CHỌN CHẾ ĐỘ ---
ROLL_SELECT_LEFT = -18.0   
ROLL_SELECT_RIGHT = 18.0   
SELECT_HOLD_DURATION = 2.0  # Giảm từ 3.0s về 2.0s theo yêu cầu

# --- THỜI GIAN KHỞI TẠO VÙNG AN TOÀN ---
AUTOCENTER_STABLE_DURATION = 1.5  # Giảm từ 2.0s về 1.5s theo yêu cầu

# --- TÍNH NĂNG BÀN PHÍM ẢO & DWELL CLICK ---
DWELL_DURATION = 2.0              
DWELL_PIXEL_RADIUS = 8            
is_keyboard_open = False          

# Bán kính hút từ tính ảo của phím (Vô hiệu hóa snap thô bạo, xử lý mượt bằng toán học)
MAGNET_SNAP_RADIUS = 35           

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

# Chế độ người dùng chọn (REGULAR / PARKINSON / UNDECIDED)
CURRENT_MODE = "UNDECIDED"