# Class điều khiển chuột qua PyAutoGUI, map tọa độ camera ra màn hình

import pyautogui
import numpy as np
import math
import config

pyautogui.FAILSAFE = False

class MouseController:
    def __init__(self):
        current_px, current_py = pyautogui.position()
        self.curr_x = current_px
        self.curr_y = current_py
        self.is_scroll_mode = False

    def move_to_smooth(self, clamped_x, clamped_y):
        """🌟 ABSOLUTE REALTIME 1:1 - Đồng bộ lập tức tọa độ chuột, triệt tiêu delay."""
        
        # 1. Tính toán ranh giới toán học ảo tối ưu cho góc quay cổ thoải mái
        boundary_x1 = config.FRAME_INNER_X1 + config.MATH_DEADZONE_REDUCTION
        boundary_x2 = config.FRAME_INNER_X2 - config.MATH_DEADZONE_REDUCTION
        boundary_y1 = config.FRAME_INNER_Y1 + config.MATH_DEADZONE_REDUCTION
        boundary_y2 = config.FRAME_INNER_Y2 - config.MATH_DEADZONE_REDUCTION
        
        # 2. Ánh xạ trực tiếp tuyến tính tuyệt đối 1:1
        mapped_x = (clamped_x - boundary_x1) / (boundary_x2 - boundary_x1)
        mapped_y = (clamped_y - boundary_y1) / (boundary_y2 - boundary_y1)
        
        mapped_x = np.clip(mapped_x, 0.0, 1.0)
        mapped_y = np.clip(mapped_y, 0.0, 1.0)
        
        # Tọa độ pixel đích ngoài đời thực
        target_x = mapped_x * config.SCREEN_WIDTH
        target_y = mapped_y * config.SCREEN_HEIGHT
        
        # 3. Phân tách bộ lọc thích ứng nâng tốc độ lên mức tối đa
        if config.CURRENT_MODE == "PARKINSON":
            move_dist = math.hypot(target_x - self.curr_x, target_y - self.curr_y)
            if move_dist < 8.0:
                adaptive_alpha = 0.05  # Giữ phanh ma sát ảo chống run bần bật tại chỗ cho người bệnh
            else:
                adaptive_alpha = 0.85  # Phóng đi nhanh khi di chuyển xa
        else:
            # 🌟 YÊU CẦU 2: NGƯỜI KHÔNG RUN CHẠY TỐC ĐỘ MAX - ZERO DELAY
            # Ép hệ số bằng 1.0 tuyệt đối. Chuột không còn nhịp hãm, mũi đến đâu chuột bay đến đó ngay lập tức!
            adaptive_alpha = 1.0  
            
        # Cập nhật vị trí
        self.curr_x = self.curr_x + adaptive_alpha * (target_x - self.curr_x)
        self.curr_y = self.curr_y + adaptive_alpha * (target_y - self.curr_y)
        
        # Điều khiển chuột hệ điều hành
        pyautogui.moveTo(int(self.curr_x), int(self.curr_y), duration=0.0)

    def execute_click(self):
        pyautogui.click()

    def execute_scroll(self, anchor_y, current_y):
        diff_y = current_y - anchor_y
        if abs(diff_y) < 0.015:
            return
        scroll_amount = int(diff_y * -1800)
        if scroll_amount != 0:
            pyautogui.scroll(scroll_amount)