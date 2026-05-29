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

    def move_to_smooth(self, x_norm, y_norm):
        """Hệ thống map tọa độ thông minh tự co giãn theo Chế độ người dùng chọn."""
        
        # 🌟 ĐỘC LẬP: Nếu là Người thường (REGULAR), siết biên ảo hẹp hơn sâu nữa để triệt tiêu hiện tượng mỏi cổ
        current_reduction = 0.14 if config.CURRENT_MODE == "REGULAR" else config.MATH_DEADZONE_REDUCTION
        
        # 1. Tính toán biên giới hạn toán học ảo dựa trên vùng an toàn động
        boundary_x1 = config.FRAME_INNER_X1 + current_reduction
        boundary_x2 = config.FRAME_INNER_X2 - current_reduction
        boundary_y1 = config.FRAME_INNER_Y1 + current_reduction
        boundary_y2 = config.FRAME_INNER_Y2 - current_reduction
        
        # 2. Ánh xạ trực tiếp tuyến tính tuyệt đối 1:1 theo tọa độ phần trăm
        mapped_x = (x_norm - boundary_x1) / (boundary_x2 - boundary_x1)
        mapped_y = (y_norm - boundary_y1) / (boundary_y2 - boundary_y1)
        
        # Bo biên chống tràn kẹt chuột ngoài rìa màn hình
        mapped_x = np.clip(mapped_x, 0.0, 1.0)
        mapped_y = np.clip(mapped_y, 0.0, 1.0)
        
        # Tính toán tọa độ Pixel đích thực tế trên màn hình máy tính
        target_x = mapped_x * config.SCREEN_WIDTH
        target_y = mapped_y * config.SCREEN_HEIGHT
        
        # 3. Tính khoảng cách dịch chuyển để kích hoạt bộ lọc thích ứng
        move_dist = math.hypot(target_x - self.curr_x, target_y - self.curr_y)
        
        # PHÂN TÁCH LUỒNG TOÁN HỌC DỰA TRÊN CHẾ ĐỘ NGƯỜI DÙNG CHỌN
        if config.CURRENT_MODE == "PARKINSON":
            # --- PHIÊN BẢN CHO NGƯỜI RUN (PARKINSON MODE) ---
            if move_dist < 8.0:
                adaptive_alpha = 0.05  # Phanh ma sát ảo ghìm cứng chuột đứng im hoàn toàn khi bị run bần bật
            elif move_dist > 35.0:
                adaptive_alpha = 0.85  
            else:
                adaptive_alpha = config.MOUSE_LERP_BASE_ALPHA
        else:
            # --- PHIÊN BẢN CHO NGƯỜI KHÔNG RUN (ACTIVE SIÊU TỐC MODE - ZERO DELAY) ---
            if move_dist < 2.5:
                adaptive_alpha = 0.20  # Khử nhiễu camera nhẹ tại chỗ
            else:
                # 🌟 Ép hệ số lên 1.0: Không delay, không trễ lọc, mũi nhích một milimet chuột phóng đúng vị trí tương tự realtime!
                adaptive_alpha = 1.0  
        
        # Thực hiện dịch chuyển tọa độ con trỏ nền
        self.curr_x = self.curr_x + adaptive_alpha * (target_x - self.curr_x)
        self.curr_y = self.curr_y + adaptive_alpha * (target_y - self.curr_y)
        
        # Điều khiển chuột hệ điều hành
        pyautogui.moveTo(int(self.curr_x), int(self.curr_y), duration=0.0)

    def execute_click(self):
        """Thực hiện click chuột trái đơn"""
        pyautogui.click()

    def execute_scroll(self, anchor_y, current_y):
        """Cuộn chuột dọc thích ứng dựa trên độ lệch chiều dọc đầu."""
        diff_y = current_y - anchor_y
        if abs(diff_y) < 0.015:
            return
        scroll_amount = int(diff_y * -1800)
        if scroll_amount != 0:
            pyautogui.scroll(scroll_amount)