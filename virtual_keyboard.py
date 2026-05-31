# virtual_keyboard.py
import cv2
import time
import pyautogui
import numpy as np
import config

class VirtualKeyboard:
    def __init__(self):
        # Kích thước bàn phím ảo siêu to khổng lồ
        self.kb_w = 1100
        self.kb_h = 420
        
        # 🌟 YÊU CẦU 3: Thiết lập vị trí xuất hiện BAN ĐẦU nằm ở CHÍNH GIỮA màn hình máy tính
        self.kb_x = (config.SCREEN_WIDTH - self.kb_w) // 2
        self.kb_y = (config.SCREEN_HEIGHT - self.kb_h) // 2
        
        self.last_mouse_pos = (0, 0)
        self.dwell_start_time = None
        self.current_hovered_key = None
        self.progress_pct = 0.0
        
        self.window_name = "FacileTouch Virtual Keyboard"
        
        # Cấu hình khởi tạo cửa sổ tĩnh chống lag
        cv2.namedWindow(self.window_name, cv2.WINDOW_AUTOSIZE)
        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_TOPMOST, 1)
        # Tạm giấu ra ngoài vùng nhìn thấy lúc khởi chạy
        cv2.moveWindow(self.window_name, -2000, -2000)
        
        self.is_visible = False
        self.is_dragging_mode = False
        
        # Bộ nhớ theo dõi tọa độ thực tế tránh gọi trùng lặp hàm moveWindow gây lag chuột
        self.last_sent_x = -2000
        self.last_sent_y = -2000

    def check_dwell_clicking(self):
        """Kiểm tra cơ chế đứng im 2.0 giây để gõ phím hoặc di chuyển bàn phím ảo."""
        if not config.is_keyboard_open or config.system_state != "RUNNING":
            self.dwell_start_time = None
            self.is_dragging_mode = False
            if self.is_visible:
                cv2.moveWindow(self.window_name, -2000, -2000)
                self.last_sent_x, self.last_sent_y = -2000, -2000
                self.is_visible = False
            return

        # 🌟 TỐI ƯU CHỐNG LAG: Chỉ gọi moveWindow khi chuyển trạng thái hiển thị
        if not self.is_visible:
            cv2.moveWindow(self.window_name, self.kb_x, self.kb_y)
            self.last_sent_x, self.last_sent_y = self.kb_x, self.kb_y
            self.is_visible = True

        mx, my = pyautogui.position()
        current_time = time.time()
        
        # CHẾ ĐỘ KÉO THẢ DI CHUYỂN BÀN PHÍM
        if self.is_dragging_mode:
            new_x = int(mx - self.kb_w // 2)
            new_y = int(my - self.kb_h // 2)
            self.kb_x = max(0, min(new_x, config.SCREEN_WIDTH - self.kb_w))
            self.kb_y = max(0, min(new_y, config.SCREEN_HEIGHT - self.kb_h))
            
            # 🌟 TỐI ƯU CHỐNG LAG: Chỉ đẩy lệnh di chuyển lên HĐH nếu tọa độ thực sự thay đổi khác biệt
            if self.kb_x != self.last_sent_x or self.kb_y != self.last_sent_y:
                cv2.moveWindow(self.window_name, self.kb_x, self.kb_y)
                self.last_sent_x, self.last_sent_y = self.kb_x, self.kb_y
                
            self.draw_standalone_keyboard()
            return

        # 🌟 YÊU CẦU 4: SỬA LỖI HOVER LỆCH Ô - Lấy tọa độ vùng làm việc thực tế (Client Area) 
        # Trích xuất chính xác để bù trừ độ dày của thanh tiêu đề Title Bar và Borders hệ điều hành
        try:
            win_rect = cv2.getWindowImageRect(self.window_name)
            client_x, client_y, client_w, client_h = win_rect
        except:
            client_x, client_y, client_w, client_h = self.kb_x, self.kb_y, self.kb_w, self.kb_h

        # Kiểm tra xem con trỏ chuột thực tế có nằm chính xác trong lòng vùng phím vẽ hay không
        if not (client_x <= mx <= client_x + client_w and client_y <= my <= client_y + client_h):
            self.dwell_start_time = None
            self.current_hovered_key = None
            self.progress_pct = 0.0
            self.draw_standalone_keyboard()
            return

        # Tính toán phần trăm tọa độ tương đối đã loại bỏ hoàn toàn sai số viền cửa sổ
        rel_x = mx - client_x
        rel_y = my - client_y
        
        rows = len(config.KEYBOARD_LAYOUT)
        cols = len(config.KEYBOARD_LAYOUT[0])
        cell_w = client_w // cols
        cell_h = client_h // rows
        
        col_idx = min(rel_x // cell_w, cols - 1)
        row_idx = min(rel_y // cell_h, rows - 1)
        hovered_key = config.KEYBOARD_LAYOUT[row_idx][col_idx]

        dist = cv2.norm(np.array([mx, my]) - np.array(self.last_mouse_pos))
        
        if dist > config.DWELL_PIXEL_RADIUS or hovered_key != self.current_hovered_key:
            self.dwell_start_time = current_time
            self.current_hovered_key = hovered_key
            self.progress_pct = 0.0
        else:
            elapsed = current_time - self.dwell_start_time
            self.progress_pct = min(100.0, (elapsed / config.DWELL_DURATION) * 100.0)
            
            if elapsed >= config.DWELL_DURATION:
                if hovered_key == "MOVE":
                    self.is_dragging_mode = True
                    self.dwell_start_time = None
                    self.progress_pct = 0.0
                else:
                    self.trigger_key_press(hovered_key)
                    self.dwell_start_time = current_time 
                    self.progress_pct = 0.0

        self.last_mouse_pos = (mx, my)
        self.draw_standalone_keyboard()

    def trigger_key_press(self, key_text):
        """Giả lập gõ phím xuống Windows."""
        if key_text == "CLOSE":
            config.is_keyboard_open = False
        elif key_text == "SPACE":
            pyautogui.press("space")
        elif key_text == "BACKSPACE":
            pyautogui.press("backspace")
        elif key_text == "ENTER":
            pyautogui.press("enter")
        else:
            pyautogui.press(key_text.lower())

    def draw_standalone_keyboard(self):
        """Vẽ giao diện bàn phím lên cửa sổ nổi riêng biệt."""
        if not config.is_keyboard_open or not self.is_visible: return

        kb_frame = np.zeros((self.kb_h, self.kb_w, 3), dtype=np.uint8) + 20
        
        if self.is_dragging_mode:
            cv2.rectangle(kb_frame, (0, 0), (self.kb_w, self.kb_h), (0, 165, 255), 6)
            cv2.putText(kb_frame, "CHEDO DI CHUYEN: HA MOM (CLICK) NHE PHAT DE GHIM CO DINH TRANH LAG", (60, self.kb_h // 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 165, 255), 2, cv2.LINE_AA)
            cv2.imshow(self.window_name, kb_frame)
            return

        rows = len(config.KEYBOARD_LAYOUT)
        cols = len(config.KEYBOARD_LAYOUT[0])
        cell_w = self.kb_w // cols
        cell_h = self.kb_h // rows

        for r in range(rows):
            for c in range(cols):
                k_text = config.KEYBOARD_LAYOUT[r][c]
                x1 = c * cell_w
                y1 = r * cell_h
                x2 = x1 + cell_w
                y2 = y1 + cell_h
                
                if self.current_hovered_key == k_text:
                    cv2.rectangle(kb_frame, (x1, y1), (x2, y2), (0, 255, 170), -1)
                    bar_w = int((x2 - x1) * (self.progress_pct / 100.0))
                    cv2.rectangle(kb_frame, (x1, y2 - 10), (x1 + bar_w, y2 - 2), (0, 0, 255), -1)
                else:
                    cv2.rectangle(kb_frame, (x1, y1), (x2, y2), (60, 60, 60), 2)

                text_color = (0, 0, 0) if self.current_hovered_key == k_text else (255, 255, 255)
                if k_text == "MOVE":
                    text_color = (0, 165, 255) if self.current_hovered_key != k_text else (0, 0, 0)
                cv2.putText(kb_frame, k_text, (x1 + cell_w//2 - len(k_text)*8, y1 + cell_h//2 + 8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2, cv2.LINE_AA)

        cv2.imshow(self.window_name, kb_frame)

    def draw_overlay(self, frame):
        pass