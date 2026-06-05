# eztouch.py
import sys
import os
import cv2
from PySide6.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, 
                               QHBoxLayout, QLabel, QGraphicsDropShadowEffect, 
                               QStackedWidget, QTextEdit, QLineEdit, QProgressBar)
from PySide6.QtCore import QThread, Qt, QTimer
from PySide6.QtGui import QColor, QFont

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import main
import config

class FaceThread(QThread):
    def run(self):
        main.main()  

STYLE_BLUE_BUTTON = """
    QPushButton {
        background-color: #3182CE; color: white; font-size: 16px; font-weight: bold;
        border: none; border-radius: 14px; padding: 14px;
    }
    QPushButton:hover { background-color: #4299E1; margin-top: -2px; margin-bottom: 2px; }
    QPushButton:pressed { background-color: #2B6CB0; margin-top: 0px; margin-bottom: 0px; }
"""

STYLE_ORANGE_BUTTON = """
    QPushButton {
        background-color: #ED8936; color: white; font-size: 18px; font-weight: bold;
        border: none; border-radius: 14px; padding: 14px;
    }
    QPushButton:hover { background-color: #F6AD55; margin-top: -2px; margin-bottom: 2px; }
    QPushButton:pressed { background-color: #DD6B20; margin-top: 0px; margin-bottom: 0px; }
"""

