# Class điều khiển chuột qua PyAutoGUI, map tọa độ camera ra màn hình

# Class điều khiển chuột qua PyAutoGUI, map tọa độ camera ra màn hình

import pyautogui
import math
import config

pyautogui.FAILSAFE = False

class MouseController:
    def __init__(self):
        current_px, current_py = pyautogui.position()
        self.curr_x = current_px
        self.curr_y = current_py
        self.is_dragging = False

    def move_to_smooth(self, x_norm, y_norm):
        """Map tọa độ, áp dụng bộ gia tốc góc chết và nội suy tuyến tính thích ứng động."""
        # 1. Tính toán vector lệch so với tâm đã được Calibration định vị
        offset_x = x_norm - config.CALIBRATED_CENTER_X
        offset_y = y_norm - config.CALIBRATED_CENTER_Y
        
        # 2. Áp dụng cơ chế Mouse Acceleration hình nón (nhân hệ số lũy thừa khi ra xa tâm)
        dist_from_center = math.hypot(offset_x, offset_y)
        if dist_from_center > 0:
            scale = math.pow(dist_from_center, config.MOUSE_ACCEL_FACTOR - 1.0)
            scale = min(scale, 2.5) 
            offset_x *= (1.0 + scale)
            offset_y *= (1.0 + scale)
            
        # Re-map lại tọa độ ảo sau khi tăng tốc
        x_accelerated = config.CALIBRATED_CENTER_X + offset_x
        y_accelerated = config.CALIBRATED_CENTER_Y + offset_y

        # 3. Chuyển đổi sang hệ tọa độ màn hình dựa trên vùng biên an toàn
        mapped_x = (x_accelerated - config.FRAME_INNER_X1) / (config.FRAME_INNER_X2 - config.FRAME_INNER_X1)
        mapped_y = (y_accelerated - config.FRAME_INNER_Y1) / (config.FRAME_INNER_Y2 - config.FRAME_INNER_Y1)
        
        target_x = max(0, min(config.SCREEN_WIDTH - 1, mapped_x * config.SCREEN_WIDTH))
        target_y = max(0, min(config.SCREEN_HEIGHT - 1, mapped_y * config.SCREEN_HEIGHT))
        
        # 🌟 NÂNG CẤP CAO CẤP: LERP ALPHA THÍCH ỨNG THEO VẬN TỐC RUNG LẮC
        # Tính khoảng cách từ vị trí chuột hiện tại đến mục tiêu mới
        move_dist = math.hypot(target_x - self.curr_x, target_y - self.curr_y)
        
        if move_dist < 5.0:
            # Nếu khoảng cách cực nhỏ (người dùng đang bị run tại chỗ), siết chặt Alpha để ghìm cứng chuột
            adaptive_alpha = 0.08
        elif move_dist > 100.0:
            # Nếu di chuyển khoảng cách xa (chủ động quay đầu chuyển vùng), tăng Alpha để bám đuổi nhạy bén
            adaptive_alpha = 0.35
        else:
            # Các vùng di chuyển thông thường dùng hệ số mịn mượt tuyến tính
            adaptive_alpha = config.MOUSE_LERP_BASE_ALPHA
        
        # 4. Áp dụng thuật toán LERP với hệ số Alpha thích ứng động vừa tính
        self.curr_x = self.curr_x + adaptive_alpha * (target_x - self.curr_x)
        self.curr_y = self.curr_y + adaptive_alpha * (target_y - self.curr_y)
        
        # Điều khiển hệ điều hành di chuyển chuột
        pyautogui.moveTo(int(self.curr_x), int(self.curr_y), duration=0.0)

    def execute_click(self):
        """Thực hiện click đơn"""
        if not self.is_dragging:
            pyautogui.click()

    def start_drag(self):
        """Kích hoạt trạng thái nhấn giữ chuột trái (Mouse Down)"""
        if not self.is_dragging:
            pyautogui.mouseDown()
            self.is_dragging = True

    def end_drag(self):
        """Giải phóng trạng thái nhấn giữ chuột (Mouse Up)"""
        if self.is_dragging:
            pyautogui.mouseUp()
            self.is_dragging = False