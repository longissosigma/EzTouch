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

# 🎨 BẢNG MÀU DẢI GRADIENT ĐỒNG BỘ 100% VỚI WORKMARK (XANH NEON HI-TECH & TÍM VIOLET)
STYLE_BLUE_BUTTON = """
    QPushButton {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #3F5EFB, stop:1 #5C7CFA);
        color: white; font-weight: 700;
        border: none; border-radius: 20px; padding: 16px;
    }
    QPushButton:hover { 
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #5C7CFA, stop:1 #708FFA);
        margin-top: -2px; margin-bottom: 2px;
    }
    QPushButton:pressed { 
        background-color: #314CC7; margin-top: 2px; margin-bottom: -2px;
    }
    QPushButton:disabled {
        background-color: #CBD5E1; color: #94A3B8;
    }
"""

STYLE_ORANGE_BUTTON = """
    QPushButton {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #651FFF, stop:1 #7C4DFF);
        color: white; font-weight: 700;
        border: none; border-radius: 20px; padding: 16px;
    }
    QPushButton:hover { 
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #7C4DFF, stop:1 #9E7CFF);
        margin-top: -2px; margin-bottom: 2px;
    }
    QPushButton:pressed { 
        background-color: #5314D1; margin-top: 2px; margin-bottom: -2px;
    }
"""

STYLE_TOOLBAR_PAUSE = """
    QPushButton {
        background-color: #E53E3E; color: white; font-size: 16px; font-weight: bold; border-radius: 20px; border: none;
    }
    QPushButton:hover { background-color: #C53030; margin-top: -2px; margin-bottom: 2px; }
    QPushButton:pressed { background-color: #9B1C1C; margin-top: 2px; margin-bottom: -2px; }
"""

STYLE_TOOLBAR_RESUME = """
    QPushButton {
        background-color: #3F5EFB; color: white; font-size: 16px; font-weight: bold; border-radius: 20px; border: none;
    }
    QPushButton:hover { background-color: #5C7CFA; margin-top: -2px; margin-bottom: 2px; }
    QPushButton:pressed { background-color: #314CC7; margin-top: 2px; margin-bottom: -2px; }
"""

