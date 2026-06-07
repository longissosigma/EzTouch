# config.py
import pyautogui

SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
CAM_WIDTH, CAM_HEIGHT = 1280, 720

FILTER_FREQ = 30.0  
FILTER_MIN_CUTOFF = 0.45   
FILTER_BETA = 0.12        
FILTER_D_CUTOFF = 1.0  

# --- THỜI GIAN ĐỒNG BỘ CHUẨN BACKEND ---
ROLL_SELECT_LEFT = -18.0   
ROLL_SELECT_RIGHT = 18.0   
SELECT_HOLD_DURATION = 2.0       # Cố định chuẩn 2.0 giây
AUTOCENTER_STABLE_DURATION = 1.5 # Cố định chuẩn 1.5 giây

DWELL_DURATION = 2.0              
DWELL_PIXEL_RADIUS = 8            
is_keyboard_open = False          

# 🌟 DYNAMIC FITTS' LAW CONFIGURATION
MAGNET_SNAP_RADIUS = 15           # Vùng đệm 15px tạo lực hút nam châm ảo theo yêu cầu

KEYBOARD_LAYOUT = [
    ["A", "B", "C", "D", "E", "F"],
    ["G", "H", "I", "J", "K", "L"],
    ["M", "N", "O", "P", "Q", "R"],
    ["S", "T", "U", "V", "W", "X"],
    ["Y", "Z", "SPACE", "BACKSPACE", "ENTER", "MOVE", "CLOSE"]
]

system_state = "RUNNING"          
prev_system_state = "RUNNING"     

CLICK_MAX_DURATION = 0.55  
DRAG_MIN_DURATION = 1.3    
HOT_CORNER_DURATION = 3.0    
RESUME_MOUTH_DURATION = 3.0  
FACE_ABSENCE_DURATION = 2.0       

FRAME_INNER_X1 = 0.25
FRAME_INNER_X2 = 0.75
FRAME_INNER_Y1 = 0.25
FRAME_INNER_Y2 = 0.75

MATH_DEADZONE_REDUCTION = 0.11
DYNAMIC_MOUTH_THRESH = 0.045  
CALIBRATED_CENTER_X = 0.5
CALIBRATED_CENTER_Y = 0.5
CURRENT_MODE = "UNDECIDED"

# --- TRẠNG THÁI TOÀN CỤC CHO TRIAL MODE (ONBOARDING) ---
is_trial_active = False
trial_task_stage = 0  
trial_countdown_pct = 0

# Biến theo dõi focus đồng bộ đa tầng toàn hệ thống
is_chat_input_focused = False
trial_keyboard_warning_text = ""

# 🌟 DANH SÁCH TỌA ĐỘ MỤC TIÊU NAM CHÂM ẢO TOÀN CỤC (Lưu cấu trúc từ điển: {"Tên_nút": (Tâm_X, Tâm_Y)})
MAGNETIC_TARGETS = {}