class EzTouchTrialSpace(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.setWindowTitle("EzTouch - Không Gian Trải Nghiệm Thử Nghiệm")
        self.setWindowFlags(Qt.Window) 
        self.showMaximized() 
        
        self.setStyleSheet("""
            QWidget {
                background-color: #EDF2F7;
                color: #2D3748;
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
        
        self.header_label = QLabel("EZTOUCH TRIAL")
        self.header_label.setAlignment(Qt.AlignCenter)
        self.header_label.setStyleSheet("font-size: 26px; font-weight: 900; color: #2B6CB0; letter-spacing: 1.5px;")
        self.layout.addWidget(self.header_label)
        
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
        self.btn_exit_trial.setStyleSheet("""
            QPushButton { background-color: #4A5568; color: white; border-radius: 10px; padding: 10px; font-weight: 600; border: none; }
            QPushButton:hover { background-color: #718096; }
        """)
        self.btn_exit_trial.clicked.connect(self.exit_trial)
        self.layout.addWidget(self.btn_exit_trial, alignment=Qt.AlignRight)

    def setup_page_intro(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)
        
        lbl_title = QLabel("Chào mừng bạn đến với EzTouch")
        lbl_title.setStyleSheet("font-size: 42px; font-weight: 900; color: #3182CE;")
        
        lbl_author = QLabel("by the SigmaCode")
        lbl_author.setStyleSheet("font-size: 18px; font-weight: 700; font-style: italic; color: #4A5568; letter-spacing: 2px;")
        
        lbl_mission = QLabel(
            "SỨ MỆNH DỰ ÁN:\n"
            "EzTouch ra đời nhằm mục đích xóa bỏ rào cản số, mang không gian công nghệ\n"
            "đến gần hơn với trẻ em khuyết tật vận động chi trên và người cao tuổi mắc chứng bệnh run vô thức.\n"
            "Chúng tôi tin rằng từ những vệt sáng cuối trời, mọi thế giới riêng đều xứng đáng được thắp sáng."
        )
        lbl_mission.setStyleSheet("font-size: 16px; line-height: 160%; color: #4A5568; font-weight: 500; text-align: center;")
        lbl_mission.setAlignment(Qt.AlignCenter)

        self.calibration_panel = QWidget()
        self.calibration_panel.setFixedWidth(780)
        self.calibration_panel.setStyleSheet("QWidget { background-color: #FFFFFF; border-radius: 24px; border: 1px solid #E2E8F0; }")
        
        p_shadow = QGraphicsDropShadowEffect()
        p_shadow.setBlurRadius(40)
        p_shadow.setOffset(0, 10)
        p_shadow.setColor(QColor(49, 130, 206, 40))
        self.calibration_panel.setGraphicsEffect(p_shadow)

        panel_layout = QVBoxLayout(self.calibration_panel)
        panel_layout.setContentsMargins(40, 35, 40, 35)
        panel_layout.setSpacing(20)
        
        self.lbl_calib_title = QLabel("🔮 THIẾT LẬP KHÔNG GIAN SINH HỌC CÁ NHÂN")
        self.lbl_calib_title.setStyleSheet("font-size: 19px; font-weight: 800; color: #2B6CB0; border: none;")
        self.lbl_calib_title.setAlignment(Qt.AlignCenter)
        
        self.lbl_calib_status = QLabel("👉 Vui lòng nghiêng nhẹ đầu sang TRÁI để chọn chế độ bảo vệ chống run,\nhoặc nghiêng đầu sang PHẢI để chọn chế độ lướt siêu tốc.")
        self.lbl_calib_status.setStyleSheet("font-size: 15px; color: #4A5568; font-weight: 600; line-height: 160%; border: none;")
        self.lbl_calib_status.setAlignment(Qt.AlignCenter)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(14)
        self.progress_bar.setStyleSheet("""
            QProgressBar { background-color: #EDF2F7; border-radius: 7px; border: none; }
            QProgressBar::chunk { 
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4299E1, stop:1 #3182CE); 
                border-radius: 7px; 
            }
        """)
        
        self.lbl_countdown = QLabel("⏱️ Đang đồng bộ tín hiệu mốc khuôn mặt thông minh...")
        self.lbl_countdown.setStyleSheet("font-size: 15px; font-weight: 700; color: #3182CE; border: none;")
        self.lbl_countdown.setAlignment(Qt.AlignCenter)
        
        panel_layout.addWidget(self.lbl_calib_title)
        panel_layout.addWidget(self.lbl_calib_status)
        panel_layout.addWidget(self.progress_bar)
        panel_layout.addWidget(self.lbl_countdown)
        
        self.btn_start_onboarding = QPushButton("BẮT ĐẦU TRẢI NGHIỆM ▶")
        self.btn_start_onboarding.setFixedSize(360, 56)
        self.btn_start_onboarding.setEnabled(False) 
        self.btn_start_onboarding.setStyleSheet("background-color: #CBD5E0; color: #A0AEC0; font-size: 16px; font-weight: bold; border-radius: 16px; border: none;")
        self.btn_start_onboarding.clicked.connect(self.handle_intro_finished)
        
        layout.addWidget(lbl_title, alignment=Qt.AlignCenter)
        layout.addWidget(lbl_author, alignment=Qt.AlignCenter)
        layout.addWidget(lbl_mission, alignment=Qt.AlignCenter)
        layout.addWidget(self.calibration_panel, alignment=Qt.AlignCenter)
        layout.addWidget(self.btn_start_onboarding, alignment=Qt.AlignCenter)
        self.stack.addWidget(page)

    def setup_page_task1(self):
        self.page1 = QWidget()
        self.layout1 = QVBoxLayout(self.page1)
        
        self.lbl_guide1 = QLabel("Task 1: DI CHUYỂN CHUỘT & CLICK SINH HỌC CHỦ ĐỘNG")
        self.lbl_guide1.setStyleSheet("font-size: 22px; font-weight: 700; color: #2B6CB0;")
        self.lbl_guide1.setAlignment(Qt.AlignCenter)
        
        self.lbl_sub_guide1 = QLabel("Bạn hãy di chuyển mũi sao cho con trỏ chuột di chuyển đến cái nút to màu cam ở góc màn hình.")
        self.lbl_sub_guide1.setStyleSheet("font-size: 16px; color: #4A5568; margin-bottom: 20px;")
        self.lbl_sub_guide1.setAlignment(Qt.AlignCenter)
        
        self.click_area = QWidget()
        self.click_area.setMinimumHeight(350)
        area_layout = QHBoxLayout(self.click_area)
        
        self.target_btn = QPushButton("BẤM VÀO TỚ\n(HÁ MỒM)")
        self.target_btn.setFixedSize(180, 100)
        self.target_btn.setStyleSheet("""
            QPushButton { background-color: #ED8936; color: white; border-radius: 20px; font-size: 15px; font-weight: bold; border: none; }
            QPushButton:hover { background-color: #F6AD55; }
        """)
        self.target_btn.clicked.connect(self.handle_task1_success)
        area_layout.addWidget(self.target_btn, alignment=Qt.AlignRight | Qt.AlignBottom)
        
        self.btn_next1 = QPushButton("TIẾP THEO SANG TASK 2 ▶")
        self.btn_next1.setFixedWidth(280)
        self.btn_next1.setStyleSheet(STYLE_BLUE_BUTTON)
        self.btn_next1.hide()
        self.btn_next1.clicked.connect(lambda: self.go_to_stage(2))
        
        self.layout1.addWidget(self.lbl_guide1)
        self.layout1.addWidget(self.lbl_sub_guide1)
        self.layout1.addWidget(self.click_area)
        self.layout1.addWidget(self.btn_next1, alignment=Qt.AlignCenter)
        self.stack.addWidget(self.page1)

    def setup_page_task2(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        self.lbl_guide2 = QLabel("Task 2: TÍNH NĂNG CUỘN TRANG (SCROLL MODE)")
        self.lbl_guide2.setStyleSheet("font-size: 22px; font-weight: 700; color: #2B6CB0;")
        self.lbl_guide2.setAlignment(Qt.AlignCenter)
        
        self.lbl_sub_guide2 = QLabel("Tiếp theo bạn hãy há mồm và giữ im đó trong vòng 1.3 giây.")
        self.lbl_sub_guide2.setStyleSheet("font-size: 16px; color: #E53E3E; font-weight: bold; margin-bottom: 10px;")
        self.lbl_sub_guide2.setAlignment(Qt.AlignCenter)
        
        self.news_text = QTextEdit()
        self.news_text.setReadOnly(True)
        self.news_text.setFont(QFont("Segoe UI", 12))
        self.news_text.setPlainText(
            "[BÁO CÁO KHOA HỌC] - ỨNG DỤNG MÔ HÌNH TOÁN HỌC TRONG TRỢ NĂNG SỐ 2026\n\n" +
            "Nghiên cứu chỉ ra rằng việc tương tác không tiếp xúc hỗ trợ bệnh nhân Parkinson phục hồi chức năng hành vi phản xạ rất tốt.\n" +
            "Hệ thống định vị mốc nhân trắc học khuôn mặt cho phép bắt chuẩn xác chuyển động đỉnh mũi...\n" +
            "Để đọc thêm thông tin chi tiết, người dùng cần học cách cuộn trang mà không dùng tay.\n" +
            "Tiến trình cuộn trang sử dụng vector gia tốc tuyến tính âm đè lớp của PyAutoGUI.\n" * 45 +
            "\n--- BẠN ĐÃ CUỘN ĐẾN CUỐI TRANG THÀNH CÔNG RỒI! ---"
        )
        self.news_text.setStyleSheet("background-color: white; border: 1px solid #CBD5E0; border-radius: 12px; padding: 15px;")
        
        self.btn_next2 = QPushButton("TIẾP THEO SANG TASK 3 ▶")
        self.btn_next2.setFixedWidth(280)
        self.btn_next2.setStyleSheet(STYLE_BLUE_BUTTON)
        self.btn_next2.hide()
        self.btn_next2.clicked.connect(lambda: self.go_to_stage(3))
        
        layout.addWidget(self.lbl_guide2)
        layout.addWidget(self.lbl_sub_guide2)
        layout.addWidget(self.news_text)
        layout.addWidget(self.btn_next2, alignment=Qt.AlignCenter)
        self.stack.addWidget(page)

    def setup_page_task3(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        self.lbl_guide3 = QLabel("Task 3: LÀM QUEN BÀN PHÍM ẢO MA TRẬN ĐỘC LẬP")
        self.lbl_guide3.setStyleSheet("font-size: 22px; font-weight: 700; color: #2B6CB0;")
        self.lbl_guide3.setAlignment(Qt.AlignCenter)
        
        self.lbl_sub_guide3 = QLabel("Hãy nhấp (há mồm nhanh) vào ô nhắn tin Messenger giả lập bên dưới.")
        self.lbl_sub_guide3.setStyleSheet("font-size: 16px; color: #4A5568; margin-bottom: 10px;")
        self.lbl_sub_guide3.setAlignment(Qt.AlignCenter)
        
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Nhấp vào đây để soạn tin nhắn chat...")
        self.chat_input.setMinimumHeight(60)
        self.chat_input.setFont(QFont("Segoe UI", 14))
        self.chat_input.setStyleSheet("background-color: white; border: 2px solid #3182CE; border-radius: 12px; padding-left: 15px;")
        self.chat_input.clicked_connect_flag = False
        self.chat_input.cursorPositionChanged.connect(self.handle_chat_input_focused)
        
        self.btn_next3 = QPushButton("TIẾP THEO SANG TASK 4 ▶")
        self.btn_next3.setFixedWidth(280)
        self.btn_next3.setStyleSheet(STYLE_BLUE_BUTTON)
        self.btn_next3.hide()
        self.btn_next3.clicked.connect(lambda: self.go_to_stage(4))
        
        layout.addWidget(self.lbl_guide3)
        layout.addWidget(self.lbl_sub_guide3)
        layout.addWidget(self.chat_input)
        layout.addStretch()
        layout.addWidget(self.btn_next3, alignment=Qt.AlignCenter)
        self.stack.addWidget(page)

    def setup_page_task4(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        
        self.lbl_guide4 = QLabel("Task 4: CƠ CHẾ NGHỈ NGƠI TẠM DỪNG (PAUSE/RESUME)")
        self.lbl_guide4.setStyleSheet("font-size: 22px; font-weight: 700; color: #2B6CB0;")
        self.lbl_guide4.setAlignment(Qt.AlignCenter)
        
        self.lbl_sub_guide4 = QLabel("Khi bạn muốn nghỉ ngơi hãy ấn vào nút 'PAUSE' màu đỏ trên thanh công cụ dọc góc trái nhé!")
        self.lbl_sub_guide4.setStyleSheet("font-size: 18px; color: #E53E3E; font-weight: bold; margin: 30px;")
        self.lbl_sub_guide4.setAlignment(Qt.AlignCenter)
        
        self.btn_next4 = QPushButton("HOÀN THÀNH TOÀN BỘ HÀNH TRÌNH ▶")
        self.btn_next4.setFixedWidth(320)
        self.btn_next4.setStyleSheet(STYLE_BLUE_BUTTON)
        self.btn_next4.hide()
        self.btn_next4.clicked.connect(lambda: self.go_to_stage(5))
        
        layout.addWidget(self.lbl_guide4)
        layout.addWidget(self.lbl_sub_guide4)
        layout.addWidget(self.btn_next4, alignment=Qt.AlignCenter)
        self.stack.addWidget(page)

    def setup_page_finish(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        
        lbl_congrat = QLabel("🎉 CHÚC MỪNG BẠN NHÉEE! 🎉")
        lbl_congrat.setStyleSheet("font-size: 36px; font-weight: 900; color: #38A169;")
        
        lbl_content = QLabel(
            "Bạn đã làm chủ được tất cả các thao tác cơ bản của hệ thống EzTouch rồi đó!\n"
            "Giờ hãy tự tin trải nghiệm ứng dụng thực tế ngoài không gian số.\n"
            "Tất nhiên, sau này bạn có thể quay lại đây luyện tập bất cứ lúc nào nếu quên."
        )
        lbl_content.setStyleSheet("font-size: 16px; font-weight: 600; color: #4A5568; margin: 25px; line-height: 160%; text-align: center;")
        lbl_content.setAlignment(Qt.AlignCenter)
        
        btn_back_home = QPushButton("QUAY LẠI TRANG CHỦ")
        btn_back_home.setFixedSize(280, 60)
        btn_back_home.setStyleSheet(STYLE_ORANGE_BUTTON)
        btn_back_home.clicked.connect(self.exit_trial)
        
        layout.addWidget(lbl_congrat)
        layout.addWidget(lbl_content)
        layout.addWidget(btn_back_home, alignment=Qt.AlignCenter)
        self.stack.addWidget(page)

    def go_to_stage(self, stage_idx):
        config.trial_task_stage = stage_idx
        self.stack.setCurrentIndex(stage_idx)
        if stage_idx != 3:
            config.is_keyboard_open = False

    def handle_intro_finished(self):
        self.go_to_stage(1)

    def handle_task1_success(self):
        if config.trial_task_stage == 1:
            self.lbl_sub_guide1.setText("Bạn làm tốt lắm ý, chuẩn bị sẵn sàng cho tính năng mới nào!")
            self.lbl_sub_guide1.setStyleSheet("font-size: 18px; color: #38A169; font-weight: bold;")
            self.target_btn.hide()
            self.btn_next1.show()

    def handle_chat_input_focused(self):
        if config.trial_task_stage == 3 and not self.chat_input.clicked_connect_flag:
            self.chat_input.clicked_connect_flag = True
            self.lbl_sub_guide3.setText("Tuyệt vời! Bây giờ hãy nhìn sang thanh công cụ dọc, NHẤP VÀO NÚT 'KB ON' để mở bàn phím ảo lên.")
            self.lbl_sub_guide3.setStyleSheet("font-size: 16px; color: #ED8936; font-weight: bold;")

    def monitor_user_actions(self):
        if not config.is_trial_active: return
        
        # --- Realtime Monitor Stage 0 ---
        if config.trial_task_stage == 0:
            self.progress_bar.setValue(config.trial_countdown_pct)
            if config.CURRENT_MODE == "UNDECIDED":
                self.lbl_countdown.setText("⏱️ Đang chờ nhận diện cử chỉ nghiêng đầu chọn chế độ...")
            elif config.CURRENT_MODE in ["PARKINSON", "REGULAR"] and config.CALIBRATED_CENTER_X == 0.5:
                mode_name = "BẢO VỆ CHỐNG RUN" if config.CURRENT_MODE == "PARKINSON" else "LƯỚT SIÊU TỐC"
                self.lbl_calib_status.setText(f"Đã kích hoạt chế độ: {mode_name}.\nBây giờ, hãy GIỮ YÊN VỊ TRÍ NHÌN THOẢI MÁI ĐỂ THIẾT LẬP TÂM AN TOÀN.")
                self.lbl_countdown.setText("⏱️ Đang đồng bộ và định vị vùng an toàn...")
            else:
                self.lbl_calib_status.setText("🎉 Thiết lập không gian sinh học thành công! Hệ thống đã tự điều chỉnh theo thể trạng của bạn.")
                self.lbl_calib_status.setStyleSheet("font-size: 15px; color: #38A169; font-weight: bold; line-height: 140%; border: none;")
                self.lbl_countdown.setText("✅ Không gian sinh học đã sẵn sàng 100%!")
                self.btn_start_onboarding.setEnabled(True)
                self.btn_start_onboarding.setStyleSheet(STYLE_BLUE_BUTTON)

        # --- Realtime Monitor Task 1 ---
        elif config.trial_task_stage == 1 and self.target_btn.isVisible():
            btn_pos = self.target_btn.mapToGlobal(self.target_btn.rect().topLeft())
            import pyautogui
            mx, my = pyautogui.position()
            if (btn_pos.x() <= mx <= btn_pos.x() + self.target_btn.width() and 
                btn_pos.y() <= my <= btn_pos.y() + self.target_btn.height()):
                self.lbl_sub_guide1.setText("Bạn đã làm tốt lắm, hãy HÁ MỒM để thực hiện cú nhấp chuột nào!")
                self.lbl_sub_guide1.setStyleSheet("font-size: 16px; color: #38A169; font-weight: bold;")
            else:
                if mx > config.SCREEN_WIDTH // 3 or my > config.SCREEN_HEIGHT // 3:
                    self.lbl_sub_guide1.setText("Cố lên nào, sắp được rồi! Hãy di chuyển con trỏ vào ô màu cam nhé.")
                    self.lbl_sub_guide1.setStyleSheet("font-size: 16px; color: #ED8936; font-weight: bold;")
                else:
                    self.lbl_sub_guide1.setText("Bạn hãy di chuyển mũi sao cho con trỏ chuột di chuyển đến cái nút to màu cam ở góc màn hình.")
                    self.lbl_sub_guide1.setStyleSheet("font-size: 16px; color: #4A5568;")
                
        # --- Realtime Monitor Task 2 ---
        elif config.trial_task_stage == 2 and not self.btn_next2.isVisible():
            if self.main_app.is_engine_running:
                if config.system_state == "RUNNING":
                    self.lbl_sub_guide2.setText("Đã bật tính năng cuộn chuột, giờ hãy cúi đầu xuống để cuộn xuống và ngửa lên để cuộn lên.")
                    self.lbl_sub_guide2.setStyleSheet("font-size: 16px; color: #3182CE; font-weight: bold;")
            
            scroll_bar = self.news_text.verticalScrollBar()
            if scroll_bar.value() >= scroll_bar.maximum() - 2:
                self.lbl_sub_guide2.setText("Xuất sắc! Bạn đã cuộn xuống dòng cuối cùng thành công.")
                self.lbl_sub_guide2.setStyleSheet("font-size: 16px; color: #38A169; font-weight: bold;")
                self.btn_next2.show()
                
        # --- Realtime Monitor Task 3 ---
        elif config.trial_task_stage == 3:
            self.chat_input.setFocus()
            if config.is_keyboard_open and "HÃY DI CHUYỂN" not in self.lbl_sub_guide3.text().upper():
                self.lbl_sub_guide3.setText("Bàn phím đã mở! Hãy di chuyển mũi vào ô chữ bất kỳ trên bàn phím ảo và giữ đó 2 giây hoặc há mồm để nhấp.")
                self.lbl_sub_guide3.setStyleSheet("font-size: 15px; color: #2B6CB0; font-weight: bold;")
            if len(self.chat_input.text()) >= 3 and config.is_keyboard_open:
                self.lbl_sub_guide3.setText("Quá đỉnh! Giờ hãy ấn lại nút 'KB OFF' trên thanh công cụ dọc để tắt bàn phím ảo đi (Nút màu cam đậm).")
                self.lbl_sub_guide3.setStyleSheet("font-size: 16px; color: #E53E3E; font-weight: bold;")
            if len(self.chat_input.text()) >= 3 and not config.is_keyboard_open:
                self.lbl_sub_guide3.setText("Hoàn hảo! Bạn đã tắt bàn phím ảo thành công.")
                self.lbl_sub_guide3.setStyleSheet("font-size: 16px; color: #38A169; font-weight: bold;")
                self.btn_next3.show()

        # --- Realtime Monitor Task 4 ---
        elif config.trial_task_stage == 4 and not self.btn_next4.isVisible():
            if config.system_state == "PAUSED":
                self.has_triggered_pause = True  
                self.lbl_sub_guide4.setText("Tốt lắm! Giờ bạn hãy thực hành quay lại bằng cách nhấn nút 'RESUME' màu xanh trên thanh công cụ hoặc há mồm trong 3 giây.")
                self.lbl_sub_guide4.setStyleSheet("font-size: 16px; color: #3182CE; font-weight: bold;")
            
            elif config.system_state == "RUNNING" and self.has_triggered_pause:
                self.lbl_sub_guide4.setText("Xuất sắc! Bạn đã làm chủ hoàn toàn cơ chế nghỉ ngơi sinh học.")
                self.lbl_sub_guide4.setStyleSheet("font-size: 18px; color: #38A169; font-weight: bold;")
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

# =========================================================
# 🌟 THANH CÔNG CỤ DỌC TRỢ NĂNG (ACCESSIBILITY TOOLBAR)
# =========================================================
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
        self.toolbar_body.setFixedWidth(90)
        self.toolbar_body.setStyleSheet(
            "QWidget { background-color: #F3F6FA; border: 2px solid #3182CE; border-top-right-radius: 18px; border-bottom-right-radius: 18px; }"
        )
        
        body_layout = QVBoxLayout(self.toolbar_body)
        body_layout.setContentsMargins(6, 20, 6, 20)
        body_layout.setSpacing(15)
        
        self.btn_toggle_pause = QPushButton()
        self.btn_toggle_pause.setFixedSize(76, 76) 
        self.btn_toggle_pause.setCursor(Qt.PointingHandCursor)
        self.btn_toggle_pause.clicked.connect(self.handle_pause_click)
        
        self.btn_toggle_keyboard = QPushButton()
        self.btn_toggle_keyboard.setFixedSize(76, 76) 
        self.btn_toggle_keyboard.setCursor(Qt.PointingHandCursor)
        self.btn_toggle_keyboard.clicked.connect(self.handle_keyboard_click)
        
        body_layout.addWidget(self.btn_toggle_pause)
        body_layout.addWidget(self.btn_toggle_keyboard)
        
        self.btn_slide_handle = QPushButton("◀")
        self.btn_slide_handle.setFixedSize(22, 70)
        self.btn_slide_handle.setCursor(Qt.PointingHandCursor)
        self.btn_slide_handle.setStyleSheet(
            "QPushButton { background-color: #3182CE; color: #FFFFFF; border: none; border-top-right-radius: 10px; border-bottom-right-radius: 10px; font-weight: bold; font-size: 12px; }"
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
        total_w = 112 if self.is_expanded else 22
        total_h = 210
        pos_x = 0
        pos_y = (config.SCREEN_HEIGHT - total_h) // 2
        self.setGeometry(pos_x, pos_y, total_w, total_h)

    def update_button_styles(self):
        if config.system_state == "PAUSED":
            self.btn_toggle_pause.setText("RESUME")
            self.btn_toggle_pause.setStyleSheet(
                "QPushButton { background-color: #3182CE; color: white; font-size: 12px; font-weight: bold; border-radius: 16px; border: none; }"
                "QPushButton:hover { background-color: #4299E1; margin-top: -2px; }"
            )
        else:
            self.btn_toggle_pause.setText("PAUSE")
            self.btn_toggle_pause.setStyleSheet(
                "QPushButton { background-color: #E53E3E; color: white; font-size: 12px; font-weight: bold; border-radius: 16px; border: none; }"
                "QPushButton:hover { background-color: #FC8181; margin-top: -2px; }"
            )
            
        if not config.is_keyboard_open:
            self.btn_toggle_keyboard.setText("KB ON")
            self.btn_toggle_keyboard.setStyleSheet(
                "QPushButton { background-color: #4A5568; color: white; font-size: 12px; font-weight: bold; border-radius: 16px; border: none; }"
                "QPushButton:hover { background-color: #718096; margin-top: -2px; }"
            )
        else:
            self.btn_toggle_keyboard.setText("KB OFF")
            self.btn_toggle_keyboard.setStyleSheet(
                "QPushButton { background-color: #ED8936; color: white; font-size: 12px; font-weight: bold; border-radius: 16px; border: none; }"
                "QPushButton:hover { background-color: #F6AD55; margin-top: -2px; }"
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

# =========================================================
# TAB KHỞI CHẠY GỐC (GIỮ NGUYÊN KIẾN TRÚC)
# =========================================================
class EzTouchApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EzTouch - Thắp Sáng Thế Giới Riêng")
        self.setFixedSize(560, 420)
        self.setStyleSheet("QWidget { background-color: #F3F6FA; color: #2D3748; font-family: 'Segoe UI', sans-serif; }")

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
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 35, 40, 35)
        main_layout.setSpacing(10)

        title_label = QLabel("EzTouch")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("QLabel { font-size: 46px; font-weight: 850; color: #3182CE; border: none; }")
        
        team_label = QLabel("by SigmaCode")
        team_label.setAlignment(Qt.AlignCenter)
        team_label.setStyleSheet("QLabel { font-size: 13px; font-weight: 600; font-style: italic; color: #4A5568; letter-spacing: 3px; }")
        
        subtitle_label = QLabel("HỆ THỐNG ĐIỀU KHIỂN CHUỘT MÁY TÍNH BẰNG KHUÔN MẶT")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("QLabel { font-size: 10px; font-weight: 700; color: #718096; letter-spacing: 1.5px; }")

        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        self.action_button = QPushButton("STANDARD MODE")
        self.action_button.setCursor(Qt.PointingHandCursor)
        self.action_button.setFixedHeight(95)
        self.action_button.setStyleSheet(STYLE_BLUE_BUTTON.replace("font-size: 16px;", "font-size: 18px;"))
        self.action_button.clicked.connect(self.handle_engine_toggle)
        
        self.trial_button = QPushButton("TRIAL")
        self.trial_button.setCursor(Qt.PointingHandCursor)
        self.trial_button.setFixedHeight(95)
        self.trial_button.setStyleSheet(STYLE_ORANGE_BUTTON.replace("font-size: 16px;", "font-size: 18px;"))
        self.trial_button.clicked.connect(self.start_trial_mode)

        button_layout.addWidget(self.action_button, 6)
        button_layout.addWidget(self.trial_button, 4)

        status_footer = QLabel("“Từ những vệt sáng cuối trời, thắp sáng những thế giới riêng”")
        status_footer.setAlignment(Qt.AlignCenter)
        status_footer.setStyleSheet("QLabel { font-size: 13px; font-weight: 500; color: #4A5568; font-style: italic; margin-top: 15px; }")

        main_layout.addWidget(title_label)
        main_layout.addWidget(team_label)
        main_layout.addWidget(subtitle_label)
        main_layout.addStretch()
        main_layout.addLayout(button_layout)
        main_layout.addStretch()
        main_layout.addWidget(status_footer)
        
        self.setLayout(main_layout)

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