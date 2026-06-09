# eztouch.py
import sys
import os
import cv2
import numpy as np
from PySide6.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, 
                               QHBoxLayout, QLabel, QGraphicsDropShadowEffect, 
                               QStackedWidget, QTextEdit, QLineEdit, QProgressBar)
from PySide6.QtCore import QThread, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QPixmap, QImage

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

from core import main
from core import config

class FaceThread(QThread):
    def run(self):
        main.main()  

# =========================================================================
# 🕹️ KIỆT TÁC CSS: 3D MECHANICAL ARCADE SWITCH (CYBER-PUNK PREMIUM)
# =========================================================================
STYLE_BLUE_BUTTON = """
    QPushButton {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1e293b, stop:1 #020617); 
        color: #38bdf8; 
        font-family: 'Consolas', 'Segoe UI', monospace;
        font-weight: 900;
        border-top: 3px solid #7dd3fc;
        border-left: 3px solid #38bdf8;
        border-right: 3px solid #1d4ed8;
        border-bottom: 6px solid #1e3a8a; 
        border-radius: 16px;
        padding: 14px;
    }
    QPushButton:hover { 
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0f172a, stop:1 #1e293b);
        color: #ffffff; 
        border-top: 3px solid #ffffff;
        border-left: 3px solid #38bdf8;
        border-right: 3px solid #38bdf8;
        border-bottom: 6px solid #38bdf8;
    }
    QPushButton:pressed { 
        background-color: #020617;
        color: #38bdf8;
        border-top: 5px solid #1e3a8a;
        border-left: 3px solid #1e3a8a;
        border-right: 3px solid #1e3a8a;
        border-bottom: 1px solid #1e3a8a;
        padding-top: 18px;
        padding-bottom: 10px;
    }
    QPushButton:disabled {
        background-color: #1e293b; color: #475569; border: 2px solid #475569;
    }
"""

STYLE_ORANGE_BUTTON = """
    QPushButton {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2e1065, stop:1 #020617); 
        color: #c084fc; 
        font-family: 'Consolas', 'Segoe UI', monospace;
        font-weight: 900;
        border-top: 3px solid #f3e8ff;
        border-left: 3px solid #c084fc;
        border-right: 3px solid #7e22ce;
        border-bottom: 6px solid #581c87; 
        border-radius: 16px;
        padding: 14px;
    }
    QPushButton:hover { 
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #020617, stop:1 #2e1065);
        color: #ffffff; 
        border-top: 3px solid #ffffff;
        border-left: 3px solid #c084fc;
        border-right: 3px solid #c084fc;
        border-bottom: 6px solid #c084fc;
    }
    QPushButton:pressed { 
        background-color: #020617;
        color: #c084fc;
        border-top: 5px solid #581c87;
        border-left: 3px solid #581c87;
        border-right: 3px solid #581c87;
        border-bottom: 1px solid #581c87;
        padding-top: 18px;
        padding-bottom: 10px;
    }
"""

STYLE_TOOLBAR_PAUSE = """
    QPushButton {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #450a0a, stop:1 #020617); 
        color: #f87171; font-size: 15px; font-weight: bold; font-family: 'Consolas', monospace;
        border-top: 2px solid #fca5a5; border-left: 2px solid #f87171; border-right: 2px solid #dc2626; border-bottom: 5px solid #991b1b;
        border-radius: 16px;
    }
    QPushButton:hover { background-color: #f87171; color: #020617; border: 2px solid #ffffff; }
    QPushButton:pressed { border-top: 4px solid #991b1b; border-bottom: 1px solid #991b1b; padding-top: 2px; }
"""

STYLE_TOOLBAR_RESUME = """
    QPushButton {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1e293b, stop:1 #020617); 
        color: #38bdf8; font-size: 15px; font-weight: bold; font-family: 'Consolas', monospace;
        border-top: 2px solid #56ccf2; border-left: 2px solid #38bdf8; border-right: 2px solid #2563eb; border-bottom: 5px solid #1d4ed8;
        border-radius: 16px;
    }
    QPushButton:hover { background-color: #38bdf8; color: #020617; border: 2px solid #ffffff; }
    QPushButton:pressed { border-top: 4px solid #1d4ed8; border-bottom: 1px solid #1d4ed8; padding-top: 2px; }
"""

def get_transparent_logo_pixmap(image_path, target_height):
    if not os.path.exists(image_path):
        return QPixmap()
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        return QPixmap()
    if img.shape[2] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    alpha_channel = img[:, :, 3]
    pts = cv2.findNonZero(alpha_channel)
    if pts is not None:
        x, y, w, h = cv2.boundingRect(pts)
        pad = 6
        y1 = max(0, y - pad)
        y2 = min(img.shape[0], y + h + pad)
        x1 = max(0, x - pad)
        x2 = min(img.shape[1], x + w + pad)
        img = img[y1:y2, x1:x2]
    img = np.ascontiguousarray(img)
    height, width, channel = img.shape
    bytes_per_line = channel * width
    q_img = QImage(img.data, width, height, bytes_per_line, QImage.Format_RGBA8888).rgbSwapped()
    base_pixmap = QPixmap.fromImage(q_img)
    return base_pixmap.scaledToHeight(target_height, Qt.SmoothTransformation)


