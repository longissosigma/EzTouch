# virtual_keyboard.py
import cv2
import time
import pyautogui
import numpy as np
import config
import math

class VirtualKeyboard:
    def __init__(self):
        self.kb_w = 1100
        self.kb_h = 420
        self.kb_x = (config.SCREEN_WIDTH - self.kb_w) // 2
        self.kb_y = (config.SCREEN_HEIGHT - self.kb_h) // 2
        self.last_mouse_pos = (0, 0)
        self.dwell_start_time = None
        self.last_hovered_cell = (-1, -1)
        self.current_hovered_key = None
        self.progress_pct = 0.0
        self.window_name = "EzTouch Virtual Keyboard"
        self.is_visible = False
        self.is_dragging_mode = False
        self.is_window_created = False
        
        # 🌟 BỘ PHANH THỜI GIAN COOLDOWN CHỐNG TỰ KÍCH HOẠT LẠI LẬP TỨC
        self.last_drop_time = 0.0

    def check_dwell_clicking(self):
        if not config.is_keyboard_open or config.system_state != "RUNNING":
            self.dwell_start_time = None
            self.is_dragging_mode = False
            self.last_hovered_cell = (-1, -1)
            self.current_hovered_key = None
            if self.is_visible:
                try:
                    cv2.resizeWindow(self.window_name, 1, 1)
                    cv2.moveWindow(self.window_name, 0, 0)
                except:
                    pass
                self.is_visible = False
            return

        if not self.is_window_created:
            cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL | cv2.WINDOW_FREERATIO)
            cv2.setWindowProperty(self.window_name, cv2.WND_PROP_TOPMOST, 1)
            cv2.resizeWindow(self.window_name, 1, 1)
            cv2.moveWindow(self.window_name, 0, 0)
            self.is_window_created = True

        if not self.is_visible:
            cv2.resizeWindow(self.window_name, self.kb_w, self.kb_h)
            cv2.moveWindow(self.window_name, self.kb_x, self.kb_y)
            cv2.setWindowProperty(self.window_name, cv2.WND_PROP_TOPMOST, 1)
            self.is_visible = True

        mx, my = pyautogui.position()
        current_time = time.time()
        
        # 🌟 1. LUỒNG DỊCH CHUYỂN BÀN PHÍM THEO MŨI TRONG CHẾ ĐỘ DRAG MODE
        if self.is_dragging_mode:
            new_x = int(mx - self.kb_w // 2)
            new_y = int(my - self.kb_h // 2)
            self.kb_x = max(0, min(new_x, config.SCREEN_WIDTH - self.kb_w))
            self.kb_y = max(0, min(new_y, config.SCREEN_HEIGHT - self.kb_h))
            cv2.moveWindow(self.window_name, self.kb_x, self.kb_y)
            self.draw_standalone_keyboard()
            return

        try:
            win_rect = cv2.getWindowImageRect(self.window_name)
            client_x, client_y, client_w, client_h = win_rect
        except:
            client_x, client_y, client_w, client_h = self.kb_x, self.kb_y, self.kb_w, self.kb_h

        if not (client_x <= mx <= client_x + client_w and client_y <= my <= client_y + client_h):
            self.dwell_start_time = None
            self.current_hovered_key = None
            self.last_hovered_cell = (-1, -1)
            self.progress_pct = 0.0
            self.draw_standalone_keyboard()
            return

        rel_x = mx - client_x
        rel_y = my - client_y
        
        rows = len(config.KEYBOARD_LAYOUT)
        cols = len(config.KEYBOARD_LAYOUT[0])
        cell_w = client_w // cols
        cell_h = client_h // rows
        
        col_idx = min(rel_x // cell_w, cols - 1)
        row_idx = min(rel_y // cell_h, rows - 1)
        hovered_key = config.KEYBOARD_LAYOUT[row_idx][col_idx]

        # 🔥 BỘ CHẶN COOLDOWN: Nếu vừa ghim bàn phím xuống chưa quá 1.2 giây, 
        # khóa chết nút "MOVE" không cho phép tự động kích hoạt lại bậy bạ
        if hovered_key == "MOVE" and (current_time - self.last_drop_time < 1.2):
            self.dwell_start_time = None
            self.current_hovered_key = None
            self.last_hovered_cell = (-1, -1)
            self.progress_pct = 0.0
            self.draw_standalone_keyboard()
            return

        current_cell = (row_idx, col_idx)
        if current_cell != self.last_hovered_cell:
            self.dwell_start_time = current_time
            self.last_hovered_cell = current_cell
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

    def execute_active_mouth_type(self):
        """🌟 XỬ LÝ HÁ MỒM (CLICK CHỦ ĐỘNG) TRÊN BÀN PHÍM ẢO"""
        current_time = time.time()
        
        # 🔥 ĐÃ SỬA TRIỆT ĐỂ: Nếu đang kéo dịch chuyển, há mồm một phát (Click) 
        # là tắt dragging và chốt thời gian ghim 'last_drop_time' để kích hoạt bộ phanh khóa
        if self.is_dragging_mode:
            self.is_dragging_mode = False
            self.last_drop_time = current_time
            self.dwell_start_time = current_time
            self.progress_pct = 0.0
            self.current_hovered_key = None
            self.last_hovered_cell = (-1, -1)
            return True 

        if config.is_keyboard_open and self.current_hovered_key and not self.is_dragging_mode:
            if config.is_trial_active and config.trial_task_stage == 3 and not config.is_chat_input_focused:
                self.dwell_start_time = current_time
                self.progress_pct = 0.0
                return True 
                
            if self.current_hovered_key == "MOVE":
                # Chặn luôn click nhanh vào MOVE nếu đang trong thời gian xả phanh cooldown
                if current_time - self.last_drop_time < 1.2:
                    return True
                self.is_dragging_mode = True
            else:
                self.trigger_key_press(self.current_hovered_key)
            self.dwell_start_time = current_time
            self.progress_pct = 0.0
            return True
        return False

    def trigger_key_press(self, key_text):
        if key_text == "CLOSE":
            config.is_keyboard_open = False
            return

        if config.is_trial_active and config.trial_task_stage == 3 and not config.is_chat_input_focused:
            return 

        if key_text == "SPACE":
            pyautogui.press("space")
        elif key_text == "BACKSPACE":
            pyautogui.press("backspace")
        elif key_text == "ENTER":
            pyautogui.press("enter")
        else:
            pyautogui.press(key_text.lower())

    def draw_standalone_keyboard(self):
        if not config.is_keyboard_open or not self.is_visible: return

        kb_frame = np.zeros((self.kb_h, self.kb_w, 3), dtype=np.uint8) + 20
        
        if self.is_dragging_mode:
            cv2.rectangle(kb_frame, (0, 0), (self.kb_w, self.kb_h), (0, 165, 255), 6)
            instruct_text = "CHEDO DI CHUYEN: HA MOM (CLICK) 1 CAI DE CO DINH BAN PHIM TAI DAY"
            cv2.putText(kb_frame, instruct_text, (50, self.kb_h // 2 + 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 165, 255), 2, cv2.LINE_AA)
            cv2.imshow(self.window_name, kb_frame)
            return

        if config.is_trial_active and config.trial_task_stage == 3 and not config.is_chat_input_focused:
            cv2.rectangle(kb_frame, (0, 0), (self.kb_w, self.kb_h), (0, 0, 240), 6)
            warn_str = "BAN CHUA NHAP VAO O NHAN TIN NE, HAY NHAP VAO ROI MOI GO CHU NHE!"
            cv2.putText(kb_frame, warn_str, (45, self.kb_h // 2 + 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2, cv2.LINE_AA)
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