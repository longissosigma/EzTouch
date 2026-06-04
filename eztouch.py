# eztouch.py
import sys
import os
from PySide6.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, 
                               QHBoxLayout, QLabel, QGraphicsDropShadowEffect)
from PySide6.QtCore import QThread, Qt, QTimer
from PySide6.QtGui import QColor

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import main
import config

class FaceThread(QThread):
    def run(self):
        main.main()  # Khởi chạy lõi xử lý AI

# =========================================================
# 🌟 THANH CÔNG CỤ DỌC PHÓNG TO TRỢ NĂNG (ACCESSIBILITY TOOLBAR)
# =========================================================
class EzTouchSideToolbar(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |     # Găm cứng lên trên cùng mọi ứng dụng
            Qt.FramelessWindowHint |      # Ẩn viền cửa sổ
            Qt.Tool                       # Ẩn icon taskbar
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.is_expanded = True  
        self.init_ui()
        self.update_position()

    def init_ui(self):
        self.outer_layout = QHBoxLayout()
        self.outer_layout.setContentsMargins(0, 0, 0, 0)
        self.outer_layout.setSpacing(0)
        
        # --- PHÓNG TO CHIỀU RỘNG LÊN 90PX GIÚP TRẺ EM VÀ NGƯỜI GIÀ DỄ CLICK ---
        self.toolbar_body = QWidget()
        self.toolbar_body.setFixedWidth(90)
        self.toolbar_body.setStyleSheet(
            "QWidget {"
            "    background-color: #F3F6FA;"
            "    border: 2px solid #3182CE;"
            "    border-top-right-radius: 18px;"
            "    border-bottom-right-radius: 18px;"
            "}"
        )
        
        body_layout = QVBoxLayout(self.toolbar_body)
        body_layout.setContentsMargins(6, 20, 6, 20)
        body_layout.setSpacing(15)
        
        # 🌟 NÚT 1: CHUYỂN ĐỔI CHẾ ĐỘ PAUSE / RESUME ĐỘNG
        self.btn_toggle_pause = QPushButton()
        self.btn_toggle_pause.setFixedSize(76, 76) # Tăng kích thước nút rõ ràng
        self.btn_toggle_pause.setCursor(Qt.PointingHandCursor)
        self.btn_toggle_pause.clicked.connect(self.handle_pause_click)
        
        # 🌟 NÚT 2: BẬT/TẮT BÀN PHÍM ẢO (KB ON / OFF)
        self.btn_toggle_keyboard = QPushButton()
        self.btn_toggle_keyboard.setFixedSize(76, 76) # Tăng kích thước nút rõ ràng
        self.btn_toggle_keyboard.setCursor(Qt.PointingHandCursor)
        self.btn_toggle_keyboard.clicked.connect(self.handle_keyboard_click)
        
        body_layout.addWidget(self.btn_toggle_pause)
        body_layout.addWidget(self.btn_toggle_keyboard)
        
        # Nút tay cầm thụt thò điều hướng mở rộng
        self.btn_slide_handle = QPushButton("◀")
        self.btn_slide_handle.setFixedSize(22, 70)
        self.btn_slide_handle.setCursor(Qt.PointingHandCursor)
        self.btn_slide_handle.setStyleSheet(
            "QPushButton {"
            "    background-color: #3182CE;"
            "    color: #FFFFFF;"
            "    border: none;"
            "    border-top-right-radius: 10px;"
            "    border-bottom-right-radius: 10px;"
            "    font-weight: bold;"
            "    font-size: 12px;"
            "}"
            "QPushButton:hover { background-color: #4299E1; }"
        )
        self.btn_slide_handle.clicked.connect(self.toggle_collapse)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(2, 2)
        shadow.setColor(QColor(0, 0, 0, 45))
        self.setGraphicsEffect(shadow)
        
        self.outer_layout.addWidget(self.toolbar_body)
        self.outer_layout.addWidget(self.btn_slide_handle)
        self.setLayout(self.outer_layout)
        
        self.update_button_styles()

    def update_position(self):
        """Chốt tâm cố định chính giữa cạnh rìa màn hình bên trái."""
        total_w = 112 if self.is_expanded else 22
        total_h = 210
        pos_x = 0
        pos_y = (config.SCREEN_HEIGHT - total_h) // 2
        self.setGeometry(pos_x, pos_y, total_w, total_h)

    def update_button_styles(self):
        """Cập nhật giao diện nút bấm theo máy trạng thái động."""
        # Kiểm tra trạng thái Pause / Resume toàn cục từ config
        if config.system_state == "PAUSED":
            self.btn_toggle_pause.setText("RESUME")
            self.btn_toggle_pause.setStyleSheet(
                "QPushButton {"
                "    background-color: #3182CE; color: white; font-size: 12px;"
                "    font-weight: bold; border-radius: 16px; border: none;"
                "}"
                "QPushButton:hover { background-color: #4299E1; }"
            )
        else: # Trạng thái RUNNING hoặc SLEEP
            self.btn_toggle_pause.setText("PAUSE")
            self.btn_toggle_pause.setStyleSheet(
                "QPushButton {"
                "    background-color: #E53E3E; color: white; font-size: 12px;"
                "    font-weight: bold; border-radius: 16px; border: none;"
                "}"
                "QPushButton:hover { background-color: #FC8181; }"
            )
            
        # Đồng bộ trạng thái phím ảo KB
        if not config.is_keyboard_open:
            self.btn_toggle_keyboard.setText("KB ON")
            self.btn_toggle_keyboard.setStyleSheet(
                "QPushButton {"
                "    background-color: #4A5568; color: white; font-size: 12px;"
                "    font-weight: bold; border-radius: 16px; border: none;"
                "}"
                "QPushButton:hover { background-color: #718096; }"
            )
        else:
            self.btn_toggle_keyboard.setText("KB OFF")
            self.btn_toggle_keyboard.setStyleSheet(
                "QPushButton {"
                "    background-color: #ED8936; color: white; font-size: 12px;"
                "    font-weight: bold; border-radius: 16px; border: none;"
                "}"
                "QPushButton:hover { background-color: #F6AD55; }"
            )

    def handle_pause_click(self):
        """Điều khiển trạng thái hoạt động trực tiếp thông qua config máy trạng thái."""
        if self.main_app.is_engine_running:
            if config.system_state == "RUNNING":
                config.system_state = "PAUSED"
            elif config.system_state == "PAUSED":
                config.system_state = "RUNNING"
            self.update_button_styles()

    def handle_keyboard_click(self):
        if self.main_app.is_engine_running and config.system_state == "RUNNING":
            config.is_keyboard_open = not config.is_keyboard_open
            self.update_button_styles()

    def toggle_collapse(self):
        self.is_expanded = not self.is_expanded
        if self.is_expanded:
            self.toolbar_body.show()
            self.btn_slide_handle.setText("◀")
        else:
            self.toolbar_body.hide()
            self.btn_slide_handle.setText("▶")
        self.update_position()


# =========================================================
# TAB KHỞI CHẠY GỐC (GIỮ NGUYÊN KIẾN TRÚC)
# =========================================================
class EzTouchApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EzTouch - Thắp Sáng Thế Giới Riêng")
        self.setFixedSize(560, 420)
        
        self.setStyleSheet(
            "QWidget {"
            "    background-color: #F3F6FA;"
            "    color: #2D3748;"
            "    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;"
            "}"
        )

        self.face_thread = None
        self.is_engine_running = False
        self.init_ui()
        
        # Khởi tạo thanh công cụ dọc trợ năng bám dính
        self.side_toolbar = EzTouchSideToolbar(self)
        self.side_toolbar.show()
        
        # Timer đồng bộ đa luồng liên tục
        self.sync_timer = QTimer(self)
        self.sync_timer.setInterval(200)
        self.sync_timer.timeout.connect(self.sync_ui_states)
        self.sync_timer.start()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 35, 40, 35)
        main_layout.setSpacing(10)

        title_label = QLabel("EzTouch")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(
            "QLabel {"
            "    font-size: 46px; font-weight: 850; letter-spacing: -0.5px;"
            "    color: #3182CE; background: transparent; border: none;"
            "}"
        )
        
        team_label = QLabel("by SigmaCode")
        team_label.setAlignment(Qt.AlignCenter)
        team_label.setStyleSheet(
            "QLabel {"
            "    font-size: 13px; font-weight: 600; font-style: italic;"
            "    letter-spacing: 3px; color: #4A5568; margin-top: -5px;"
            "    margin-bottom: 5px; background: transparent; border: none;"
            "}"
        )
        
        subtitle_label = QLabel("HỆ THỐNG ĐIỀU KHIỂN CHUỘT MÁY TÍNH BẰNG KHUÔN MẶT")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet(
            "QLabel {"
            "    font-size: 10px; font-weight: 700; letter-spacing: 1.5px;"
            "    color: #718096; background: transparent; border: none;"
            "}"
        )

        self.action_button = QPushButton("BẮT ĐẦU CHƠI THÔI!")
        self.action_button.setCursor(Qt.PointingHandCursor)
        self.action_button.setFixedHeight(95)
        
        self.btn_shadow = QGraphicsDropShadowEffect()
        self.btn_shadow.setBlurRadius(30)
        self.btn_shadow.setOffset(0, 10)
        self.btn_shadow.setColor(QColor(49, 130, 206, 60))
        self.action_button.setGraphicsEffect(self.btn_shadow)
        
        self.update_button_style()
        self.action_button.clicked.connect(self.handle_engine_toggle)

        status_footer = QLabel("“Từ những vệt sáng cuối trời, thắp sáng những thế giới riêng”")
        status_footer.setAlignment(Qt.AlignCenter)
        status_footer.setStyleSheet(
            "QLabel {"
            "    font-size: 13px; font-weight: 500; color: #4A5568;"
            "    font-style: italic; background: transparent; border: none; margin-top: 15px;"
            "}"
        )

        main_layout.addWidget(title_label)
        main_layout.addWidget(team_label)
        main_layout.addWidget(subtitle_label)
        main_layout.addStretch()
        main_layout.addWidget(self.action_button)
        main_layout.addStretch()
        main_layout.addWidget(status_footer)
        
        self.setLayout(main_layout)

    def update_button_style(self):
        if not self.is_engine_running:
            self.action_button.setText("KÍCH HOẠT EZTOUCH")
            self.action_button.setStyleSheet(
                "QPushButton { font-size: 20px; font-weight: 700; color: #FFFFFF; background-color: #3182CE; border: none; border-radius: 20px; }"
                "QPushButton:hover { background-color: #4299E1; }"
                "QPushButton:pressed { background-color: #2B6CB0; padding-top: 6px; }"
            )
            if hasattr(self, 'btn_shadow'):
                self.btn_shadow.setColor(QColor(49, 130, 206, 60))
        else:
            self.action_button.setText("DỪNG HỆ THỐNG")
            self.action_button.setStyleSheet(
                "QPushButton { font-size: 20px; font-weight: 700; color: #FFFFFF; background-color: #E53E3E; border: none; border-radius: 20px; }"
                "QPushButton:hover { background-color: #FC8181; }"
                "QPushButton:pressed { background-color: #C53030; padding-top: 6px; }"
            )
            if hasattr(self, 'btn_shadow'):
                self.btn_shadow.setColor(QColor(229, 62, 62, 60))

    def sync_ui_states(self):
        """Đồng bộ hóa giao diện đa luồng realtime."""
        if hasattr(self, 'side_toolbar'):
            self.side_toolbar.update_button_styles()
            self.update_button_style()

    def handle_engine_toggle(self):
        if not self.is_engine_running:
            if self.face_thread is None or not self.face_thread.isRunning():
                self.face_thread = FaceThread()
                self.face_thread.start()
                self.is_engine_running = True
                self.update_button_style()
                self.setWindowState(Qt.WindowMinimized)
        else:
            if self.face_thread and self.face_thread.isRunning():
                main.stop_system()
                self.face_thread.wait()
                self.is_engine_running = False
                config.system_state = "RUNNING" # Trả về trạng thái mặc định khi tắt hẳn
                self.update_button_style()

    def closeEvent(self, event):
        if hasattr(self, 'side_toolbar'):
            self.side_toolbar.close()
        if self.face_thread and self.face_thread.isRunning():
            main.stop_system()
            self.face_thread.wait()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EzTouchApp()
    window.show()
    sys.exit(app.exec())