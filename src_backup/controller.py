# controller.py
import pyautogui
import numpy as np
import math
from . import config

pyautogui.FAILSAFE = False

class MouseController:
    def __init__(self):
        current_px, current_py = pyautogui.position()
        self.curr_x = current_px
        self.curr_y = current_py
        self.is_scroll_mode = False
        self.last_target_x = current_px
        self.last_target_y = current_py

    def check_magnetic_snapping(self, target_x, target_y):
        """
        🔮 DYNAMIC FITTS' LAW ENGINE
        Tính toán khoảng cách thời gian thực đến toàn bộ các nút bấm quan trọng đang hiển thị trên màn hình.
        Nếu lọt vào vùng đệm, nam châm ảo sẽ kích hoạt hút chặt để chống trượt chuột cho người bệnh run tay.
        """
        if not config.MAGNETIC_TARGETS:
            return target_x, target_y

        for name, center_pos in list(config.MAGNETIC_TARGETS.items()):
            cx, cy = center_pos
            distance = math.hypot(target_x - cx, target_y - cy)
            if distance <= config.MAGNET_SNAP_RADIUS:
                return float(cx), float(cy)
                
        return target_x, target_y

    def move_to_smooth(self, clamped_x, clamped_y):
        """
        🌟 BIOMETRIC HYPER-SPEED SMOOTH ENGINE V12.0 - MAXIMUM SMOOTH & ANTI-TREMOR
        Tối ưu hóa Regular Mode: Giải phóng vô cực gia tốc di chuyển, kết hợp bộ phanh tĩnh vùng chết động.
        Chuột lướt mượt 1:1 như dùng tay khi nhích đầu, và khóa chết cứng ngắc khi ngồi yên.
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
        
        # Ánh xạ ra tọa độ pixel đích thô trên màn hình thực tế
        raw_target_x = mapped_x * config.SCREEN_WIDTH
        raw_target_y = mapped_y * config.SCREEN_HEIGHT
        
        # Thực thi kiểm tra lực hút nam châm ảo trước khi di chuyển
        target_x, target_y = self.check_magnetic_snapping(raw_target_x, raw_target_y)
        
        # Tính khoảng cách dịch chuyển thực tế từ vị trí hiện tại đến vị trí mục tiêu
        move_dist = math.hypot(target_x - self.curr_x, target_y - self.curr_y)
        
        if config.CURRENT_MODE == "PARKINSON":
            # Chế độ Parkinson: Giữ nguyên bộ phanh tầng thích ứng thích nghi chống rung lắc vô thức
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
            # 🚀 CHẾ ĐỘ REGULAR: ĐỘNG CƠ THÍCH ỨNG SIÊU TỐC ĐỘ (MAXIMUM SMOOTH 1:1)
            # Bước 1: Bộ phanh khóa tĩnh vùng chết - Khi ngồi im, khóa chết cứng 100% không cho chuột tự rung
            if move_dist < 3.5:
                # Nếu đang bị hút bởi nam châm ảo, ép tọa độ về tâm nút bấm ngay lập tức
                if target_x != raw_target_x or target_y != raw_target_y:
                    self.curr_x = target_x
                    self.curr_y = target_y
                    pyautogui.moveTo(int(self.curr_x), int(self.curr_y), duration=0.0)
                return # Đứng im phăng phắc, hấp thụ hoàn toàn xung nhiễu li ti của camera vật lý
            
            # Bước 2: Khi di chuyển chủ động vượt ngưỡng phanh, nhả phanh và lướt siêu tốc với Lerp tăng lên 0.85
            # Hệ số 0.85 loại bỏ hoàn toàn cảm giác khựng hay trễ, chuột bám đuổi đỉnh mũi cực mịn và bốc y như tay di
            self.curr_x = self.curr_x + 0.85 * (target_x - self.curr_x)
            self.curr_y = self.curr_y + 0.85 * (target_y - self.curr_y)
        
        self.last_target_x = target_x
        self.last_target_y = target_y
        
        # Thực thi dịch chuyển con trỏ chuột tầng OS tức thời
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