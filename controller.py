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
        
        # Bộ đệm vận tốc động để theo dõi quán tính run giật
        self.last_target_x = current_px
        self.last_target_y = current_py

    def move_to_smooth(self, clamped_x, clamped_y):
        """
        🌟 ADVANCED BIOMETRIC INTERPOLATION ENGINE V3.0
        Tối ưu hóa bộ chống rung chi tiết vàng cho Parkinson và gia tốc lướt mượt cho Regular.
        """
        if config.system_state != "RUNNING": 
            return

        # 1. Tính toán ranh giới vùng biên an toàn toán học
        boundary_x1 = config.FRAME_INNER_X1 + config.MATH_DEADZONE_REDUCTION
        boundary_x2 = config.FRAME_INNER_X2 - config.MATH_DEADZONE_REDUCTION
        boundary_y1 = config.FRAME_INNER_Y1 + config.MATH_DEADZONE_REDUCTION
        boundary_y2 = config.FRAME_INNER_Y2 - config.MATH_DEADZONE_REDUCTION
        
        # Khóa biên chống lỗi chia cho 0
        range_x = max(0.001, boundary_x2 - boundary_x1)
        range_y = max(0.001, boundary_y2 - boundary_y1)

        # 2. Ánh xạ trực tiếp tuyến tính tuyệt đối 1:1 sang hệ pixel màn hình
        mapped_x = (clamped_x - boundary_x1) / range_x
        mapped_y = (clamped_y - boundary_y1) / range_y
        
        mapped_x = np.clip(mapped_x, 0.0, 1.0)
        mapped_y = np.clip(mapped_y, 0.0, 1.0)
        
        target_x = mapped_x * config.SCREEN_WIDTH
        target_y = mapped_y * config.SCREEN_HEIGHT
        
        # Tính khoảng cách hình học thực tế từ vị trí chuột HIỆN TẠI đến mục tiêu MỚI
        move_dist = math.hypot(target_x - self.curr_x, target_y - self.curr_y)
        
        # 3. CHI TIẾT VÀNG: PHÂN TÁCH GIẢI THUẬT ĐỘNG THEO CHẾ ĐỘ SINH HỌC
        if config.CURRENT_MODE == "PARKINSON":
            # Bộ lọc chống rung thích ứng chuyển tầng (Smooth Curve Activation)
            if move_dist < 12.0:
                # [Vùng Run Tại Chỗ]: Con trỏ chuột bị khóa chết cứng 100% để click và gõ phím tĩnh lặng
                adaptive_alpha = 0.0
            elif move_dist < 42.0:
                # [Vùng Chuyển Tiếp Mềm]: Người bệnh cố rướn cổ dứt khoát vượt biên độ run.
                # Sử dụng hàm mượt hóa đồ thị hình Sin để nhả phanh từ từ, tránh hiện tượng chuột bị giật nảy.
                scale = (move_dist - 12.0) / (42.0 - 12.0)
                smooth_step = (math.sin((scale - 0.5) * math.pi) + 1.0) / 2.0
                adaptive_alpha = smooth_step * 0.15
            else:
                # [Vùng Di Chuyển Chủ Động]: Chuột bám theo hành trình rướn cổ của người bệnh
                adaptive_alpha = 0.15 + min(0.35, (move_dist - 42.0) / 100.0)
                
        else:
            # 🌟 CHẾ ĐỘ REGULAR MODE - TỐI ƯU GIA TỐC PHẢN HỒI SIÊU TỐC
            if move_dist < 6.0:
                # Khi nhắm trúng các mục tiêu siêu nhỏ: Giảm tốc để không trượt tâm
                adaptive_alpha = 0.15 + (move_dist / 6.0) * 0.10
            elif move_dist > 80.0:
                # Khi liếc đầu nhanh để lướt sang góc màn hình khác: Đuổi kịp ngay lập tức không trễ
                adaptive_alpha = 0.82
            else:
                # Khúc trung gian giữa nhanh và chậm: Nội suy mượt theo tỷ lệ khoảng cách
                scale = (move_dist - 6.0) / (80.0 - 6.0)
                adaptive_alpha = 0.25 + scale * (0.82 - 0.25)
            
        # 4. Thực hiện lệnh nội suy Lerp cập nhật vị trí nền
        self.curr_x = self.curr_x + adaptive_alpha * (target_x - self.curr_x)
        self.curr_y = self.curr_y + adaptive_alpha * (target_y - self.curr_y)
        
        self.last_target_x = target_x
        self.last_target_y = target_y
        
        # Thực thi di chuyển chuột tầng OS
        pyautogui.moveTo(int(self.curr_x), int(self.curr_y), duration=0.0)

    def execute_click(self):
        """Giải phóng lệnh click toàn cục"""
        if config.system_state == "RUNNING":
            pyautogui.click()

    def execute_scroll(self, anchor_y, current_y):
        if config.system_state != "RUNNING": 
            return
        diff_y = current_y - anchor_y
        if abs(diff_y) < 0.015: 
            return
        # Hệ số cuộn trang động siêu mượt giúp giảm mỏi cơ cổ cho người khuyết tật
        scroll_amount = int(diff_y * -2300)
        if scroll_amount != 0:
            pyautogui.scroll(scroll_amount)