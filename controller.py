# controller.py
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
        self.last_target_x = current_px
        self.last_target_y = current_py

    def move_to_smooth(self, clamped_x, clamped_y):
        """
        🌟 BIOMETRIC HYPER-SPEED SMOOTH ENGINE V9.0 - ANTI-TREMOR
        Tối ưu hóa Regular Mode: Tích hợp bộ lọc vùng chết toán học (Mathematical Deadzone).
        Khóa chết cứng con trỏ khi ngồi yên và giải phóng gia tốc Lerp cao khi chủ động di chuyển.
        """
        if config.system_state != "RUNNING": 
            return

        # 1. Tính toán ranh giới vùng biên an toàn toán học
        boundary_x1 = config.FRAME_INNER_X1 + config.MATH_DEADZONE_REDUCTION
        boundary_x2 = config.FRAME_INNER_X2 - config.MATH_DEADZONE_REDUCTION
        boundary_y1 = config.FRAME_INNER_Y1 + config.MATH_DEADZONE_REDUCTION
        boundary_y2 = config.FRAME_INNER_Y2 - config.MATH_DEADZONE_REDUCTION
        
        range_x = max(0.001, boundary_x2 - boundary_x1)
        range_y = max(0.001, boundary_y2 - boundary_y1)

        mapped_x = (clamped_x - boundary_x1) / range_x
        mapped_y = (clamped_y - boundary_y1) / range_y
        
        mapped_x = np.clip(mapped_x, 0.0, 1.0)
        mapped_y = np.clip(mapped_y, 0.0, 1.0)
        
        # Ánh xạ ra tọa độ pixel đích trên màn hình
        target_x = mapped_x * config.SCREEN_WIDTH
        target_y = mapped_y * config.SCREEN_HEIGHT
        
        # Tính khoảng cách dịch chuyển thực tế từ vị trí hiện tại đến vị trí mục tiêu
        move_dist = math.hypot(target_x - self.curr_x, target_y - self.curr_y)
        
        if config.CURRENT_MODE == "PARKINSON":
            # Chế độ Parkinson: Giữ nguyên bộ phanh tầng thích ứng chống rung lắc vô thức
            if move_dist < 12.0:
                adaptive_alpha = 0.0
            elif move_dist < 42.0:
                scale = (move_dist - 12.0) / (42.0 - 12.0)
                smooth_step = (math.sin((scale - 0.5) * math.pi) + 1.0) / 2.0
                adaptive_alpha = smooth_step * 0.15
            else:
                adaptive_alpha = 0.15 + min(0.35, (move_dist - 42.0) / 100.0)
                
            self.curr_x = self.curr_x + adaptive_alpha * (target_x - self.curr_x)
            self.curr_y = self.curr_y + adaptive_alpha * (target_y - self.curr_y)
            
        else:
            # 🚀 CHẾ ĐỘ REGULAR: BỘ PHANH VÙNG CHẾT TOÁN HỌC (DEADZONE CONTROL)
            # Tăng ngưỡng chặn lên 4.5 pixel để hấp thụ toàn bộ xung nhiễu của camera vật lý khi m ngồi im
            if move_dist < 4.5:
                return # Khóa cứng chuột đứng im phăng phắc, không cho phép dao động nhiễu hạt phá hoại
            
            # Khi di chuyển chủ động vượt ngưỡng nhiễu, chuột đuổi theo mũi cực nhanh và mượt mà
            # Sử dụng hệ số Lerp mượt 0.65 để vừa triệt tiêu răng cưa vừa giữ tốc độ lướt 1:1 siêu tốc
            self.curr_x = self.curr_x + 0.65 * (target_x - self.curr_x)
            self.curr_y = self.curr_y + 0.65 * (target_y - self.curr_y)
        
        self.last_target_x = target_x
        self.last_target_y = target_y
        
        # Thực thi dịch chuyển con trỏ chuột tầng OS
        pyautogui.moveTo(int(self.curr_x), int(self.curr_y), duration=0.0)

    def execute_click(self):
        if config.system_state == "RUNNING":
            pyautogui.click()

    def execute_scroll(self, anchor_y, current_y):
        if config.system_state != "RUNNING": 
            return
        diff_y = current_y - anchor_y
        if abs(diff_y) < 0.015: 
            return
        scroll_amount = int(diff_y * -2500)
        if scroll_amount != 0:
            pyautogui.scroll(scroll_amount)