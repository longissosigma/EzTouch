# Class điều khiển chuột qua PyAutoGUI, map tọa độ camera ra màn hình

import pyautogui
import time
import math
import config

pyautogui.FAILSAFE = False

class MouseController:
    def __init__(self):
        # Lưu trữ tọa độ hiện tại của chuột để thực hiện tính toán LERP
        current_px, current_py = pyautogui.position()
        self.curr_x = current_px
        self.curr_y = current_py
        self.is_dragging = False

    def move_to_smooth(self, x_norm, y_norm):
        """Map tọa độ, áp dụng bộ gia tốc góc chết và nội suy tuyến tính (LERP)."""
        # 1. Tính toán vector lệch so với tâm đã được Calibration định vị
        offset_x = x_norm - config.CALIBRATED_CENTER_X
        offset_y = y_norm - config.CALIBRATED_CENTER_Y
        
        # 2. Áp dụng cơ chế Mouse Acceleration hình nón (nhân hệ số lũy thừa khi ra xa tâm)
        dist_from_center = math.hypot(offset_x, offset_y)
        if dist_from_center > 0:
            scale = math.pow(dist_from_center, config.MOUSE_ACCEL_FACTOR - 1.0)
            # Giới hạn scale để tránh chuột nhảy quá xa đột ngột
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
        
        # 4. Áp dụng thuật toán LERP (Linear Interpolation) khử Jitter tuyệt đối
        self.curr_x = self.curr_x + config.MOUSE_LERP_ALPHA * (target_x - self.curr_x)
        self.curr_y = self.curr_y + config.MOUSE_LERP_ALPHA * (target_y - self.curr_y)
        
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