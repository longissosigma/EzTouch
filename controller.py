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
        """🌟 PERFECT INERTIAL LOCKING FOR ALL MODES - Đồng bộ thuật toán hàm mũ siêu mượt cho cả 2 chế độ."""
        if config.system_state != "RUNNING": 
            return

        # 1. Tính toán ranh giới vùng biên an toàn tối ưu cho cổ thoải mái
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
        
        # Tính khoảng cách dịch chuyển của chuột để tối ưu Alpha thích ứng
        move_dist = math.hypot(target_x - self.curr_x, target_y - self.curr_y)
        
        # 3. ĐỒNG BỘ THUẬT TOÁN MA SÁT THÍCH ỨNG HÀM MŨ CHO TẤT CẢ CÁC CHẾ ĐỘ
        # Dù người dùng chọn Regular hay Parkinson, thuật toán hoàn hảo này đều xử lý trọn gói
        if move_dist < 18.0:
            # Khi di chuyển ngắn hoặc giữ im đầu: Áp dụng hàm mũ bậc 2 để ghìm chặt Alpha xuống mức siêu nhỏ.
            # Chuột sẽ được đổ bê tông khóa cứng tại chỗ, triệt tiêu sạch nhiễu răng cưa của thấu kính camera.
            adaptive_alpha = (move_dist / 18.0) ** 2 * 0.08
            adaptive_alpha = max(0.005, adaptive_alpha)  # Giữ mốc ma sát ảo tối thiểu để triệt nhiễu hoàn toàn
        else:
            # Khi chủ động quay đầu dứt khoát để di chuyển xa: Phanh ma sát ảo tự động nhả ra,
            # Alpha tự động phình to tuyến tính (0.45 -> 0.70) dựa theo khoảng cách đuổi bắt.
            # Chuột sẽ vút đi cực kỳ mượt mà, tốc độ phản xạ tức thì mà không làm mỏi cơ cổ.
            adaptive_alpha = 0.45 + min(0.25, (move_dist - 18.0) / 60.0)
            
        # 4. Thực hiện Lerp cập nhật vị trí nền
        self.curr_x = self.curr_x + adaptive_alpha * (target_x - self.curr_x)
        self.curr_y = self.curr_y + adaptive_alpha * (target_y - self.curr_y)
        
        # Điều khiển chuột thực tế của hệ điều hành
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