class EzTouchTrialSpace(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.setWindowTitle("EzTouch // Trial_System_Terminal")
        self.setWindowFlags(Qt.Window) 
        self.showMaximized() 
        
        self.setStyleSheet("""
            QWidget {
                background-color: #090d16; color: #cbd5e1;
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            }
            QLabel { background: transparent; }
        """)
        
        self.has_triggered_pause = False
        self.init_ui()
        
        self.trial_timer = QTimer(self)
        self.trial_timer.setInterval(100)
        self.trial_timer.timeout.connect(self.monitor_user_actions)
        self.trial_timer.start()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(60, 30, 60, 30)
        self.layout.setSpacing(15)
        
        self.header_title_label = QLabel("Chào mừng đến với cơ chế trải nghiệm của EzTouch ;)")
        self.header_title_label.setAlignment(Qt.AlignCenter)
        self.header_title_label.setStyleSheet("""
            QLabel {
                font-size: 26px; 
                font-weight: 900; 
                color: #38bdf8; 
                letter-spacing: 1px;
                padding-top: 10px;
                font-family: 'Consolas', monospace;
            }
        """)
        self.layout.addWidget(self.header_title_label)

        self.overall_progress = QProgressBar()
        self.overall_progress.setRange(0, 100)
        self.overall_progress.setValue(0)
        self.overall_progress.setFixedHeight(12)
        self.overall_progress.setStyleSheet("""
            QProgressBar { 
                background-color: #020617; 
                border: 2px solid #1e293b;
                border-radius: 6px; 
                text-align: center; 
                font-size: 10px;
                font-weight: bold; 
                color: #38bdf8; 
            }
            QProgressBar::chunk { 
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #38bdf8, stop:1 #c084fc); 
                border-radius: 4px;
            }
        """)
        self.layout.addWidget(self.overall_progress)
        
        self.stack = QStackedWidget()
        self.layout.addWidget(self.stack)
        
        self.setup_page_intro()
        self.setup_page_task1()
        self.setup_page_task2()
        self.setup_page_task3()
        self.setup_page_task4()
        self.setup_page_finish()
        
        self.btn_exit_trial = QPushButton("TERMINATE_TRIAL // DISCONNECT_")
        self.btn_exit_trial.setFixedWidth(280)
        self.btn_exit_trial.setStyleSheet(STYLE_BLUE_BUTTON.replace("padding: 14px;", "padding: 8px; font-size: 13px; border-radius: 10px;"))
        self.btn_exit_trial.clicked.connect(self.exit_trial)
        self.layout.addWidget(self.btn_exit_trial, alignment=Qt.AlignRight)

    def setup_page_intro(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        
        intro_card = QWidget()
        intro_card.setFixedSize(840, 520) 
        # 👑 NÂNG CẤP THỊ GIÁC: Đổi sang màu nền siêu tương phản cao giúp chữ hướng dẫn nổi bật kịch trần
        intro_card.setStyleSheet("QWidget { background-color: #020617; border: 2px solid #334155; border-radius: 20px; }")
        
        card_shadow = QGraphicsDropShadowEffect()
        card_shadow.setBlurRadius(35)
        card_shadow.setColor(QColor(56, 189, 248, 30))
        intro_card.setGraphicsEffect(card_shadow)
        
        card_layout = QVBoxLayout(intro_card)
        card_layout.setContentsMargins(45, 30, 45, 30)
        card_layout.setSpacing(15)

        self.welcome_logo_label = QLabel()
        self.welcome_logo_label.setAlignment(Qt.AlignCenter)
        logo_pixmap = get_transparent_logo_pixmap("picture/workmark.png", 90)
        if not logo_pixmap.isNull():
            self.welcome_logo_label.setPixmap(logo_pixmap)
        
        lbl_author = QLabel("> PROTOCOL_AUTHOR: EZ_TEAM_")
        lbl_author.setAlignment(Qt.AlignCenter)
        lbl_author.setStyleSheet("font-size: 14px; font-weight: bold; color: #c084fc; letter-spacing: 2px; font-family: 'Consolas';")
        
        lbl_mission = QLabel(
            "// MISSION_OBJECTIVE:\n"
            "EzTouch ra đời nhằm mục đích xóa bỏ rào cản số, mang không gian công nghệ\n"
            "đến gần hơn với trẻ em khuyết tật vận động chi trên và người cao tuổi mắc chứng bệnh run vô thức.\n"
            "Chúng tôi tin rằng từ những vệt sáng cuối trời, mọi thế giới riêng đều xứng đáng được thắp sáng."
        )
        # 👑 HIGH-READABILITY TYPOGRAPHY: SỬ DỤNG FONT CHỮ DÀY VỚI ĐỘ CO GIÃN SANG TRỌNG, DỄ ĐỌC TUYỆT ĐỐI
        lbl_mission.setStyleSheet("font-size: 15px; font-weight: 600; line-height: 165%; color: #f1f5f9; text-align: center; font-family: 'Segoe UI', -apple-system, sans-serif;")
        lbl_mission.setAlignment(Qt.AlignCenter)

        self.calibration_panel = QWidget()
        self.calibration_panel.setStyleSheet("QWidget { background-color: #090d16; border-radius: 14px; border: 2px solid #1e293b; }")
        
        panel_layout = QVBoxLayout(self.calibration_panel)
        panel_layout.setContentsMargins(30, 20, 30, 20)
        panel_layout.setSpacing(10)
        
        self.lbl_calib_title = QLabel("🔮 [NEURAL_BIOMETRIC_CALIBRATION]")
        self.lbl_calib_title.setStyleSheet("font-size: 14px; font-weight: 800; color: #38bdf8; border: none; font-family: 'Consolas';")
        self.lbl_calib_title.setAlignment(Qt.AlignCenter)
        
        self.lbl_calib_status = QLabel("> Vui lòng nghiêng nhẹ đầu sang TRÁI để chọn chế độ bảo vệ chống run,\nhoặc nghiêng đầu sang PHẢI để chọn chế độ lướt siêu tốc.")
        self.lbl_calib_status.setStyleSheet("font-size: 14px; font-weight: 600; color: #cbd5e1; line-height: 150%; border: none; font-family: 'Segoe UI';")
        self.lbl_calib_status.setAlignment(Qt.AlignCenter)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setStyleSheet("""
            QProgressBar { background-color: #020617; border-radius: 4px; border: none; }
            QProgressBar::chunk { background-color: #38bdf8; }
        """)
        
        self.lbl_countdown = QLabel("⏱️ SYNC_STREAM: Đang đồng bộ tín hiệu mốc khuôn mặt thông minh...")
        self.lbl_countdown.setStyleSheet("font-size: 13px; font-weight: 700; color: #c084fc; border: none; font-family: 'Consolas';")
        self.lbl_countdown.setAlignment(Qt.AlignCenter)
        
        panel_layout.addWidget(self.lbl_calib_title)
        panel_layout.addWidget(self.lbl_calib_status)
        panel_layout.addWidget(self.progress_bar)
        panel_layout.addWidget(self.lbl_countdown)
        
        self.btn_start_onboarding = QPushButton("INITIALIZE_LINK_START_▶")
        self.btn_start_onboarding.setFixedSize(360, 50)
        self.btn_start_onboarding.setEnabled(False) 
        self.btn_start_onboarding.setStyleSheet("background-color: #0f172a; color: #475569; font-size: 15px; font-weight: bold; border: 2px solid #475569; border-radius: 12px;")
        self.btn_start_onboarding.clicked.connect(self.handle_intro_finished)
        
        card_layout.addWidget(self.welcome_logo_label, alignment=Qt.AlignCenter)
        card_layout.addWidget(lbl_author, alignment=Qt.AlignCenter)
        card_layout.addWidget(lbl_mission, alignment=Qt.AlignCenter)
        card_layout.addWidget(self.calibration_panel)
        card_layout.addWidget(self.btn_start_onboarding, alignment=Qt.AlignCenter)
        
        layout.addWidget(intro_card, alignment=Qt.AlignCenter)
        self.stack.addWidget(page)

    def setup_page_task1(self):
        self.page1 = QWidget()
        self.layout1 = QVBoxLayout(self.page1)
        self.layout1.setAlignment(Qt.AlignCenter)
        
        task_card = QWidget()
        task_card.setFixedSize(840, 520) 
        task_card.setStyleSheet("QWidget { background-color: #020617; border: 2px solid #334155; border-radius: 20px; }")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(56, 189, 248, 20))
        task_card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(task_card)
        card_layout.setContentsMargins(45, 35, 45, 35)
        card_layout.setSpacing(10)
        
        self.lbl_guide1 = QLabel("> TASK_01 // ACTIVE_BIOMETRIC_CLICK_PROTOCOL")
        self.lbl_guide1.setStyleSheet("font-size: 18px; font-weight: 800; color: #38bdf8; font-family: 'Consolas';")
        self.lbl_guide1.setAlignment(Qt.AlignCenter)
        
        self.lbl_sub_guide1 = QLabel("Bạn hãy di chuyển mũi sao cho con trỏ chuột di chuyển đến cái nút ma trận cơ khí ở góc khung.")
        self.lbl_sub_guide1.setStyleSheet("font-size: 15px; font-weight: 600; color: #e2e8f0; font-family: 'Segoe UI';")
        self.lbl_sub_guide1.setAlignment(Qt.AlignCenter)
        
        self.click_area = QWidget()
        area_layout = QHBoxLayout(self.click_area)
        area_layout.setContentsMargins(0, 0, 0, 0)
        
        self.target_btn = QPushButton("HIT_ME_PRO //\n[ HÁ MỒM ]")
        self.target_btn.setFixedSize(190, 105)
        self.target_btn.setStyleSheet(STYLE_ORANGE_BUTTON)
        self.target_btn.clicked.connect(self.handle_task1_success)
        area_layout.addWidget(self.target_btn, alignment=Qt.AlignRight | Qt.AlignBottom)
        
        self.btn_next1 = QPushButton("NEXT_PHASE_TASK_02_▶")
        self.btn_next1.setFixedWidth(290)
        self.btn_next1.setStyleSheet(STYLE_BLUE_BUTTON)
        self.btn_next1.hide()
        self.btn_next1.clicked.connect(lambda: self.go_to_stage(2))
        
        card_layout.addWidget(self.lbl_guide1)
        card_layout.addWidget(self.lbl_sub_guide1)
        card_layout.addWidget(self.click_area)
        card_layout.addWidget(self.btn_next1, alignment=Qt.AlignCenter)
        
        self.layout1.addWidget(task_card, alignment=Qt.AlignCenter)
        self.stack.addWidget(self.page1)

    def setup_page_task2(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        
        task_card = QWidget()
        task_card.setFixedSize(840, 520) 
        task_card.setStyleSheet("QWidget { background-color: #020617; border: 2px solid #334155; border-radius: 20px; }")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(56, 189, 248, 20))
        task_card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(task_card)
        card_layout.setContentsMargins(45, 35, 45, 35)
        card_layout.setSpacing(10)
        
        self.lbl_guide2 = QLabel("> TASK_02 // SYSTEM_PAGE_SCROLL_MATRIX")
        self.lbl_guide2.setStyleSheet("font-size: 18px; font-weight: 800; color: #38bdf8; font-family: 'Consolas';")
        self.lbl_guide2.setAlignment(Qt.AlignCenter)
        
        self.lbl_sub_guide2 = QLabel("👉 Há mồm và giữ im đó trong vòng 1.3 giây để kích hoạt Vector cuộn.")
        self.lbl_sub_guide2.setStyleSheet("font-size: 15px; color: #f87171; font-weight: 800; font-family: 'Segoe UI';")
        self.lbl_sub_guide2.setAlignment(Qt.AlignCenter)
        
        self.news_text = QTextEdit()
        self.news_text.setReadOnly(True)
        self.news_text.setFont(QFont("Consolas", 11))
        self.news_text.setPlainText(
            "Há mồm trong 2 giây để bật tính năng cuộn trang - sau đó ngửa lên và cúi xuống để di chuyển\n\n" +
            "Nghiên cứu chỉ ra rằng việc tương tác không tiếp xúc hỗ trợ bệnh nhân Parkinson phục hồi chức năng hành vi phản xạ rất tốt.\n" +
            "Hệ thống định vị mốc nhân trắc học khuôn mặt cho phép bắt chuẩn xác chuyển động đỉnh mũi...\n" +
            "Để đọc thêm thông tin chi tiết, người dùng cần học cách cuộn trang mà không dùng tay.\n" +
            "Tiến trình cuộn trang sử dụng vector gia tốc tuyến tính âm đè lớp của PyAutoGUI.\n" * 45 +
            "\n--- BẠN ĐÃ CUỘN ĐẾN CUỐI TRANG THÀNH CÔNG RỒI! ---"
        )
        self.news_text.setStyleSheet("""
            QTextEdit { 
                background-color: #090d16; 
                border: 2px solid #1e293b; 
                border-radius: 12px; 
                padding: 15px; 
                color: #f1f5f9;
            }
        """)
        
        self.btn_next2 = QPushButton("NEXT_PHASE_TASK_03_▶")
        self.btn_next2.setFixedWidth(290)
        self.btn_next2.setStyleSheet(STYLE_BLUE_BUTTON)
        self.btn_next2.hide()
        self.btn_next2.clicked.connect(lambda: self.go_to_stage(3))
        
        card_layout.addWidget(self.lbl_guide2)
        card_layout.addWidget(self.lbl_sub_guide2)
        card_layout.addWidget(self.news_text)
        card_layout.addWidget(self.btn_next2, alignment=Qt.AlignCenter)
        
        layout.addWidget(task_card, alignment=Qt.AlignCenter)
        self.stack.addWidget(page)

    def setup_page_task3(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        
        task_card = QWidget()
        task_card.setFixedSize(840, 520) 
        task_card.setStyleSheet("QWidget { background-color: #020617; border: 2px solid #334155; border-radius: 20px; }")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(56, 189, 248, 20))
        task_card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(task_card)
        card_layout.setContentsMargins(45, 35, 45, 35)
        card_layout.setSpacing(15) 
        
        self.lbl_guide3 = QLabel("> TASK_03 // NEURAL_MATRIX_KEYBOARD_LINK")
        self.lbl_guide3.setStyleSheet("font-size: 18px; font-weight: 800; color: #38bdf8; font-family: 'Consolas';")
        self.lbl_guide3.setAlignment(Qt.AlignCenter)
        
        self.lbl_sub_guide3 = QLabel("Hãy nhấp (há mồm nhanh) vào ô nhắn tin Messenger giả lập bên dưới.")
        self.lbl_sub_guide3.setStyleSheet("font-size: 15px; font-weight: 600; color: #e2e8f0; font-family: 'Segoe UI';")
        self.lbl_sub_guide3.setAlignment(Qt.AlignCenter)
        
        self.input_container = QWidget()
        input_layout = QVBoxLayout(self.input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("SYS_INPUT: Nhấp vào đây để soạn dữ liệu chat...")
        self.chat_input.setMinimumHeight(56)
        self.chat_input.setFont(QFont("Consolas", 12))
        self.chat_input.setStyleSheet("""
            QLineEdit { 
                background-color: #090d16; 
                border: 2px solid #1e293b; 
                border-radius: 12px; 
                padding-left: 15px;
                color: #38bdf8;
            }
            QLineEdit:focus {
                border-color: #c084fc;
                background-color: #0f172a;
            }
        """)
        self.chat_input.clicked_connect_flag = False
        self.chat_input.cursorPositionChanged.connect(self.handle_chat_input_focused)
        input_layout.addWidget(self.chat_input, alignment=Qt.AlignVertical)
        
        self.btn_next3 = QPushButton("NEXT_PHASE_TASK_04_▶")
        self.btn_next3.setFixedWidth(290)
        self.btn_next3.setStyleSheet(STYLE_BLUE_BUTTON)
        self.btn_next3.hide()
        self.btn_next3.clicked.connect(lambda: self.go_to_stage(4))
        
        card_layout.addWidget(self.lbl_guide3)
        card_layout.addWidget(self.lbl_sub_guide3)
        card_layout.addStretch(1) 
        card_layout.addWidget(self.input_container)
        card_layout.addStretch(1)
        card_layout.addWidget(self.btn_next3, alignment=Qt.AlignCenter)
        
        layout.addWidget(task_card, alignment=Qt.AlignCenter)
        self.stack.addWidget(page)

    def setup_page_task4(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        
        task_card = QWidget()
        task_card.setFixedSize(840, 520) 
        task_card.setStyleSheet("QWidget { background-color: #020617; border: 2px solid #334155; border-radius: 20px; }")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(56, 189, 248, 20))
        task_card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(task_card)
        card_layout.setContentsMargins(45, 35, 45, 35)
        card_layout.setSpacing(15)
        
        self.lbl_guide4 = QLabel("> TASK_04 // INTERRUPT_CORE_PROTOCOL (PAUSE)")
        self.lbl_guide4.setStyleSheet("font-size: 18px; font-weight: 800; color: #38bdf8; font-family: 'Consolas';")
        self.lbl_guide4.setAlignment(Qt.AlignCenter)
        
        self.lbl_sub_guide4 = QLabel("Khi bạn muốn nghỉ ngơi hãy ấn vào nút 'PAUSE' màu đỏ trên thanh công cụ dọc góc trái nhé!")
        self.lbl_sub_guide4.setStyleSheet("font-size: 15px; font-weight: 700; color: #f87171; font-family: 'Segoe UI';")
        self.lbl_sub_guide4.setAlignment(Qt.AlignCenter)
        
        self.btn_next4 = QPushButton("COMPLETE_ALL_TRIAL_MISSIONS_🚀")
        self.btn_next4.setFixedWidth(350) 
        self.btn_next4.setStyleSheet(STYLE_BLUE_BUTTON)
        self.btn_next4.hide()
        self.btn_next4.clicked.connect(lambda: self.go_to_stage(5))
        
        card_layout.addWidget(self.lbl_guide4)
        card_layout.addStretch(1)
        card_layout.addWidget(self.lbl_sub_guide4)
        card_layout.addStretch(1)
        card_layout.addWidget(self.btn_next4, alignment=Qt.AlignCenter)
        
        layout.addWidget(task_card, alignment=Qt.AlignCenter)
        self.stack.addWidget(page)

    def setup_page_finish(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        
        task_card = QWidget()
        task_card.setFixedSize(840, 520) 
        task_card.setStyleSheet("QWidget { background-color: #020617; border: 2px solid #334155; border-radius: 20px; }")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(192, 132, 252, 20))
        task_card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(task_card)
        card_layout.setContentsMargins(40, 35, 40, 35)
        card_layout.setSpacing(20)
        
        lbl_congrat = QLabel("🎉 [ MISSION_SUCCESSFUL // CORE_VERIFIED ] 🎉")
        lbl_congrat.setStyleSheet("font-size: 26px; font-weight: 900; color: #2dd4bf; font-family: 'Consolas';")
        lbl_congrat.setAlignment(Qt.AlignCenter)
        
        lbl_content = QLabel(
            "Bạn đã làm chủ được tất cả các thao tác cơ bản của hệ thống EzTouch rồi đó!\n"
            "Giờ hãy tự tin trải nghiệm ứng dụng thực tế ngoài không gian số.\n"
            "Tất nhiên, sau này bạn có thể quay lại đây luyện tập bất cứ lúc nào nếu quên."
        )
        lbl_content.setStyleSheet("font-size: 15px; font-weight: 600; color: #cbd5e1; line-height: 160%; font-family: 'Segoe UI';")
        lbl_content.setAlignment(Qt.AlignCenter)
        
        btn_back_home = QPushButton("RETURN_TO_MAIN_TERMINAL")
        btn_back_home.setFixedSize(290, 56)
        btn_back_home.setStyleSheet(STYLE_ORANGE_BUTTON)
        btn_back_home.clicked.connect(self.exit_trial)
        
        card_layout.addWidget(lbl_congrat)
        card_layout.addStretch(1)
        card_layout.addWidget(lbl_content)
        card_layout.addStretch(1)
        card_layout.addWidget(btn_back_home, alignment=Qt.AlignCenter)
        
        layout.addWidget(task_card, alignment=Qt.AlignCenter)
        self.stack.addWidget(page)

    def go_to_stage(self, stage_idx):
        config.trial_task_stage = stage_idx
        self.stack.setCurrentIndex(stage_idx)
        self.overall_progress.setValue(stage_idx * 20)
        if stage_idx != 3:
            config.is_keyboard_open = False

    def handle_intro_finished(self):
        self.go_to_stage(1)

    def handle_task1_success(self):
        if config.trial_task_stage == 1:
            self.lbl_sub_guide1.setText("Hệ thống chấp thuận! Giao thức Task 01 đã được xác minh.")
            self.lbl_sub_guide1.setStyleSheet("font-size: 15px; color: #2dd4bf; font-weight: bold; font-family: 'Segoe UI';")
            self.target_btn.hide()
            self.btn_next1.show()

    def handle_chat_input_focused(self):
        if config.trial_task_stage == 3 and not self.chat_input.clicked_connect_flag:
            self.chat_input.clicked_connect_flag = True
            self.lbl_sub_guide3.setText("Tuyệt vời! Bây giờ hãy nhìn sang thanh công cụ dọc, NHẤP VÀO NÚT '⌨ ON' để mở bàn phím ảo.")
            self.lbl_sub_guide3.setStyleSheet("font-size: 14px; color: #c084fc; font-weight: bold; font-family: 'Segoe UI';")

    def monitor_user_actions(self):
        if not config.is_trial_active: 
            config.MAGNETIC_TARGETS = {} 
            return
        
        if config.trial_task_stage == 0 and hasattr(self, 'btn_start_onboarding') and self.btn_start_onboarding.isEnabled():
            g_pos = self.btn_start_onboarding.mapToGlobal(self.btn_start_onboarding.rect().center())
            config.MAGNETIC_TARGETS = {"START_ONBOARDING": (g_pos.x(), g_pos.y())}
            
        elif config.trial_task_stage == 1 and hasattr(self, 'target_btn') and self.target_btn.isVisible():
            g_pos = self.target_btn.mapToGlobal(self.target_btn.rect().center())
            config.MAGNETIC_TARGETS = {"TARGET_ORANGE": (g_pos.x(), g_pos.y())}
            
        elif config.trial_task_stage == 2 and not self.btn_next2.isVisible():
            if self.main_app.is_engine_running:
                scroll_bar = self.news_text.verticalScrollBar()
                if scroll_bar.value() >= scroll_bar.maximum() - 2:
                    self.lbl_sub_guide2.setText("Xác thực thành công! Bạn đã hoàn thành chuỗi cuộn dòng dữ liệu cuối cùng.")
                    self.lbl_sub_guide2.setStyleSheet("font-size: 15px; color: #2dd4bf; font-weight: bold; font-family: 'Segoe UI';")
                    self.btn_next2.show()
            
        elif config.trial_task_stage == 3 and hasattr(self, 'chat_input'):
            g_pos = self.chat_input.mapToGlobal(self.chat_input.rect().center())
            config.MAGNETIC_TARGETS = {"CHAT_INPUT_BOX": (g_pos.x(), g_pos.y())}
            
        elif config.trial_task_stage == 4 and hasattr(self, 'btn_next4') and self.btn_next4.isVisible():
            g_pos = self.btn_next4.mapToGlobal(self.btn_next4.rect().center())
            config.MAGNETIC_TARGETS = {"FINISH_BUTTON": (g_pos.x(), g_pos.y())}
        else:
            config.MAGNETIC_TARGETS = {}
        
        if config.trial_task_stage == 0:
            self.progress_bar.setValue(config.trial_countdown_pct)
            if config.CURRENT_MODE == "UNDECIDED":
                self.lbl_countdown.setText("⏱ dependency status: Đang chờ nhận diện cử chỉ nghiêng đầu chọn chế độ...")
            elif config.CURRENT_MODE in ["PARKINSON", "REGULAR"] and config.CALIBRATED_CENTER_X == 0.5:
                mode_name = "BẢO VỆ CHỐNG RUN" if config.CURRENT_MODE == "PARKINSON" else "LƯỚT SIÊU TỐC"
                self.lbl_calib_status.setText(f"Đã kích hoạt chế độ: {mode_name}.\nBây giờ, hãy GIỮ YÊN VỊ TRÍ NHÌN THOẢI MÁI ĐỂ THIẾT LẬP TÂM AN TOÀN.")
                self.lbl_countdown.setText("⏱️ SYNC_STREAM: Đang đồng bộ và định vị vùng an toàn...")
            else:
                self.lbl_calib_status.setText("🎉 Thiết lập không gian sinh học thành công! Hệ thống lõi đã tự cấu hình hoàn tất.")
                self.lbl_calib_status.setStyleSheet("font-size: 14px; color: #2dd4bf; font-weight: bold; line-height: 140%; border: none; font-family: 'Segoe UI';")
                self.lbl_countdown.setText("✅ ONLINE: Không gian sinh học đã sẵn sàng 100%!")
                self.btn_start_onboarding.setEnabled(True)
                self.btn_start_onboarding.setStyleSheet(STYLE_BLUE_BUTTON + "font-size: 15px; padding: 10px; border-radius: 12px;")

        elif config.trial_task_stage == 1 and self.target_btn.isVisible():
            btn_pos = self.target_btn.mapToGlobal(self.target_btn.rect().topLeft())
            import pyautogui
            mx, my = pyautogui.position()
            if (btn_pos.x() <= mx <= btn_pos.x() + self.target_btn.width() and 
                btn_pos.y() <= my <= btn_pos.y() + self.target_btn.height()):
                self.lbl_sub_guide1.setText("Mục tiêu đã khóa! Hãy HÁ MỒM (Click) để truyền tín hiệu phản xạ!")
                self.lbl_sub_guide1.setStyleSheet("font-size: 15px; color: #2dd4bf; font-weight: bold; font-family: 'Segoe UI';")
            else:
                if mx > config.SCREEN_WIDTH // 3 or my > config.SCREEN_HEIGHT // 3:
                    self.lbl_sub_guide1.setText("Con trỏ sắp tiếp cận vùng an toàn! Hãy hướng về khối hộp cơ khí.")
                    self.lbl_sub_guide1.setStyleSheet("font-size: 15px; color: #c084fc; font-weight: bold; font-family: 'Segoe UI';")
                else:
                    self.lbl_sub_guide1.setText("Bạn hãy di chuyển mũi sao cho con trỏ chuột di chuyển đến cái nút ma trận cơ khí ở góc khung.")
                    self.lbl_sub_guide1.setStyleSheet("font-size: 15px; color: #94a3b8; font-family: 'Segoe UI';")
                
        elif config.trial_task_stage == 2 and not self.btn_next2.isVisible():
            if self.main_app.is_engine_running:
                if config.system_state == "RUNNING":
                    self.lbl_sub_guide2.setText("Há mồm trong 1.5 giây để bật tính năng cuộn chuột, sau đó hãy cúi đầu xuống để cuộn xuống và ngửa lên để cuộn lên.")
                    self.lbl_sub_guide2.setStyleSheet("font-size: 15px; color: #38bdf8; font-weight: bold; font-family: 'Segoe UI';")
                
        elif config.trial_task_stage == 3:
            is_focused = self.chat_input.hasFocus()
            config.is_chat_input_focused = is_focused 
            
            if config.is_keyboard_open:
                for widget in QApplication.topLevelWidgets():
                    if "Keyboard" in widget.windowTitle():
                        screen_geo = QApplication.primaryScreen().geometry()
                        kw = widget.width() if widget.width() > 100 else 760 
                        kh = widget.height() if widget.height() > 100 else 320
                        target_x = (screen_geo.width() - kw) // 2
                        target_y = screen_geo.height() - kh - 50
                        if widget.geometry().y() < target_y - 20 or widget.geometry().y() > target_y + 20:
                            widget.move(target_x, target_y)
            
            if not is_focused:
                self.lbl_sub_guide3.setText("HÃY NHẤP VÀO Ô CHAT ĐỂ ĐỒNG BỘ DỮ LIỆU ĐẦU VÀO!")
                self.lbl_sub_guide3.setStyleSheet("font-size: 15px; color: #f87171; font-weight: bold; font-family: 'Segoe UI';")
                config.trial_keyboard_warning_text = "CHUA NHAP VAO O CHAT! HAY NHAP VAO ROI MOI GO CHU NHE!"
            else:
                config.trial_keyboard_warning_text = "" 
                if not config.is_keyboard_open:
                    self.lbl_sub_guide3.setText("Kết nối ô chat ổn định! Bây giờ hãy nhìn sang thanh công cụ dọc, NHẤP NÚT '⌨ ON'.")
                    self.lbl_sub_guide3.setStyleSheet("font-size: 15px; color: #c084fc; font-weight: bold; font-family: 'Segoe UI';")
                elif config.is_keyboard_open and len(self.chat_input.text()) < 3:
                    self.lbl_sub_guide3.setText("Bàn phím đã neo đáy an toàn! Hãy giữ mũi vào ô chữ bất kỳ trong 2 giây hoặc há mồm để gõ.")
                    self.lbl_sub_guide3.setStyleSheet("font-size: 14px; color: #38bdf8; font-weight: bold; font-family: 'Segoe UI';")
                elif len(self.chat_input.text()) >= 3 and config.is_keyboard_open:
                    self.lbl_sub_guide3.setText("Dữ liệu chuỗi ký tự đã đồng bộ đủ! Hãy ấn nút '⌨ OFF' trên thanh dọc để đóng ma trận phím.")
                    self.lbl_sub_guide3.setStyleSheet("font-size: 15px; color: #f87171; font-weight: bold; font-family: 'Segoe UI';")
                elif len(self.chat_input.text()) >= 3 and not config.is_keyboard_open:
                    self.lbl_sub_guide3.setText("Giao thức Task 03 hoàn tất hoàn hảo!")
                    self.lbl_sub_guide3.setStyleSheet("font-size: 15px; color: #2dd4bf; font-weight: bold; font-family: 'Segoe UI';")
                    self.btn_next3.show()

        elif config.trial_task_stage == 4 and not self.btn_next4.isVisible():
            if config.system_state == "PAUSED":
                self.has_triggered_pause = True  
                self.lbl_sub_guide4.setText("Trạng thái đóng ngắt tạm thời kích hoạt! Nhấn nút 'RESUME' màu xanh trên thanh dọc để tái đồng bộ.")
                self.lbl_sub_guide4.setStyleSheet("font-size: 15px; color: #38bdf8; font-weight: bold; font-family: 'Segoe UI';")
            
            elif config.system_state == "RUNNING" and self.has_triggered_pause:
                self.lbl_sub_guide4.setText("Hệ thống vận hành trở lại ổn định! Chuỗi trải nghiệm sinh học kết thúc mỹ mãn.")
                self.lbl_sub_guide4.setStyleSheet("font-size: 16px; color: #2dd4bf; font-weight: bold; font-family: 'Segoe UI';")
                self.btn_next4.show()

    def exit_trial(self):
        self.trial_timer.stop()
        config.is_trial_active = False
        config.trial_task_stage = 0
        config.is_keyboard_open = False
        self.has_triggered_pause = False
        config.CURRENT_MODE = "UNDECIDED" 
        config.CALIBRATED_CENTER_X = 0.5
        config.CALIBRATED_CENTER_Y = 0.5
        config.trial_countdown_pct = 0
        if self.main_app.is_engine_running:
            self.main_app.handle_engine_toggle()
        self.close()

    def closeEvent(self, event):
        config.is_trial_active = False
        event.accept()


class EzTouchSideToolbar(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.is_expanded = True  
        self.init_ui()
        self.update_position()

    def init_ui(self):
        self.outer_layout = QHBoxLayout()
        self.outer_layout.setContentsMargins(0, 0, 0, 0)
        self.outer_layout.setSpacing(0)
        
        self.toolbar_body = QWidget()
        self.toolbar_body.setFixedWidth(124) 
        self.toolbar_body.setStyleSheet(
            "QWidget { background-color: #0b0f19; border: 3px solid #38bdf8; border-top-right-radius: 20px; border-bottom-right-radius: 20px; }"
        )
        
        body_layout = QVBoxLayout(self.toolbar_body)
        body_layout.setContentsMargins(6, 20, 6, 20)
        body_layout.setSpacing(15)
        
        self.btn_toggle_pause = QPushButton()
        self.btn_toggle_pause.setFixedSize(110, 110) 
        self.btn_toggle_pause.setCursor(Qt.PointingHandCursor)
        self.btn_toggle_pause.clicked.connect(self.handle_pause_click)
        
        self.btn_toggle_keyboard = QPushButton()
        self.btn_toggle_keyboard.setFixedSize(110, 110) 
        self.btn_toggle_keyboard.setCursor(Qt.PointingHandCursor)
        self.btn_toggle_keyboard.clicked.connect(self.handle_keyboard_click)
        
        body_layout.addWidget(self.btn_toggle_pause)
        body_layout.addWidget(self.btn_toggle_keyboard)
        
        self.btn_slide_handle = QPushButton("◀")
        self.btn_slide_handle.setFixedSize(22, 100)
        self.btn_slide_handle.setCursor(Qt.PointingHandCursor)
        self.btn_slide_handle.setStyleSheet(
            "QPushButton { background-color: #38bdf8; color: #0b0f19; border: none; border-top-right-radius: 10px; border-bottom-right-radius: 10px; font-weight: bold; font-size: 12px; }"
            "QPushButton:hover { background-color: #ffffff; }"
        )
        self.btn_slide_handle.clicked.connect(self.toggle_collapse)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(2, 2)
        shadow.setColor(QColor(56, 189, 248, 50))
        self.setGraphicsEffect(shadow)
        
        self.outer_layout.addWidget(self.toolbar_body)
        self.outer_layout.addWidget(self.btn_slide_handle)
        self.setLayout(self.outer_layout)
        self.update_button_styles()

    def update_position(self):
        total_w = 146 if self.is_expanded else 22
        total_h = 280
        pos_x = 0
        pos_y = (config.SCREEN_HEIGHT - total_h) // 2
        self.setGeometry(pos_x, pos_y, total_w, total_h)

    def update_button_styles(self):
        if config.system_state == "PAUSED":
            self.btn_toggle_pause.setText("RESUME_")
            self.btn_toggle_pause.setStyleSheet(STYLE_TOOLBAR_RESUME)
        else:
            self.btn_toggle_pause.setText("PAUSE_")
            self.btn_toggle_pause.setStyleSheet(STYLE_TOOLBAR_PAUSE)
            
        if not config.is_keyboard_open:
            self.btn_toggle_keyboard.setText("KEY_ON_")
            self.btn_toggle_keyboard.setStyleSheet(
                "QPushButton { background-color: #0f172a; color: #94a3b8; font-size: 15px; font-weight: bold; border-radius: 16px; border: 3px solid #475569; }"
                "QPushButton:hover { background-color: #475569; color: #ffffff; }"
                "QPushButton:pressed { background-color: #ffffff; color: #0f172a; }"
            )
        else:
            self.btn_toggle_keyboard.setText("KEY_OFF_")
            self.btn_toggle_keyboard.setStyleSheet(
                "QPushButton { background-color: #0f172a; color: #c084fc; font-size: 15px; font-weight: bold; border-radius: 16px; border: 3px solid #c084fc; }"
                "QPushButton:hover { background-color: #c084fc; color: #0f172a; }"
                "QPushButton:pressed { background-color: #ffffff; color: #0f172a; }"
            )

    def handle_pause_click(self):
        if self.main_app.is_engine_running:
            if config.system_state == "RUNNING":
                config.system_state = "PAUSED"
            elif config.system_state == "PAUSED":
                config.system_state = "RUNNING"
            self.update_button_styles()

    def handle_keyboard_click(self):
        if self.main_app.is_engine_running:
            if config.is_trial_active and config.trial_task_stage != 3:
                return 
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


class EzTouchApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EzTouch // Urban Neural Interface")
        
        self.setMinimumSize(560, 460) 
        self.resize(600, 500)
        self.setStyleSheet("""
            QWidget { 
                background-color: #0b0f19; 
                color: #f1f5f9; 
                font-family: 'Consolas', 'Segoe UI Monospace', 'Courier New', monospace; 
            }
        """)

        self.face_thread = None
        self.is_engine_running = False
        self.init_ui()
        
        self.side_toolbar = EzTouchSideToolbar(self)
        self.side_toolbar.show()
        
        self.sync_timer = QTimer(self)
        self.sync_timer.setInterval(200)
        self.sync_timer.timeout.connect(self.sync_ui_states)
        self.sync_timer.start()

    def init_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(40, 35, 40, 35) 
        self.main_layout.setSpacing(0) 

        # =========================================================================
        # PART I: KHUNG THỂ THƯƠNG HIỆU MATRIX (CYBER GLOW CONTAINER)
        # =========================================================================
        self.brand_card = QWidget()
        self.brand_card.setStyleSheet("""
            QWidget { 
                background-color: #0f172a; 
                border: 2px solid #1e293b; 
                border-radius: 24px; 
            }
        """)
        
        card_shadow = QGraphicsDropShadowEffect()
        card_shadow.setBlurRadius(40)
        card_shadow.setOffset(0, 0)
        card_shadow.setColor(QColor(56, 189, 248, 25)) 
        self.brand_card.setGraphicsEffect(card_shadow)

        self.brand_layout = QVBoxLayout(self.brand_card)
        self.brand_layout.setContentsMargins(35, 30, 35, 30)
        self.brand_layout.setSpacing(12) 

        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setStyleSheet("QLabel { background: transparent; border: none; }")
        
        self.team_label = QLabel("> SYSTEM_AUTHOR: EZ_TEAM_")
        self.team_label.setAlignment(Qt.AlignCenter)
        
        self.subtitle_label = QLabel("HỆ THỐNG ĐIỀU KHIỂN CHUỘT BẰNG KHUÔN MẶT // V.1.0")
        self.subtitle_label.setAlignment(Qt.AlignCenter)

        self.brand_layout.addWidget(self.logo_label, alignment=Qt.AlignCenter)
        self.brand_layout.addWidget(self.team_label)
        self.brand_layout.addWidget(self.subtitle_label)

        self.brand_card.setMaximumWidth(900)

        # =========================================================================
        # PART II: KHỐI CONTAINER NÚT ẤM GAME ARCADE 3D VẬT LÝ
        # =========================================================================
        self.action_button = QPushButton("STANDARD_MODE_")
        self.action_button.setCursor(Qt.PointingHandCursor)
        self.action_button.clicked.connect(self.handle_engine_toggle)
        
        self.trial_button = QPushButton("TRIAL_RUN_")
        self.trial_button.setCursor(Qt.PointingHandCursor)
        self.trial_button.clicked.connect(self.start_trial_mode)

        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(24) 
        self.button_layout.addWidget(self.action_button, 6)
        self.button_layout.addWidget(self.trial_button, 4)

        self.btn_container = QWidget()
        self.btn_container.setLayout(self.button_layout)
        self.btn_container.setStyleSheet("QWidget { background: transparent; border: none; }") 
        self.btn_container.setFixedWidth(480) 

        # =========================================================================
        # PART III: SLOGAN PHỤ HỆ THỐNG (FOOTER STATEMENT)
        # =========================================================================
        self.status_footer = QLabel('"// từ những vệt sáng cuối trời, thắp sáng những thế giới riêng "')
        self.status_footer.setAlignment(Qt.AlignCenter)

        self.main_layout.addWidget(self.brand_card, alignment=Qt.AlignCenter)
        self.main_layout.addStretch(4) 
        self.main_layout.addWidget(self.btn_container, alignment=Qt.AlignCenter)
        self.main_layout.addStretch(2) 
        self.main_layout.addWidget(self.status_footer)
        
        self.setLayout(self.main_layout)
        
        self.execute_responsive_ui_scaling(self.width(), self.height())

    def resizeEvent(self, event):
        w = event.size().width()
        h = event.size().height()
        self.execute_responsive_ui_scaling(w, h)
        super().resizeEvent(event)

    def execute_responsive_ui_scaling(self, w, h):
        ideal_logo_h = int(h * 0.15)
        logo_h = np.clip(ideal_logo_h, 60, 125)
        
        logo_pixmap = get_transparent_logo_pixmap("picture/workmark.png", logo_h)
        if not logo_pixmap.isNull():
            self.logo_label.setPixmap(logo_pixmap)
        
        ideal_container_w = int(w * 0.75)
        container_w = np.clip(ideal_container_w, 460, 680)
        self.btn_container.setFixedWidth(container_w)
        
        ideal_btn_h = int(h * 0.15)
        btn_h = np.clip(ideal_btn_h, 85, 125)
        self.action_button.setFixedHeight(btn_h)
        self.trial_button.setFixedHeight(btn_h)
        
        base_scale = (w * h) / 270000.0
        
        font_size_btn = int(np.clip(15 + base_scale * 1.5, 15, 23))
        font_size_team = int(np.clip(13 + base_scale * 0.6, 13, 17))
        font_size_sub = int(np.clip(10 + base_scale * 0.4, 10, 12))
        font_size_foot = int(np.clip(12 + base_scale * 0.6, 12, 16))
        
        self.action_button.setStyleSheet(STYLE_BLUE_BUTTON + f"font-size: {font_size_btn}px;")
        self.trial_button.setStyleSheet(STYLE_ORANGE_BUTTON + f"font-size: {font_size_btn}px;")
        
        self.team_label.setStyleSheet(f"QLabel {{ font-size: {font_size_team}px; font-weight: bold; color: #38bdf8; letter-spacing: 2px; border: none; }}")
        self.subtitle_label.setStyleSheet(f"QLabel {{ font-size: {font_size_sub}px; font-weight: bold; color: #64748b; letter-spacing: 1.5px; border: none; }}")
        self.status_footer.setStyleSheet(f"QLabel {{ font-size: {font_size_foot}px; font-weight: bold; color: #475569; font-style: italic; }}")

    def update_button_style(self):
        if not self.is_engine_running:
            self.action_button.setText("STANDARD_MODE_")
            self.trial_button.setEnabled(True)
        else:
            self.action_button.setText("TERMINATE_CORE_")
            self.trial_button.setEnabled(False)

    def sync_ui_states(self):
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
                config.system_state = "RUNNING"
                self.update_button_style()

    def start_trial_mode(self):
        if not self.is_engine_running:
            config.is_trial_active = True
            config.trial_countdown_pct = 0
            self.handle_engine_toggle()
            self.trial_space = EzTouchTrialSpace(self)
            self.trial_space.show()

    def closeEvent(self, event):
        if hasattr(self, 'side_toolbar'):
            self.side_toolbar.close()
        if hasattr(self, 'trial_space'):
            self.trial_space.close()
        if self.face_thread and self.face_thread.isRunning():
            main.stop_system()
            self.face_thread.wait()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EzTouchApp()
    window.show()
    sys.exit(app.exec())