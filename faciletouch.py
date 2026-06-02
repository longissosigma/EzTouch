from PySide6.QtWidgets import *
import sys
from PySide6.QtCore import QThread, Qt 
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtGui import QColor


class FaceThread(QThread):

    def run(self):
        main.main()  

import main


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FacileTouch")
        self.setStyleSheet("""
        QWidget{
        background-color:#1E1E1E;
        border:1px solid #444444;        }
        """)

        self.face_thread = None

        self.resize(1000, 500)

        self.open_button = QPushButton("START")
        self.close_button = QPushButton("STOP")

        shadow1 = QGraphicsDropShadowEffect()
        shadow1.setBlurRadius(50)
        shadow1.setOffset(15, 15)
        shadow1.setColor(QColor(0, 0, 0, 180))
        self.open_button.setGraphicsEffect(shadow1)

        shadow2 = QGraphicsDropShadowEffect()
        shadow2.setBlurRadius(50)
        shadow2.setOffset(15, 15)
        shadow2.setColor(QColor(0, 0, 0, 180))
        self.close_button.setGraphicsEffect(shadow2)

        self.open_button.setStyleSheet("QPushButton{font-family:'Press Start 2P';font-size:50px;font-weight:bold;color:white;background-color:#00A000;border-top:2px solid #40FF40;border-left:2px solid #40FF40;border-right:2px solid #007000;border-bottom:8px solid #007000;border-radius:15px;}QPushButton:pressed{background-color:#008000;border-bottom:2px solid #007000;padding-top:6px;}")
        self.close_button.setStyleSheet("QPushButton{font-family:'Press Start 2P';font-size:50px;font-weight:bold;color:white;background-color:#FF2020;border-top:2px solid #FF8080;border-left:2px solid #FF8080;border-right:2px solid #B00000;border-bottom:8px solid #B00000;border-radius:15px;}QPushButton:pressed{background-color:#D00000;border-bottom:2px solid #B00000;padding-top:6px;}")
        self.open_button.setCursor(Qt.PointingHandCursor)
        self.close_button.setCursor(Qt.PointingHandCursor)
        self.open_button.clicked.connect(self.handle_click)
        self.close_button.clicked.connect(self.handle_click)


        layout = QHBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(10)
        layout.addWidget(self.open_button, 1)
        layout.addWidget(self.close_button, 1)

        
        
        self.setLayout(layout)

    def handle_click(self):
        button = self.sender()
        if button == self.open_button:
            if self.face_thread is None or not self.face_thread.isRunning():
                self.face_thread = FaceThread()
                self.face_thread.start()

                print("Start")

        elif button == self.close_button:
             if self.face_thread and self.face_thread.isRunning():
                 main.stop_system()
                 self.face_thread.wait()
                 print("Stop")
            
    

app = QApplication(sys.argv)

window = Window()

window.show()

app.exec()