# Class điều khiển chuột qua PyAutoGUI, map tọa độ camera ra màn hình

import pyautogui
import time
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FRAME_INNER_X1, FRAME_INNER_X2, FRAME_INNER_Y1, FRAME_INNER_Y2

pyautogui.FAILSAFE = False

class MouseController:
    def __init__(self, cooldown=1.2):
        self.last_click_time = 0
        self.cooldown = cooldown

    def move_to(self, x_norm, y_norm):
        # Chuyển đổi tọa độ vùng nhận diện ra tỷ lệ màn hình
        mapped_x = (x_norm - FRAME_INNER_X1) / (FRAME_INNER_X2 - FRAME_INNER_X1)
        mapped_y = (y_norm - FRAME_INNER_Y1) / (FRAME_INNER_Y2 - FRAME_INNER_Y1)
        
        screen_x = mapped_x * SCREEN_WIDTH
        screen_y = mapped_y * SCREEN_HEIGHT
        
        # Giới hạn biên màn hình an toàn
        screen_x = max(0, min(SCREEN_WIDTH - 1, screen_x))
        screen_y = max(0, min(SCREEN_HEIGHT - 1, screen_y))
        
        pyautogui.moveTo(screen_x, screen_y, duration=0.0)

    def click(self):
        current_time = time.time()
        if current_time - self.last_click_time > self.cooldown:
            pyautogui.click()
            self.last_click_time = current_time
            return True
        return False