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

    def move_to_smooth(self, clamped_x, clamped_y):
        """🌟 PERFECT INTERPOLATION MATRIX - Thiết kế bộ lọc chống rung tối tân nhất cho Parkinson và siêu mượt cho Regular."""
        if config.system_state != "RUNNING": 
            return

        # 1. Tính toán ranh giới vùng biên an toàn toán học
        boundary_x1 = config.FRAME_INNER_X1 + config.MATH_DEADZONE_REDUCTION
        boundary_x2 = config.FRAME_INNER_X2 - config.MATH_DEADZONE_REDUCTION
        boundary_y1 = config.FRAME_INNER_Y1 + config.MATH_DEADZONE_REDUCTION
        boundary_y2 = config.FRAME_INNER_Y2 - config.MATH_DEADZONE_REDUCTION
        
        # 2. Ánh xạ trực tiếp tuyến tính tuyệt đối 1:1
        mapped_x = (clamped_x - boundary_x1) / (boundary_x2 - boundary_x1)
        mapped_y = (clamped_y - boundary_y1) / (boundary_y2 - boundary_y1)
        
        mapped_x = np.clip(mapped_x, 0.0, 1.0)
        mapped_y = np.clip(mapped_y, 0.0, 1.0)
        
        # Tọa độ pixel đích trên màn hình máy tính thực tế
        target_x = mapped_x * config.SCREEN_WIDTH
        target_y = mapped_y * config.SCREEN_HEIGHT
        
        # Tính khoảng cách dịch chuyển con trỏ để áp bộ lọc thích ứng
        move_dist = math.hypot(target_x - self.curr_x, target_y - self.curr_y)
        
        # 3. TÁCH BIỆT THUẬT TOÁN ĐIỀU KHIỂN ĐỘC LẬP THEO CHẾ ĐỘ
        if config.CURRENT_MODE == "PARKINSON":
            # BỘ CHỐNG RUNG PARKINSON SIÊU CẤP (ĐỔ BÊ TÔNG TUYỆT ĐỐI)
            if move_dist < 35.0:
                adaptive_alpha = 0.0  # Khóa cứng con trỏ chuột đứng im phăng phắc chống run
            else:
                adaptive_alpha = 0.25 + min(0.35, (move_dist - 35.0) / 80.0)
        else:
            # 🌟 CẢI TIẾN SIÊU MƯỢT CHO REGULAR MODE (Hấp thụ sạch nhiễu răng cưa, tăng quán tính êm dịu)
            if move_dist < 8.0:
                # Hạ nhẹ alpha ở cự ly gần để tạo độ êm sướng tay khi nhắm trúng mục tiêu nhỏ
                adaptive_alpha = 0.15 + (move_dist / 8.0) * 0.15
            elif move_dist > 60.0:
                # Tăng tốc độ mượt đuổi bắt dứt khoát khi di chuyển xa rộng màn hình
                adaptive_alpha = 0.70
            else:
                # Vùng điều khiển quán tính trung bình
                adaptive_alpha = 0.35
            
        # 4. Cập nhật vị trí Lerp nền
        self.curr_x = self.curr_x + adaptive_alpha * (target_x - self.curr_x)
        self.curr_y = self.curr_y + adaptive_alpha * (target_y - self.curr_y)
        
        # Ra lệnh điều khiển chuột hệ điều hành
        pyautogui.moveTo(int(self.curr_x), int(self.curr_y), duration=0.0)

    def execute_click(self):
        """Giải phóng lệnh click toàn cục"""
        if config.system_state == "RUNNING":
            pyautogui.click()

    def execute_scroll(self, anchor_y, current_y):
        if config.system_state != "RUNNING": return
        diff_y = current_y - anchor_y
        if abs(diff_y) < 0.015: return
        scroll_amount = int(diff_y * -1800)
        if scroll_amount != 0:
            pyautogui.scroll(scroll_amount)