def get_transparent_logo_pixmap(image_path, target_height):
    """
    🔮 ĐỘNG CƠ ĐỒ HỌA CAO CẤP: DYNAMIC AUTOCROP & CONTIGUOUS BUFFER FIX
    Tự động quét ma trận Alpha, cắt tỉa 100% vùng viền rỗng thừa của tệp thiết kế,
    đồng thời ép cấu trúc mảng ô nhớ liên tục để tránh lỗi BufferError trên hệ thống Qt.
    """
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
        self.setWindowTitle("EzTouch - Không Gian Trải Nghiệm Thử Nghiệm")
        self.setWindowFlags(Qt.Window) 
        self.showMaximized() 
        
        self.setStyleSheet("""
            QWidget {
                background-color: #F8FAFC; color: #1E293B;
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
        self.layout.setContentsMargins(60, 40, 60, 40)
        self.layout.setSpacing(20)
        
        # 🎨 TIÊU ĐỀ KHÔNG GIAN TRẢI NGHIỆM ĐÃ THAY BẰNG CHỮ THEO YÊU CẦU (MÀU XANH WORKMARK CHUẨN)
        self.header_title_label = QLabel("Chào mừng đến với cơ chế trải nghiệm của EzTouch ;)")
        self.header_title_label.setAlignment(Qt.AlignCenter)
        self.header_title_label.setStyleSheet("""
            QLabel {
                font-size: 26px; 
                font-weight: 800; 
                color: #3F5EFB; 
                letter-spacing: 0.5px;
                padding: 10px 0px;
            }
        """)
        self.layout.addWidget(self.header_title_label)

        # 🌟 THANH TIẾN TRÌNH ĐỒNG BỘ ĐỘC QUYỀN
        self.overall_progress = QProgressBar()
        self.overall_progress.setRange(0, 100)
        self.overall_progress.setValue(0)
        self.overall_progress.setFixedHeight(16)
        self.overall_progress.setStyleSheet("""
            QProgressBar { 
                background-color: #E2E8F0; 
                border-radius: 8px; 
                text-align: center; 
                font-size: 11px;
                font-weight: bold; 
                color: #1E293B; 
            }
            QProgressBar::chunk { 
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3F5EFB, stop:1 #651FFF); 
                border-radius: 8px; 
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
        
        self.btn_exit_trial = QPushButton("Thoát Thử Nghiệm (Quit Trial)")
        self.btn_exit_trial.setFixedWidth(220)
        self.btn_exit_trial.setStyleSheet(STYLE_BLUE_BUTTON.replace("padding: 16px;", "padding: 10px; font-size: 14px; border-radius: 12px;"))
        self.btn_exit_trial.clicked.connect(self.exit_trial)
        self.layout.addWidget(self.btn_exit_trial, alignment=Qt.AlignRight)

    def setup_page_intro(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        
        intro_card = QWidget()
        intro_card.setFixedWidth(820)
        intro_card.setStyleSheet("QWidget { background-color: #FFFFFF; border-radius: 24px; }")
        
        card_shadow = QGraphicsDropShadowEffect()
        card_shadow.setBlurRadius(40)
        card_shadow.setOffset(0, 10)
        card_shadow.setColor(QColor(63, 94, 251, 20))
        intro_card.setGraphicsEffect(card_shadow)
        
        card_layout = QVBoxLayout(intro_card)
        card_layout.setContentsMargins(50, 40, 50, 40)
        card_layout.setSpacing(15)

        self.welcome_logo_label = QLabel()
        self.welcome_logo_label.setAlignment(Qt.AlignCenter)
        logo_pixmap = get_transparent_logo_pixmap("picture/workmark.png", 90)
        if not logo_pixmap.isNull():
            self.welcome_logo_label.setPixmap(logo_pixmap)
        
        lbl_author = QLabel("by the SigmaCode")
        lbl_author.setAlignment(Qt.AlignCenter)
        lbl_author.setStyleSheet("font-size: 15px; font-weight: 700; font-style: italic; color: #64748B; letter-spacing: 2px;")
        
        lbl_mission = QLabel(
            "SỨ MỆNH DỰ ÁN:\n"
            "EzTouch ra đời nhằm mục đích xóa bỏ rào cản số, mang không gian công nghệ\n"
            "đến gần hơn với trẻ em khuyết tật vận động chi trên và người cao tuổi mắc chứng bệnh run vô thức.\n"
            "Chúng tôi tin rằng từ những vệt sáng cuối trời, mọi thế giới riêng đều xứng đáng được thắp sáng."
        )
        lbl_mission.setStyleSheet("font-size: 15px; line-height: 160%; color: #475569; font-weight: 500; text-align: center;")
        lbl_mission.setAlignment(Qt.AlignCenter)

        self.calibration_panel = QWidget()
        self.calibration_panel.setStyleSheet("QWidget { background-color: #F8FAFC; border-radius: 16px; border: 1px solid #E2E8F0; }")
        
        panel_layout = QVBoxLayout(self.calibration_panel)
        panel_layout.setContentsMargins(30, 25, 30, 25)
        panel_layout.setSpacing(15)
        
        self.lbl_calib_title = QLabel("🔮 THIẾT LẬP KHÔNG GIAN SINH HỌC CÁ NHÂN")
        self.lbl_calib_title.setStyleSheet("font-size: 17px; font-weight: 800; color: #3F5EFB; border: none;")
        self.lbl_calib_title.setAlignment(Qt.AlignCenter)
        
        self.lbl_calib_status = QLabel("👉 Vui lòng nghiêng nhẹ đầu sang TRÁI để chọn chế độ bảo vệ chống run,\nhoặc nghiêng đầu sang PHẢI để chọn chế độ lướt siêu tốc.")
        self.lbl_calib_status.setStyleSheet("font-size: 14px; color: #475569; font-weight: 600; line-height: 150%; border: none;")
        self.lbl_calib_status.setAlignment(Qt.AlignCenter)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(10)
        self.progress_bar.setStyleSheet("""
            QProgressBar { background-color: #E2E8F0; border-radius: 5px; border: none; }
            QProgressBar::chunk { 
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3F5EFB, stop:1 #651FFF); 
                border-radius: 5px; 
            }
        """)
        
        self.lbl_countdown = QLabel("⏱️ Đang đồng bộ tín hiệu mốc khuôn mặt thông minh...")
        self.lbl_countdown.setStyleSheet("font-size: 14px; font-weight: 700; color: #3F5EFB; border: none;")
        self.lbl_countdown.setAlignment(Qt.AlignCenter)
        
        panel_layout.addWidget(self.lbl_calib_title)
        panel_layout.addWidget(self.lbl_calib_status)
        panel_layout.addWidget(self.progress_bar)
        panel_layout.addWidget(self.lbl_countdown)
        
        self.btn_start_onboarding = QPushButton("BẮT ĐẦU TRẢI NGHIỆM BAN ĐẦU ▶")
        self.btn_start_onboarding.setFixedSize(360, 54)
        self.btn_start_onboarding.setEnabled(False) 
        self.btn_start_onboarding.setStyleSheet("background-color: #CBD5E1; color: #94A3B8; font-size: 16px; font-weight: bold; border-radius: 16px; border: none;")
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
        task_card.setFixedSize(820, 500)
        task_card.setStyleSheet("QWidget { background-color: #FFFFFF; border-radius: 24px; }")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 15))
        task_card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(task_card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        
        self.lbl_guide1 = QLabel("Task 1: DI CHUYỂN CHUỘT & CLICK SINH HỌC CHỦ ĐỘNG")
        self.lbl_guide1.setStyleSheet("font-size: 20px; font-weight: 700; color: #3F5EFB;")
        self.lbl_guide1.setAlignment(Qt.AlignCenter)
        
        self.lbl_sub_guide1 = QLabel("Bạn hãy di chuyển mũi sao cho con trỏ chuột di chuyển đến cái nút to màu tím ở góc khung.")
        self.lbl_sub_guide1.setStyleSheet("font-size: 15px; color: #475569; margin-bottom: 20px;")
        self.lbl_sub_guide1.setAlignment(Qt.AlignCenter)
        
        self.click_area = QWidget()
        area_layout = QHBoxLayout(self.click_area)
        
        self.target_btn = QPushButton("BẤM VÀO TỚ\n(HÁ MỒM)")
        self.target_btn.setFixedSize(180, 100)
        self.target_btn.setStyleSheet(STYLE_ORANGE_BUTTON + "font-size: 16px;")
        self.target_btn.clicked.connect(self.handle_task1_success)
        area_layout.addWidget(self.target_btn, alignment=Qt.AlignRight | Qt.AlignBottom)
        
        self.btn_next1 = QPushButton("TIẾP THEO SANG TASK 2 ▶")
        self.btn_next1.setFixedWidth(280)
        self.btn_next1.setStyleSheet(STYLE_BLUE_BUTTON + "font-size: 16px;")
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
        task_card.setFixedSize(820, 520)
        task_card.setStyleSheet("QWidget { background-color: #FFFFFF; border-radius: 24px; }")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 15))
        task_card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(task_card)
        card_layout.setContentsMargins(40, 35, 40, 35)
        
        self.lbl_guide2 = QLabel("Task 2: TÍNH NĂNG CUỘN TRANG (SCROLL MODE)")
        self.lbl_guide2.setStyleSheet("font-size: 20px; font-weight: 700; color: #3F5EFB;")
        self.lbl_guide2.setAlignment(Qt.AlignCenter)
        
        self.lbl_sub_guide2 = QLabel("Tiếp theo bạn hãy há mồm và giữ im đó trong vòng 1.3 giây.")
        self.lbl_sub_guide2.setStyleSheet("font-size: 15px; color: #DC2626; font-weight: bold; margin-bottom: 15px;")
        self.lbl_sub_guide2.setAlignment(Qt.AlignCenter)
        
        self.news_text = QTextEdit()
        self.news_text.setReadOnly(True)
        self.news_text.setFont(QFont("Segoe UI", 11))
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
                background-color: #F8FAFC; 
                border: 1px solid #E2E8F0; 
                border-radius: 14px; 
                padding: 15px; 
                color: #334155;
            }
        """)
        
        self.btn_next2 = QPushButton("TIẾP THEO SANG TASK 3 ▶")
        self.btn_next2.setFixedWidth(280)
        self.btn_next2.setStyleSheet(STYLE_BLUE_BUTTON + "font-size: 16px;")
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
        task_card.setFixedSize(820, 400)
        task_card.setStyleSheet("QWidget { background-color: #FFFFFF; border-radius: 24px; }")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 15))
        task_card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(task_card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        
        self.lbl_guide3 = QLabel("Task 3: LÀM QUEN BÀN PHÍM ẢO MA TRẬN ĐỘC LẬP")
        self.lbl_guide3.setStyleSheet("font-size: 20px; font-weight: 700; color: #3F5EFB;")
        self.lbl_guide3.setAlignment(Qt.AlignCenter)
        
        self.lbl_sub_guide3 = QLabel("Hãy nhấp (há mồm nhanh) vào ô nhắn tin Messenger giả lập bên dưới.")
        self.lbl_sub_guide3.setStyleSheet("font-size: 15px; color: #475568; margin-bottom: 20px;")
        self.lbl_sub_guide3.setAlignment(Qt.AlignCenter)
        
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Nhấp vào đây để soạn tin nhắn chat...")
        self.chat_input.setMinimumHeight(56)
        self.chat_input.setFont(QFont("Segoe UI", 13))
        self.chat_input.setStyleSheet("""
            QLineEdit { 
                background-color: #F8FAFC; 
                border: 2px solid #E2E8F0; 
                border-radius: 14px; 
                padding-left: 15px;
                color: #1E293B;
            }
            QLineEdit:focus {
                border-color: #3F5EFB;
                background-color: #FFFFFF;
            }
        """)
        self.chat_input.clicked_connect_flag = False
        self.chat_input.cursorPositionChanged.connect(self.handle_chat_input_focused)
        
        self.btn_next3 = QPushButton("TIẾP THEO SANG TASK 4 ▶")
        self.btn_next3.setFixedWidth(280)
        self.btn_next3.setStyleSheet(STYLE_BLUE_BUTTON + "font-size: 16px;")
        self.btn_next3.hide()
        self.btn_next3.clicked.connect(lambda: self.go_to_stage(4))
        
        card_layout.addWidget(self.lbl_guide3)
        card_layout.addWidget(self.lbl_sub_guide3)
        card_layout.addWidget(self.chat_input)
        card_layout.addStretch()
        card_layout.addWidget(self.btn_next3, alignment=Qt.AlignCenter)
        
        layout.addWidget(task_card, alignment=Qt.AlignCenter)
        self.stack.addWidget(page)

    def setup_page_task4(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        
        task_card = QWidget()
        task_card.setFixedSize(820, 380)
        task_card.setStyleSheet("QWidget { background-color: #FFFFFF; border-radius: 24px; }")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 15))
        task_card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(task_card)
        card_layout.setContentsMargins(40, 50, 40, 50)
        
        self.lbl_guide4 = QLabel("Task 4: CƠ CHẾ NGHỈ NGƠI TẠM DỪNG (PAUSE/RESUME)")
        self.lbl_guide4.setStyleSheet("font-size: 20px; font-weight: 700; color: #3F5EFB; letter-spacing: 0.5px;")
        
        self.lbl_sub_guide4 = QLabel("Khi bạn muốn nghỉ ngơi hãy ấn vào nút 'PAUSE' màu đỏ trên thanh công cụ dọc góc trái nhé!")
        self.lbl_sub_guide4.setStyleSheet("font-size: 16px; color: #DC2626; font-weight: bold; margin: 30px;")
        self.lbl_sub_guide4.setAlignment(Qt.AlignCenter)
        
        self.btn_next4 = QPushButton("HOÀN THÀNH HÀNH TRÌNH ▶")
        self.btn_next4.setFixedWidth(320) 
        self.btn_next4.setStyleSheet(STYLE_BLUE_BUTTON + "font-size: 16px;")
        self.btn_next4.hide()
        self.btn_next4.clicked.connect(lambda: self.go_to_stage(5))
        
        card_layout.addWidget(self.lbl_guide4)
        card_layout.addWidget(self.lbl_sub_guide4)
        card_layout.addWidget(self.btn_next4, alignment=Qt.AlignCenter)
        
        layout.addWidget(task_card, alignment=Qt.AlignCenter)
        self.stack.addWidget(page)

    def setup_page_finish(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        
        task_card = QWidget()
        task_card.setFixedSize(820, 380)
        task_card.setStyleSheet("QWidget { background-color: #FFFFFF; border-radius: 24px; }")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(63, 94, 251, 20))
        task_card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(task_card)
        card_layout.setContentsMargins(40, 50, 40, 50)
        card_layout.setSpacing(20)
        
        lbl_congrat = QLabel("🎉 XUẤT SẮC HOÀN THÀNH TRIAL! 🎉")
        lbl_congrat.setStyleSheet("font-size: 32px; font-weight: 900; color: #3F5EFB;")
        lbl_congrat.setAlignment(Qt.AlignCenter)
        
        lbl_content = QLabel(
            "Bạn đã làm chủ được tất cả các thao tác cơ bản của hệ thống EzTouch rồi đó!\n"
            "Giờ hãy tự tin trải nghiệm ứng dụng thực tế ngoài không gian số.\n"
            "Tất nhiên, sau này bạn có thể quay lại đây luyện tập bất cứ lúc nào nếu quên."
        )
        lbl_content.setStyleSheet("font-size: 15px; font-weight: 600; color: #475569; line-height: 160%; text-align: center;")
        lbl_content.setAlignment(Qt.AlignCenter)
        
        btn_back_home = QPushButton("QUAY LẠI TRANG CHỦ")
        btn_back_home.setFixedSize(280, 54)
        btn_back_home.setStyleSheet(STYLE_ORANGE_BUTTON + "font-size: 16px;")
        btn_back_home.clicked.connect(self.exit_trial)
        
        card_layout.addWidget(lbl_congrat)
        card_layout.addWidget(lbl_content)
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
            self.lbl_sub_guide1.setText("Bạn làm tốt lắm ý, chuẩn bị sẵn sàng cho tính năng mới nào!")
            self.lbl_sub_guide1.setStyleSheet("font-size: 16px; color: #3F5EFB; font-weight: bold;")
            self.target_btn.hide()
            self.btn_next1.show()

    def handle_chat_input_focused(self):
        if config.trial_task_stage == 3 and not self.chat_input.clicked_connect_flag:
            self.chat_input.clicked_connect_flag = True
            self.lbl_sub_guide3.setText("Tuyệt vời! Bây giờ hãy nhìn sang thanh công cụ dọc, NHẤP VÀO NÚT '⌨ ON' để mở bàn phím ảo.")
            self.lbl_sub_guide3.setStyleSheet("font-size: 15px; color: #651FFF; font-weight: bold;")

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
            
        elif config.trial_task_stage == 2 and hasattr(self, 'btn_next2') and self.btn_next2.isVisible():
            g_pos = self.btn_next2.mapToGlobal(self.btn_next2.rect().center())
            config.MAGNETIC_TARGETS = {"NEXT_TASK_3": (g_pos.x(), g_pos.y())}
            
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
                self.lbl_countdown.setText("⏱️ Đang chờ nhận diện cử chỉ nghiêng đầu chọn chế độ...")
            elif config.CURRENT_MODE in ["PARKINSON", "REGULAR"] and config.CALIBRATED_CENTER_X == 0.5:
                mode_name = "BẢO VỆ CHỐNG RUN" if config.CURRENT_MODE == "PARKINSON" else "LƯỚT SIÊU TỐC"
                self.lbl_calib_status.setText(f"Đã kích hoạt chế độ: {mode_name}.\nBây giờ, hãy GIỮ YÊN VỊ TRÍ NHÌN THOẢI MÁI ĐỂ THIẾT LẬP TÂM AN TOÀN.")
                self.lbl_countdown.setText("⏱️ Đang đồng bộ và định vị vùng an toàn...")
            else:
                self.lbl_calib_status.setText("🎉 Thiết lập không gian sinh học thành công! Giao diện đã tự điều chỉnh hoàn tất.")
                self.lbl_calib_status.setStyleSheet("font-size: 14px; color: #3F5EFB; font-weight: bold; line-height: 140%; border: none;")
                self.lbl_countdown.setText("✅ Không gian sinh học đã sẵn sàng 100%!")
                self.btn_start_onboarding.setEnabled(True)
                self.btn_start_onboarding.setStyleSheet(STYLE_BLUE_BUTTON + "font-size: 15px; padding: 10px; border-radius: 12px;")

        elif config.trial_task_stage == 1 and self.target_btn.isVisible():
            btn_pos = self.target_btn.mapToGlobal(self.target_btn.rect().topLeft())
            import pyautogui
            mx, my = pyautogui.position()
            if (btn_pos.x() <= mx <= btn_pos.x() + self.target_btn.width() and 
                btn_pos.y() <= my <= btn_pos.y() + self.target_btn.height()):
                self.lbl_sub_guide1.setText("Bạn đã chạm mục tiêu! Hãy HÁ MỒM (Click) để kích hoạt hoàn thành!")
                self.lbl_sub_guide1.setStyleSheet("font-size: 15px; color: #3F5EFB; font-weight: bold;")
            else:
                if mx > config.SCREEN_WIDTH // 3 or my > config.SCREEN_HEIGHT // 3:
                    self.lbl_sub_guide1.setText("Cố lên nào, sắp được rồi! Hãy di chuyển con trỏ vào ô màu vàng nhé.")
                    self.lbl_sub_guide1.setStyleSheet("font-size: 15px; color: #651FFF; font-weight: bold;")
                else:
                    self.lbl_sub_guide1.setText("Bạn hãy di chuyển mũi sao cho con trỏ chuột di chuyển đến cái nút to màu vàng ở góc khung.")
                    self.lbl_sub_guide1.setStyleSheet("font-size: 15px; color: #475568;")
                
        elif config.trial_task_stage == 2 and not self.btn_next2.isVisible():
            if self.main_app.is_engine_running:
                if config.system_state == "RUNNING":
                    self.lbl_sub_guide2.setText("Há mồm trong 1.5 giây để bật tính năng cuộn chuột, sau đó hãy cúi đầu xuống để cuộn xuống và ngửa lên để cuộn lên.")
                    self.lbl_sub_guide2.setStyleSheet("font-size: 15px; color: #3F5EFB; font-weight: bold;")
            
            scroll_bar = self.news_text.verticalScrollBar()
            if scroll_bar.value() >= scroll_bar.maximum() - 2:
                self.lbl_sub_guide2.setText("Xuất sắc! Bạn đã cuộn xuống dòng cuối cùng thành công.")
                self.lbl_sub_guide2.setStyleSheet("font-size: 15px; color: #3F5EFB; font-weight: bold;")
                self.btn_next2.show()
                
        elif config.trial_task_stage == 3:
            is_focused = self.chat_input.hasFocus()
            config.is_chat_input_focused = is_focused 
            
            # 🚀 HACK GIẢI PHÁP ĐỘNG: GỬI LỆNH ÉP CỬA SỔ BÀN PHÍM ẢO XUỐNG ĐÁY MÀN HÌNH CHỐNG CHE Ô CHAT
            # Tìm kiếm window bằng chuỗi tiêu đề cục bộ của module bàn phím ảo Qt
            if config.is_keyboard_open:
                for widget in QApplication.topLevelWidgets():
                    if widget.windowTitle() == "EzTouch Virtual Keyboard" or "Keyboard" in widget.windowTitle():
                        # Lấy kích thước chuẩn của thanh tác vụ màn hình người dùng
                        screen_geo = QApplication.primaryScreen().geometry()
                        kw = widget.width() if widget.width() > 100 else 760 
                        kh = widget.height() if widget.height() > 100 else 320
                        # Ép tọa độ X chính giữa đáy, Y chạm sát biên rìa dưới màn hình (trừ hao 50px khoảng cách thanh Taskbar Windows)
                        target_x = (screen_geo.width() - kw) // 2
                        target_y = screen_geo.height() - kh - 50
                        if widget.geometry().y() < target_y - 20 or widget.geometry().y() > target_y + 20:
                            widget.move(target_x, target_y)
            
            if not is_focused:
                self.lbl_sub_guide3.setText("Hãy nhấp vào ô tin nhắn để nhắn tin")
                self.lbl_sub_guide3.setStyleSheet("font-size: 15px; color: #DC2626; font-weight: bold;")
                config.trial_keyboard_warning_text = "CHUA NHAP VAO O CHAT! HAY NHAP VAO ROI MOI GO CHU NHE!"
            else:
                config.trial_keyboard_warning_text = "" 
                if not config.is_keyboard_open:
                    self.lbl_sub_guide3.setText("Tuyệt vời! Bây giờ hãy nhìn sang thanh công cụ dọc, NHẤP VÀO NÚT '⌨ ON' để mở bàn phím ảo.")
                    self.lbl_sub_guide3.setStyleSheet("font-size: 15px; color: #651FFF; font-weight: bold;")
                elif config.is_keyboard_open and len(self.chat_input.text()) < 3:
                    self.lbl_sub_guide3.setText("Bàn phím đã cố định dưới đáy! Hãy di chuyển mũi vào ô chữ bất kỳ trên bàn phím ảo và giữ đó 2 giây hoặc há mồm để nhấp.")
                    self.lbl_sub_guide3.setStyleSheet("font-size: 14px; color: #3F5EFB; font-weight: bold;")
                elif len(self.chat_input.text()) >= 3 and config.is_keyboard_open:
                    self.lbl_sub_guide3.setText("Quá đỉnh! Giờ hãy ấn lại nút '⌨ OFF' ở thanh công cụ để tắt bàn phím ảo.")
                    self.lbl_sub_guide3.setStyleSheet("font-size: 15px; color: #DC2626; font-weight: bold;")
                elif len(self.chat_input.text()) >= 3 and not config.is_keyboard_open:
                    self.lbl_sub_guide3.setText("Hoàn hảo! Bạn đã tắt bàn phím ảo thành công.")
                    self.lbl_sub_guide3.setStyleSheet("font-size: 15px; color: #3F5EFB; font-weight: bold;")
                    self.btn_next3.show()

        elif config.trial_task_stage == 4 and not self.btn_next4.isVisible():
            if config.system_state == "PAUSED":
                self.has_triggered_pause = True  
                self.lbl_sub_guide4.setText("Tốt lắm! Giờ bạn hãy thực hành quay lại bằng cách nhấn nút 'RESUME' màu xanh trên thanh công cụ.")
                self.lbl_sub_guide4.setStyleSheet("font-size: 15px; color: #3F5EFB; font-weight: bold;")
            
            elif config.system_state == "RUNNING" and self.has_triggered_pause:
                self.lbl_sub_guide4.setText("Xuất sắc! Bạn đã làm chủ hoàn toàn cơ chế nghỉ ngơi sinh học.")
                self.lbl_sub_guide4.setStyleSheet("font-size: 16px; color: #3F5EFB; font-weight: bold;")
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

# =========================================================================
# 🌟 THANH CÔNG CỤ DỌC TOÀN NĂNG (FITT'S LAW MIDDLE-LEFT EDGE DESTINATION)
# =========================================================================
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
            "QWidget { background-color: #F8FAFC; border: 3px solid #3F5EFB; border-top-right-radius: 20px; border-bottom-right-radius: 20px; }"
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
            "QPushButton { background-color: #3F5EFB; color: #FFFFFF; border: none; border-top-right-radius: 10px; border-bottom-right-radius: 10px; font-weight: bold; font-size: 12px; }"
            "QPushButton:hover { background-color: #5C7CFA; }"
        )
        self.btn_slide_handle.clicked.connect(self.toggle_collapse)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(2, 2)
        shadow.setColor(QColor(63, 94, 251, 30))
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
            self.btn_toggle_pause.setText("RESUME")
            self.btn_toggle_pause.setStyleSheet(STYLE_TOOLBAR_RESUME)
        else:
            self.btn_toggle_pause.setText("PAUSE")
            self.btn_toggle_pause.setStyleSheet(STYLE_TOOLBAR_PAUSE)
            
        if not config.is_keyboard_open:
            self.btn_toggle_keyboard.setText("⌨ ON")
            self.btn_toggle_keyboard.setStyleSheet(
                "QPushButton { background-color: #475569; color: white; font-size: 16px; font-weight: bold; border-radius: 16px; border: none; }"
                "QPushButton:hover { background-color: #334155; margin-top: -2px; margin-bottom: 2px; }"
                "QPushButton:pressed { background-color: #1E293B; margin-top: 2px; margin-bottom: -2px; }"
            )
        else:
            self.btn_toggle_keyboard.setText("⌨ OFF")
            self.btn_toggle_keyboard.setStyleSheet(
                "QPushButton { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #651FFF, stop:1 #7C4DFF); color: white; font-size: 16px; font-weight: bold; border-radius: 16px; border: none; }"
                "QPushButton:hover { background-color: #7C4DFF; margin-top: -2px; margin-bottom: 2px; }"
                "QPushButton:pressed { background-color: #5314D1; margin-top: 2px; margin-bottom: -2px; }"
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
        self.setWindowTitle("EzTouch - Thắp Sáng Thế Giới Riêng")
        
        self.setMinimumSize(580, 480) 
        self.resize(620, 520)
        self.setStyleSheet("QWidget { background-color: #F8FAFC; color: #1E293B; font-family: 'Segoe UI', sans-serif; }")

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
        # PART I: KHUNG THẺ THƯƠNG HIỆU CAO CẤP (NEUMORPHIC BRAND CARD)
        # =========================================================================
        self.brand_card = QWidget()
        self.brand_card.setStyleSheet("QWidget { background-color: #FFFFFF; border-radius: 24px; }")
        
        card_shadow = QGraphicsDropShadowEffect()
        card_shadow.setBlurRadius(40)
        card_shadow.setOffset(0, 10)
        card_shadow.setColor(QColor(63, 94, 251, 15)) 
        self.brand_card.setGraphicsEffect(card_shadow)

        self.brand_layout = QVBoxLayout(self.brand_card)
        self.brand_layout.setContentsMargins(35, 30, 35, 30)
        self.brand_layout.setSpacing(10) 

        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setStyleSheet("QLabel { background: transparent; border: none; }")
        
        self.team_label = QLabel("by SigmaCode")
        self.team_label.setAlignment(Qt.AlignCenter)
        
        self.subtitle_label = QLabel("HỆ THỐNG ĐIỀU KHIỂN CHUỘT MÁY TÍNH BẰNG KHUÔN MẶT")
        self.subtitle_label.setAlignment(Qt.AlignCenter)

        self.brand_layout.addWidget(self.logo_label, alignment=Qt.AlignCenter)
        self.brand_layout.addWidget(self.team_label)
        self.brand_layout.addWidget(self.subtitle_label)

        self.brand_card.setMaximumWidth(900)

        # =========================================================================
        # PART II: PHÂN VÙNG HỆ THỐNG NÚT BẤM TƯƠNG TÁC CHỦ ĐỘNG (ACTION COMPONENT)
        # =========================================================================
        self.action_button = QPushButton("STANDARD MODE")
        self.action_button.setCursor(Qt.PointingHandCursor)
        self.action_button.clicked.connect(self.handle_engine_toggle)
        
        self.trial_button = QPushButton("TRIAL")
        self.trial_button.setCursor(Qt.PointingHandCursor)
        self.trial_button.clicked.connect(self.start_trial_mode)

        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(20) 
        self.button_layout.addWidget(self.action_button, 6)
        self.button_layout.addWidget(self.trial_button, 4)

        self.btn_container = QWidget()
        self.btn_container.setLayout(self.button_layout)
        self.btn_container.setFixedWidth(480) 

        # =========================================================================
        # PART III: PHÂN VÙNG SLOGAN CHÂN TRANG (HUMANITARIAN FOOTER COMPONENT)
        # =========================================================================
        self.status_footer = QLabel("“Từ những vệt sáng cuối trời, thắp sáng những thế giới riêng”")
        self.status_footer.setAlignment(Qt.AlignCenter)

        self.main_layout.addWidget(self.brand_card, alignment=Qt.AlignCenter)
        self.main_layout.addStretch(4) 
        self.main_layout.addWidget(self.btn_container, alignment=Qt.AlignCenter)
        self.main_layout.addStretch(2) 
        self.main_layout.addWidget(self.status_footer)
        
        self.setLayout(self.main_layout)
        
        self.execute_responsive_ui_scaling(self.width(), self.height())

    def resizeEvent(self, event):
        """
        🔮 RESPONSIVE INTERACTION ENGINE V4: THE LAWS OF WHITE SPACE
        Tự động bắt chu kỳ thu phóng của cửa sổ để tính ma trận không gian thích ứng.
        """
        w = event.size().width()
        h = event.size().height()
        self.execute_responsive_ui_scaling(w, h)
        super().resizeEvent(event)

    def execute_responsive_ui_scaling(self, w, h):
        """Thuật toán cân bằng mật độ đồ họa và typography chuyển đổi động"""
        ideal_logo_h = int(h * 0.15)
        logo_h = np.clip(ideal_logo_h, 65, 125)
        
        logo_pixmap = get_transparent_logo_pixmap("picture/workmark.png", logo_h)
        if not logo_pixmap.isNull():
            self.logo_label.setPixmap(logo_pixmap)
        
        ideal_container_w = int(w * 0.75)
        container_w = np.clip(ideal_container_w, 480, 720)
        self.btn_container.setFixedWidth(container_w)
        
        ideal_btn_h = int(h * 0.15)
        btn_h = np.clip(ideal_btn_h, 85, 120)
        self.action_button.setFixedHeight(btn_h)
        self.trial_button.setFixedHeight(btn_h)
        
        base_scale = (w * h) / 270000.0
        
        font_size_btn = int(np.clip(16 + base_scale * 1.5, 16, 24))
        font_size_team = int(np.clip(13 + base_scale * 0.6, 13, 17))
        font_size_sub = int(np.clip(10 + base_scale * 0.4, 10, 12))
        font_size_foot = int(np.clip(12 + base_scale * 0.6, 12, 16))
        
        self.action_button.setStyleSheet(STYLE_BLUE_BUTTON + f"font-size: {font_size_btn}px;")
        self.trial_button.setStyleSheet(STYLE_ORANGE_BUTTON + f"font-size: {font_size_btn}px;")
        
        self.team_label.setStyleSheet(f"QLabel {{ font-size: {font_size_team}px; font-weight: 600; font-style: italic; color: #64748B; letter-spacing: 3px; }}")
        self.subtitle_label.setStyleSheet(f"QLabel {{ font-size: {font_size_sub}px; font-weight: 700; color: #94A3B8; letter-spacing: 1.5px; }}")
        self.status_footer.setStyleSheet(f"QLabel {{ font-size: {font_size_foot}px; font-weight: 500; color: #64748B; font-style: italic; }}")

    def update_button_style(self):
        if not self.is_engine_running:
            self.action_button.setText("STANDARD MODE")
            self.trial_button.setEnabled(True)
        else:
            self.action_button.setText("DỪNG HỆ THỐNG")
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