# Vòng lặp chính, kết nối các module lại với nhau

import cv2
import numpy as np
import time
import config
from detector import FaceDetector
from filters import DualOneEuroFilter
from controller import MouseController

def main():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAM_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAM_HEIGHT)

    detector = FaceDetector()
    # Sử dụng bộ lọc One Euro thích ứng cao cấp thay cho Moving Average
    mouse_filter = DualOneEuroFilter(
        freq=config.FILTER_FREQ, 
        min_cutoff=config.FILTER_MIN_CUTOFF, 
        beta=config.FILTER_BETA, 
        d_cutoff=config.FILTER_D_CUTOFF
    )
    mouse_controller = MouseController(cooldown=config.CLICK_COOLDOWN)

    # Biến quản lý trạng thái hiệu ứng UI
    ui_click_flash = 0

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        
        # Lớp overlay phủ mờ để tạo hiệu ứng UI sang trọng hiện đại
        overlay = frame.copy()

        results = detector.process_frame(frame)
        nose_x, nose_y = detector.get_nose_position(results)
        mouth_ratio = detector.get_mouth_open_ratio(results)
        
        if nose_x is not None and nose_y is not None:
            # 1. Khử nhiễu run rẩy thích ứng
            smooth_x, smooth_y = mouse_filter.update(nose_x, nose_y)
            
            # 2. Phát tín hiệu di chuyển chuột
            mouse_controller.move_to(smooth_x, smooth_y)
            
            # Vẽ hồng tâm mục tiêu điều khiển ngay tại mũi (UI tròn bám đuổi)
            center_pt = (int(nose_x * w), int(nose_y * h))
            cv2.circle(frame, center_pt, 8, (0, 255, 127), -1)   # Nhân xanh neon
            cv2.circle(frame, center_pt, 16, (255, 255, 255), 2) # Vòng ngoài trắng

            # 3. Xử lý hành động há miệng để Click
            if mouth_ratio > config.MOUTH_AR_THRESH:
                if mouse_controller.click():
                    ui_click_flash = 5 # Kích hoạt hiệu ứng lóe sáng UI trong 5 khung hình

        # --- PHẦN THIẾT KẾ GIAO DIỆN HỖ TRỢ NGƯỜI DÙNG (HUD UI) ---
        
        # 1. Vẽ khung Deadzone điều khiển (Màu Trắng dịu tinh tế thay vì Đỏ rực)
        x1, y1 = int(config.FRAME_INNER_X1 * w), int(config.FRAME_INNER_Y1 * h)
        x2, y2 = int(config.FRAME_INNER_X2 * w), int(config.FRAME_INNER_Y2 * h)
        cv2.rectangle(overlay, (x1, y1), (x2, y2), (255, 255, 255), 2)
        cv2.putText(frame, "VUNG DIEU KHIEN DAU", (x1 + 5, y1 - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

        # 2. Xây dựng Thanh Progress Bar đo mức độ há miệng bên góc phải màn hình
        bar_x1, bar_y1 = w - 50, h - 250
        bar_x2, bar_y2 = w - 25, h - 50
        
        # Vẽ nền thanh đo bằng màu xám mờ
        cv2.rectangle(overlay, (bar_x1, bar_y1), (bar_x2, bar_y2), (50, 50, 50), -1)
        
        # Tính toán chiều cao mức độ há miệng thực tế so với ngưỡng kích hoạt
        max_expected_ratio = config.MOUTH_AR_THRESH * 2.5
        fill_level = int(np.interp(mouth_ratio, [0, max_expected_ratio], [0, 200]))
        fill_level = max(0, min(200, fill_level)) # Kẹp giá trị an toàn
        
        # Ngưỡng vạch kích hoạt màu Đỏ cam cố định trên thanh đo để người dùng căn chỉnh góc há
        thresh_y = bar_y2 - int(np.interp(config.MOUTH_AR_THRESH, [0, max_expected_ratio], [0, 200]))
        
        # Tô màu thanh đo (Đỏ nếu vượt ngưỡng click, Xanh Neon nếu đang bình thường)
        bar_color = (0, 0, 255) if mouth_ratio > config.MOUTH_AR_THRESH else (0, 255, 127)
        cv2.rectangle(overlay, (bar_x1, bar_y2 - fill_level), (bar_x2, bar_y2), bar_color, -1)
        cv2.line(overlay, (bar_x1 - 5, thresh_y), (bar_x2 + 5, thresh_y), (0, 165, 255), 2)
        cv2.putText(frame, "CLICK", (bar_x1 - 50, thresh_y + 5), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 165, 255), 1, cv2.LINE_AA)
        cv2.putText(frame, "MIENG", (bar_x1 - 15, bar_y1 - 15), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

        # Trộn lớp phủ mờ Overlay vào ảnh gốc để tạo chiều sâu UI
        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)

        # 3. Hiệu ứng Flash toàn màn hình khi có sự kiện CLICK thành công
        if ui_click_flash > 0:
            flash_layer = np.zeros_like(frame)
            flash_layer[:] = (0, 255, 127) # Chớp xanh ngọc bích dịu mắt
            cv2.addWeighted(flash_layer, 0.4, frame, 0.6, 0, frame)
            cv2.putText(frame, "[ CLICKED ]", (w // 2 - 100, 60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 3, cv2.LINE_AA)
            ui_click_flash -= 1

        # Hiển thị thanh HUD trực quan
        cv2.imshow("Head Mouse Accessibility Dashboard", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()