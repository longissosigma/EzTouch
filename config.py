# Chứa các tham số cấu hình (độ nhạy, ngưỡng click, kích thước màn hình)

import pyautogui

# Kích thước màn hình hệ điều hành
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

# Cấu hình Camera
CAM_WIDTH, CAM_HEIGHT = 640, 480

# --- THAM SỐ LỌC NHIỄU MỚI (ONE EURO FILTER) ---
# Tần số quét mẫu (phù hợp với tốc độ khung hình webcam thông thường)
FILTER_FREQ = 30.0  
# Tốc độ cắt tối thiểu (Giảm số này xuống nếu muốn con trỏ đứng im cực mượt khi người dùng bị run tại chỗ)
FILTER_MIN_CUTOFF = 0.5  
# Hệ số nhạy theo tốc độ (Tăng số này nếu muốn chuột bám đuổi nhanh khi quay đầu đột ngột)
FILTER_BETA = 0.05  
# Tốc độ cắt đạo hàm
FILTER_D_CUTOFF = 1.0  

# --- CẤU HÌNH CLICK ---
# Ngưỡng tỷ lệ há miệng để kích hoạt click
MOUTH_AR_THRESH = 0.06 
# Thời gian hồi chiêu giữa các lần click (giây)
CLICK_COOLDOWN = 1.2 

# --- VÙNG TƯƠNG TÁC AN TOÀN (DEADZONE BOUNDS) ---
FRAME_INNER_X1 = 0.35
FRAME_INNER_X2 = 0.65
FRAME_INNER_Y1 = 0.35
FRAME_INNER_Y2 = 0.65